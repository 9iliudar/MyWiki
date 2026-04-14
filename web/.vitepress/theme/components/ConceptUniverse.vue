<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { stripIpaFromTitle } from "../utils/displayTitle";
import graphRaw from "../../../data/graph.json";
import routeRaw from "../../../data/route-map.json";

/* ── Types ── */
interface UniverseNode {
  id: string;
  name: string;
  title: string;
  domain: string;
  importance: number;
  related: string[];
  mastery: string;
  tags: string[];
  route: string;
}

interface Cluster {
  id: string;
  label: string;
}

interface ProjectedNode extends UniverseNode {
  left: number;
  top: number;
  scale: number;
  depth: number;
  z: number;
  opacity: number;
  hudShiftX: string;
  hudShiftY: string;
  entryOffsetX: string;
  entryOffsetY: string;
  entryDepth: string;
  arrivalDelay: string;
  driftDelay: string;
  floatX: string;
  floatY: string;
  floatDuration: string;
}

/* ── Constants ── */
const MAX_VISIBLE_NODES = 18;
const PERSPECTIVE = 940;
const CLOUD_RADIUS = 280;

/* ── Props ── */
const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ (e: "close"): void }>();

/* ── Raw data ── */
const allNodes = ref<UniverseNode[]>([]);
const allEdges = ref<{ source: string; target: string }[]>([]);
const clusters = ref<Cluster[]>([]);
const routeMap = ref<Record<string, string>>({});

/* ── State ── */
const centerId = ref("");
const selectedId = ref<string | null>(null);
const history = ref<string[]>([]);
const query = ref("");
const rotation = ref({ x: -0.24, y: 0.42 });
const warpPhase = ref<"idle" | "warp-lock" | "warp-out" | "warp-in">("idle");
const warpTargetId = ref<string | null>(null);
const warpGhost = ref<ProjectedNode | null>(null);
const warpOrigin = ref({ x: "50%", y: "50%" });
const arrivalOrigin = ref({ x: 0, y: 0, width: 0, height: 0 });
const activeClusterId = ref<string | null>(null);
const isPointerDown = ref(false);
const isDragging = ref(false);
const isSettling = ref(false);

const sceneRef = ref<HTMLDivElement | null>(null);
const dragState = ref<any>(null);
const inertiaFrame = ref(0);
const moveFrame = ref(0);
const warpTimeouts = ref<number[]>([]);
const rotationCache = ref({ x: -0.24, y: 0.42 });
const suppressClickUntil = ref(0);

/* ── Computed ── */
const nodeMap = computed(() => new Map(allNodes.value.map((n) => [n.id, n])));

const centerNode = computed(
  () => nodeMap.value.get(centerId.value) ?? allNodes.value[0]
);
const selectedNode = computed(() =>
  selectedId.value ? nodeMap.value.get(selectedId.value) ?? null : null
);

const activeCluster = computed(
  () => clusters.value.find((c) => c.id === activeClusterId.value) ?? null
);

const activeClusterNodes = computed(() => {
  if (!activeCluster.value) return allNodes.value;
  return allNodes.value.filter(
    (n) => n.domain === activeCluster.value!.label
  );
});
const activeClusterCount = computed(() => activeClusterNodes.value.length);

function scoreNode(node: UniverseNode) {
  return node.importance * 10 + node.related.length;
}

const visibleNodes = computed(() => {
  const center = centerNode.value;
  if (!center) return [];
  // Always show all nodes — dataset is small enough
  const others = allNodes.value.filter((n) => n.id !== center.id);
  return [center, ...others.sort((a, b) => scoreNode(b) - scoreNode(a))].slice(
    0,
    MAX_VISIBLE_NODES
  );
});

const quickLinks = computed(() => {
  if (!selectedNode.value) return [];
  return selectedNode.value.related
    .map((id) => nodeMap.value.get(id))
    .filter(Boolean)
    .sort((a, b) => scoreNode(b!) - scoreNode(a!))
    .slice(0, 8) as UniverseNode[];
});

const searchResults = computed(() => {
  const kw = query.value.trim().toLowerCase();
  if (!kw) return [];
  return allNodes.value
    .filter((n) => {
      const corpus =
        `${n.name} ${n.title} ${n.domain} ${n.tags.join(" ")}`.toLowerCase();
      return corpus.includes(kw);
    })
    .sort((a, b) => scoreNode(b) - scoreNode(a))
    .slice(0, 12);
});

/* ── 3D Math (identical to Ai123) ── */
function clamp(v: number, min: number, max: number) {
  return Math.min(max, Math.max(min, v));
}

function fibonacciSphere(count: number) {
  return Array.from({ length: count }, (_, i) => {
    const offset = 2 / count;
    const y = i * offset - 1 + offset / 2;
    const radius = Math.sqrt(1 - y * y);
    const phi = i * Math.PI * (3 - Math.sqrt(5));
    return { x: Math.cos(phi) * radius, y, z: Math.sin(phi) * radius };
  });
}

function rotatePoint(
  p: { x: number; y: number; z: number },
  rx: number,
  ry: number
) {
  const cx = Math.cos(rx),
    sx = Math.sin(rx);
  const cy = Math.cos(ry),
    sy = Math.sin(ry);
  const y1 = p.y * cx - p.z * sx;
  const z1 = p.y * sx + p.z * cx;
  const x2 = p.x * cy + z1 * sy;
  const z2 = -p.x * sy + z1 * cy;
  return { x: x2, y: y1, z: z2 };
}

function projectPoint(p: { x: number; y: number; z: number }) {
  const depth = (p.z + CLOUD_RADIUS) / (CLOUD_RADIUS * 2);
  const scale = PERSPECTIVE / (PERSPECTIVE - p.z);
  return {
    left: 50 + (p.x / CLOUD_RADIUS) * 28,
    top: 50 + (p.y / CLOUD_RADIUS) * 24,
    scale,
    depth,
    z: p.z,
    opacity: clamp(0.18 + depth * 0.92, 0.16, 1),
  };
}

function getHudAvoidance(
  proj: { left: number; top: number },
  depth: number,
  hasHud: boolean
) {
  if (!hasHud) return { x: 0, y: 0 };
  const threshold = 54;
  const pressure = clamp((proj.left - threshold) / 22, 0, 1);
  if (pressure === 0) return { x: 0, y: 0 };
  const dw = 0.34 + depth * 0.76;
  return {
    x: -(18 + pressure * 64) * dw,
    y: (50 - proj.top) * 0.18 * pressure,
  };
}

const projectedNodes = computed<ProjectedNode[]>(() => {
  const sphere = fibonacciSphere(Math.max(visibleNodes.value.length, 1));
  const hasHud = Boolean(selectedNode.value);
  return visibleNodes.value
    .map((node, i) => {
      const base = sphere[i];
      const r = CLOUD_RADIUS + (node.importance - 3) * 14;
      const rotated = rotatePoint(
        { x: base.x * r, y: base.y * r, z: base.z * r },
        rotation.value.x,
        rotation.value.y
      );
      const proj = projectPoint(rotated);
      const avoid = getHudAvoidance(proj, proj.depth, hasHud);
      const ao = arrivalOrigin.value;
      const fx = ao.width
        ? ((proj.left - 50) / 100) * ao.width + avoid.x
        : 0;
      const fy = ao.height
        ? ((proj.top - 50) / 100) * ao.height + avoid.y
        : 0;
      const ex = ao.width ? ao.x - fx : 0;
      const ey = ao.height ? ao.y - fy : 0;
      const ez = -72 + (1 - proj.depth) * -48;
      return {
        ...node,
        ...proj,
        hudShiftX: `${avoid.x}px`,
        hudShiftY: `${avoid.y}px`,
        entryOffsetX: `${ex}px`,
        entryOffsetY: `${ey}px`,
        entryDepth: `${ez}px`,
        arrivalDelay: `${160 + i * 42}ms`,
        driftDelay: `${(i % 6) * 0.8}s`,
        floatX: `${((i % 5) - 2) * 0.8}px`,
        floatY: `${(((i * 2) % 5) - 2) * 0.7}px`,
        floatDuration: `${11 + (i % 5) * 1.8}s`,
      } as ProjectedNode;
    })
    .sort((a, b) => a.z - b.z);
});

/* ── Mastery display ── */
function masteryLabel(m: string) {
  return m === "deep" ? "deep" : m === "solid" ? "solid" : "surface";
}
function masteryLevel(m: string) {
  return m === "deep" ? 3 : m === "solid" ? 2 : 1;
}

/* ── Drag / Inertia ── */
function stopInertia() {
  cancelAnimationFrame(inertiaFrame.value);
  inertiaFrame.value = 0;
  isSettling.value = false;
}

function startInertia(vel: { x: number; y: number }) {
  stopInertia();
  isSettling.value = true;
  let v = { ...vel };
  const step = () => {
    v = {
      x: Math.abs(v.x) < 0.00004 ? 0 : v.x * 0.93,
      y: Math.abs(v.y) < 0.00004 ? 0 : v.y * 0.93,
    };
    const cur = rotationCache.value;
    const next = {
      x: clamp(cur.x + v.x, -1.04, 1.04),
      y: cur.y + v.y,
    };
    rotationCache.value = next;
    rotation.value = next;
    if (v.x === 0 && v.y === 0) {
      inertiaFrame.value = 0;
      isSettling.value = false;
      return;
    }
    inertiaFrame.value = requestAnimationFrame(step);
  };
  inertiaFrame.value = requestAnimationFrame(step);
}

function scheduleDragRotation() {
  if (!dragState.value || moveFrame.value) return;
  moveFrame.value = requestAnimationFrame(() => {
    moveFrame.value = 0;
    if (!dragState.value) return;
    const d = dragState.value;
    const dx = d.currentX - d.startX;
    const dy = d.currentY - d.startY;
    const next = {
      x: clamp(d.originX + dy * 0.0041, -1.04, 1.04),
      y: d.originY + dx * 0.0049,
    };
    rotationCache.value = next;
    rotation.value = next;
  });
}

function handlePointerDown(e: PointerEvent) {
  if (
    (e.target as HTMLElement).closest(
      ".universe-node, .universe-hud, .universe-controls, .universe-search-panel, .universe-topbar, .universe-filter-row, .universe-category-panel, input"
    )
  )
    return;
  stopInertia();
  isPointerDown.value = true;
  isDragging.value = false;
  dragState.value = {
    pointerId: e.pointerId,
    startX: e.clientX,
    startY: e.clientY,
    currentX: e.clientX,
    currentY: e.clientY,
    originX: rotationCache.value.x,
    originY: rotationCache.value.y,
    lastX: e.clientX,
    lastY: e.clientY,
    lastTime: performance.now(),
    velocityX: 0,
    velocityY: 0,
    moved: false,
  };
  sceneRef.value?.setPointerCapture(e.pointerId);
}

function handlePointerMove(e: PointerEvent) {
  if (!dragState.value) return;
  const d = dragState.value;
  d.currentX = e.clientX;
  d.currentY = e.clientY;
  const now = performance.now();
  const elapsed = Math.max(now - d.lastTime, 16);
  const dx = e.clientX - d.startX;
  const dy = e.clientY - d.startY;
  if (Math.abs(dx) > 4 || Math.abs(dy) > 4) {
    d.moved = true;
    isDragging.value = true;
  }
  d.velocityX = ((e.clientY - d.lastY) * 0.0041) / elapsed;
  d.velocityY = ((e.clientX - d.lastX) * 0.0049) / elapsed;
  d.lastX = e.clientX;
  d.lastY = e.clientY;
  d.lastTime = now;
  scheduleDragRotation();
}

function handlePointerUp(e: PointerEvent) {
  if (!dragState.value) return;
  cancelAnimationFrame(moveFrame.value);
  moveFrame.value = 0;
  sceneRef.value?.releasePointerCapture(e.pointerId);
  isPointerDown.value = false;
  if (dragState.value.moved) {
    suppressClickUntil.value = performance.now() + 220;
    startInertia({
      x: clamp(dragState.value.velocityX * 10, -0.008, 0.008),
      y: clamp(dragState.value.velocityY * 10, -0.01, 0.01),
    });
  } else {
    isSettling.value = false;
  }
  isDragging.value = false;
  dragState.value = null;
}

/* ── Navigation ── */
function enterNode(targetId: string) {
  if (!nodeMap.value.has(targetId) || targetId === centerId.value) {
    selectedId.value = targetId;
    return;
  }
  const targetNode = nodeMap.value.get(targetId)!;
  const targetCluster = clusters.value.find(
    (c) => c.label === targetNode.domain
  );
  if (targetCluster && targetCluster.id !== activeClusterId.value) {
    activeClusterId.value = targetCluster.id;
  }

  warpTimeouts.value.forEach((t) => clearTimeout(t));
  warpTimeouts.value = [];
  const ghost = projectedNodes.value.find((n) => n.id === targetId);
  if (ghost) {
    warpGhost.value = ghost;
    warpOrigin.value = {
      x: `calc(${ghost.left}% + ${ghost.hudShiftX})`,
      y: `calc(${ghost.top}% + ${ghost.hudShiftY})`,
    };
    if (sceneRef.value) {
      const rect = sceneRef.value.getBoundingClientRect();
      arrivalOrigin.value = {
        x:
          ((ghost.left - 50) / 100) * rect.width +
          parseFloat(ghost.hudShiftX),
        y:
          ((ghost.top - 50) / 100) * rect.height +
          parseFloat(ghost.hudShiftY),
        width: rect.width,
        height: rect.height,
      };
    }
  }
  warpTargetId.value = targetId;
  selectedId.value = targetId;
  warpPhase.value = "warp-lock";
  stopInertia();

  warpTimeouts.value.push(
    window.setTimeout(() => {
      warpPhase.value = "warp-out";
    }, 280)
  );
  warpTimeouts.value.push(
    window.setTimeout(() => {
      centerId.value = targetId;
      selectedId.value = targetId;
      history.value = [...history.value, targetId].slice(-12);
      rotation.value = {
        x: -0.24 + Math.sin(performance.now() * 0.001) * 0.06,
        y: 0.42,
      };
      rotationCache.value = rotation.value;
      warpPhase.value = "warp-in";
      warpTimeouts.value.push(
        window.setTimeout(() => {
          warpPhase.value = "idle";
          warpTargetId.value = null;
          warpGhost.value = null;
          warpOrigin.value = { x: "50%", y: "50%" };
          arrivalOrigin.value = { x: 0, y: 0, width: 0, height: 0 };
          warpTimeouts.value = [];
        }, 520)
      );
    }, 560)
  );
}

function handleBack() {
  if (history.value.length <= 1) {
    centerId.value = allNodes.value[0]?.id ?? "";
    selectedId.value = null;
    history.value = [centerId.value];
    stopInertia();
    return;
  }
  const next = history.value.slice(0, -1);
  const prevId = next[next.length - 1];
  history.value = next;
  centerId.value = prevId;
  selectedId.value = null;
  rotation.value = { x: -0.24, y: 0.42 };
  rotationCache.value = rotation.value;
  stopInertia();
}

function handleNodeClick(nodeId: string) {
  if (performance.now() < suppressClickUntil.value) return;
  selectedId.value = nodeId;
}

function navigateToPage(node: UniverseNode) {
  if (node.route) {
    window.location.href = node.route;
  }
}

/* ── Scene class ── */
const sceneClass = computed(() =>
  [
    "universe-scene",
    isPointerDown.value ? "is-pointer-down" : "",
    isDragging.value ? "is-dragging" : "",
    !isDragging.value && !isSettling.value && warpPhase.value === "idle"
      ? "is-idle"
      : "",
  ]
    .filter(Boolean)
    .join(" ")
);

/* ── Data loading ── */
onMounted(async () => {
  const graphData = graphRaw as { nodes: any[]; edges: any[] };
  const routeData = routeRaw as { routeByName: Record<string, string> };

  routeMap.value = routeData.routeByName || {};

  // Build adjacency
  const adj: Record<string, Set<string>> = {};
  for (const e of graphData.edges) {
    if (!adj[e.source]) adj[e.source] = new Set();
    if (!adj[e.target]) adj[e.target] = new Set();
    adj[e.source].add(e.target);
    adj[e.target].add(e.source);
  }

  // Convert nodes
  allNodes.value = graphData.nodes.map((n: any) => ({
    id: n.id,
    name: stripIpaFromTitle(n.title),
    title: n.title,
    domain: n.category || "General",
    importance: Math.min(5, 2 + (adj[n.id]?.size ?? 0)),
    related: [...(adj[n.id] ?? [])],
    mastery: n.mastery || "solid",
    tags: n.tags || [],
    route: routeMap.value[n.id] || `/pages/${n.id}.html`,
  }));

  allEdges.value = graphData.edges;

  // Build clusters from categories
  const cats = [...new Set(allNodes.value.map((n) => n.domain))].sort();
  clusters.value = cats.map((c) => ({ id: c, label: c }));
  activeClusterId.value = clusters.value[0]?.id ?? null;

  // Set initial center to highest-connected node
  const sorted = [...allNodes.value].sort(
    (a, b) => scoreNode(b) - scoreNode(a)
  );
  centerId.value = sorted[0]?.id ?? "";
  history.value = [centerId.value];
});

/* ── Keyboard ── */
function handleKeyDown(e: KeyboardEvent) {
  if (e.key === "Escape") emit("close");
}
onMounted(() => window.addEventListener("keydown", handleKeyDown));
onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown);
  cancelAnimationFrame(inertiaFrame.value);
  cancelAnimationFrame(moveFrame.value);
  warpTimeouts.value.forEach((t) => clearTimeout(t));
});

/* ── Cluster switch — recenter on first node of selected category ── */
watch(activeClusterId, () => {
  if (!activeCluster.value) return;
  const next = activeClusterNodes.value.sort(
    (a, b) => scoreNode(b) - scoreNode(a)
  )[0];
  if (!next) return;
  centerId.value = next.id;
  selectedId.value = null;
  history.value = [next.id];
  rotation.value = { x: -0.24, y: 0.42 };
  rotationCache.value = rotation.value;
});
</script>

<template>
  <div
    v-if="open"
    class="universe-container"
    :class="warpPhase"
  >
      <!-- Scene -->
      <div
        ref="sceneRef"
        :class="sceneClass"
        :style="{
          '--warp-origin-x': warpOrigin.x,
          '--warp-origin-y': warpOrigin.y,
        }"
        @click="(e: MouseEvent) => {
          if ((e.target as HTMLElement) === (e.currentTarget as HTMLElement) || (e.target as HTMLElement).classList.contains('universe-backdrop')) {
            selectedId = null;
          }
        }"
        @pointerdown="handlePointerDown"
        @pointermove="handlePointerMove"
        @pointerup="handlePointerUp"
        @pointercancel="handlePointerUp"
        @pointerleave="handlePointerUp"
        @lostpointercapture="handlePointerUp"
      >
        <div class="universe-backdrop" />
        <div class="universe-warp-veil" aria-hidden="true" />
        <div class="universe-warp-lines" aria-hidden="true" />

        <!-- Warp ghost -->
        <div
          v-if="warpGhost"
          class="universe-warp-ghost"
          aria-hidden="true"
          :style="{
            left: `${warpGhost.left}%`,
            top: `${warpGhost.top}%`,
            '--ghost-shift-x': warpGhost.hudShiftX,
            '--ghost-shift-y': warpGhost.hudShiftY,
            '--ghost-scale': warpGhost.scale,
          }"
        >
          <span>{{ warpGhost.name }}</span>
          <small>{{ warpGhost.domain }}</small>
        </div>

        <!-- Core glow -->
        <div class="universe-core" aria-hidden="true" />

        <!-- Nodes -->
        <div class="universe-field">
          <button
            v-for="node in projectedNodes"
            :key="node.id"
            type="button"
            :class="[
              'universe-node',
              selectedId === node.id ? 'active' : '',
              warpTargetId === node.id ? 'is-warp-target' : '',
              node.z < -30 ? 'is-distant' : '',
            ]"
            :style="{
              left: `${node.left}%`,
              top: `${node.top}%`,
              transform: `translate(-50%, -50%) translate3d(var(--node-shift-x), var(--node-shift-y), 0) scale(var(--node-scale))`,
              opacity: node.opacity,
              zIndex: Math.round(node.depth * 100) + 10,
              '--node-shift-x': node.hudShiftX,
              '--node-shift-y': node.hudShiftY,
              '--node-entry-x': node.entryOffsetX,
              '--node-entry-y': node.entryOffsetY,
              '--node-entry-z': node.entryDepth,
              '--node-scale': node.scale,
              '--node-arrival-delay': node.arrivalDelay,
              '--node-drift-delay': node.driftDelay,
              '--node-float-x': node.floatX,
              '--node-float-y': node.floatY,
              '--node-float-duration': node.floatDuration,
            }"
            @pointerdown.stop
            @pointerup.stop
            @click.stop="handleNodeClick(node.id)"
            @dblclick.stop="enterNode(node.id)"
          >
            <span class="universe-node-content">
              <span>{{ node.name }}</span>
              <small>{{ node.domain }}</small>
            </span>
          </button>
        </div>

        <!-- Stats -->
        <div class="universe-stats">
          <span>Total: {{ allNodes.length }}</span>
          <span>Center: {{ centerNode?.name }}</span>
        </div>

        <!-- Category filter -->
        <div
          class="universe-category-panel"
          @click.stop
          @pointerdown.stop
        >
          <div class="universe-category-chips">
            <button
              v-for="cluster in clusters"
              :key="cluster.id"
              type="button"
              :class="[
                'universe-cat-chip',
                cluster.id === activeClusterId ? 'active' : '',
              ]"
              @click="activeClusterId = cluster.id"
            >
              {{ cluster.label }}
            </button>
          </div>
        </div>

        <!-- HUD -->
        <aside v-if="selectedNode" class="universe-hud">
          <div class="universe-hud-top">
            <p class="universe-hud-label">Selected concept</p>
          </div>
          <h3>{{ selectedNode.name }}</h3>
          <div class="universe-hud-meta">
            <span class="universe-hud-domain">{{ selectedNode.domain }}</span>
            <span class="universe-hud-mastery" :class="'mastery-' + selectedNode.mastery">
              {{ masteryLabel(selectedNode.mastery) }}
            </span>
          </div>
          <div class="universe-hud-tags">
            <span v-for="tag in selectedNode.tags.slice(0, 5)" :key="tag" class="universe-tag">
              {{ tag }}
            </span>
          </div>
          <div class="universe-importance" :aria-label="`Importance ${selectedNode.importance}/5`">
            <span v-for="i in 5" :key="i" :class="i <= selectedNode.importance ? 'filled' : ''">●</span>
          </div>
          <button class="universe-hud-open" @click="navigateToPage(selectedNode)">
            Open page →
          </button>
          <div v-if="quickLinks.length" class="universe-quick-links">
            <button
              v-for="node in quickLinks"
              :key="node.id"
              type="button"
              @click="enterNode(node.id)"
            >
              {{ node.name }}
            </button>
          </div>
        </aside>
      </div>
  </div>
</template>

<style scoped>
/* ── Variables (VitePress native) ── */
.universe-container {
  --uni-brand: var(--vp-c-brand-1, #8b5cf6);
  --uni-brand-soft: var(--vp-c-bg-soft);
  --uni-brand-strong: var(--vp-c-brand-soft, rgba(139, 92, 246, 0.14));
  --uni-bg: var(--vp-c-bg);
  --uni-bg-card: var(--vp-c-bg-soft);
  --uni-text-1: var(--vp-c-text-1);
  --uni-text-2: var(--vp-c-text-2);
  --uni-text-3: var(--vp-c-text-3);
  --uni-border: var(--vp-c-divider);
  --uni-radius: 10px;
}

/* ── Container (inline, not overlay) ── */
.universe-container {
  position: fixed;
  top: var(--vp-nav-height, 64px);
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--uni-bg);
  overflow: hidden;
  z-index: 1;
}

/* ── Scene ── */
.universe-scene {
  position: absolute;
  inset: 0;
  overflow: hidden;
  cursor: grab;
  perspective: 940px;
  touch-action: none;
  user-select: none;
}

.universe-scene.is-pointer-down,
.universe-scene.is-dragging {
  cursor: grabbing;
}

/* ── Backdrop ── */
.universe-backdrop {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* ── Core (subtle center indicator) ── */
.universe-core {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120px;
  height: 120px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid var(--uni-border);
  opacity: 0.3;
  pointer-events: none;
}

/* ── Warp effects ── */
.universe-warp-veil {
  position: absolute;
  inset: 0;
  background: var(--uni-bg);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s;
}

.warp-lock .universe-warp-veil { opacity: 0.2; }
.warp-out .universe-warp-veil { opacity: 0.5; }
.warp-in .universe-warp-veil { opacity: 0; }

.universe-warp-lines {
  display: none;
}

.universe-warp-ghost {
  position: absolute;
  transform: translate(-50%, -50%) translate3d(var(--ghost-shift-x, 0), var(--ghost-shift-y, 0), 0) scale(var(--ghost-scale, 1));
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
  z-index: 50;
}

.universe-warp-ghost span {
  color: var(--uni-text-1);
  font-weight: 700;
  font-size: 0.95rem;
}

.universe-warp-ghost small {
  color: var(--uni-text-3);
  font-size: 0.7rem;
}

.warp-lock .universe-warp-ghost {
  animation: ghost-lock 0.3s ease-out forwards;
}

.warp-out .universe-warp-ghost {
  animation: ghost-zoom 0.5s ease-in forwards;
}

@keyframes ghost-lock {
  to { transform: translate(-50%, -50%) translate3d(var(--ghost-shift-x, 0), var(--ghost-shift-y, 0), 0) scale(calc(var(--ghost-scale, 1) * 1.2)); }
}

@keyframes ghost-zoom {
  to { transform: translate(-50%, -50%) scale(3); opacity: 0; }
}

/* ── Node field ── */
.universe-field {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.universe-node {
  position: absolute;
  pointer-events: auto;
  border: 1px solid var(--uni-border);
  background: var(--uni-brand-soft);
  border-radius: 20px;
  padding: 0.35rem 0.75rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  font-family: inherit;
  white-space: nowrap;
}

.universe-scene.is-idle .universe-node {
  animation: node-float var(--node-float-duration, 12s) ease-in-out infinite;
  animation-delay: var(--node-drift-delay, 0s);
}

.warp-in .universe-node {
  animation: node-arrive 0.5s cubic-bezier(0.22, 1, 0.36, 1) backwards;
  animation-delay: var(--node-arrival-delay, 0ms);
}

@keyframes node-float {
  0%, 100% { translate: 0 0; }
  33% { translate: var(--node-float-x, 0) var(--node-float-y, 0); }
  66% { translate: calc(var(--node-float-x, 0) * -0.7) calc(var(--node-float-y, 0) * -0.5); }
}

@keyframes node-arrive {
  from {
    translate: var(--node-entry-x, 0) var(--node-entry-y, 0);
    opacity: 0;
    scale: 0.3;
  }
}

.universe-node:hover {
  background: var(--uni-brand-soft);
  border-color: var(--uni-text-3);
}

.universe-node.active {
  background: var(--uni-brand-soft);
  border-color: var(--uni-brand);
}

.universe-node.is-distant {
  filter: blur(0.5px);
}

.universe-node.is-warp-target {
  opacity: 0 !important;
}

.universe-node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.universe-node-content span {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--uni-text-1);
}

.universe-node-content small {
  font-size: 0.65rem;
  color: var(--uni-text-3);
}

/* ── Stats ── */
.universe-stats {
  position: absolute;
  bottom: 0.8rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 1.2rem;
  font-size: 0.72rem;
  color: var(--uni-text-3);
  pointer-events: none;
}

/* ── Category filter ── */
.universe-category-panel {
  position: absolute;
  bottom: 2.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 15;
}

.universe-category-chips {
  display: flex;
  gap: 0.35rem;
  padding: 0.3rem;
  background: var(--uni-bg-card);
  border: 1px solid var(--uni-border);
  border-radius: 999px;
}

.universe-cat-chip {
  padding: 0.3rem 0.7rem;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--uni-text-2);
  font-size: 0.78rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, color 0.15s;
}

.universe-cat-chip:hover {
  background: var(--uni-brand-soft);
  color: var(--uni-text-1);
}

.universe-cat-chip.active {
  background: var(--uni-brand);
  color: #fff;
}

/* ── HUD ── */
.universe-hud {
  position: absolute;
  top: 6rem;
  right: 1.2rem;
  width: 260px;
  max-height: calc(100% - 2.4rem);
  overflow-y: auto;
  background: var(--uni-bg-card);
  border: 1px solid var(--uni-border);
  border-radius: var(--uni-radius);
  padding: 1rem 1.1rem;
  z-index: 15;
  scrollbar-width: none;
}

.universe-hud::-webkit-scrollbar { display: none; }

.universe-hud-top {
  margin-bottom: 0.4rem;
}

.universe-hud-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--uni-text-3);
  margin: 0;
}

.universe-hud h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--uni-text-1);
  margin: 0 0 0.5rem;
  line-height: 1.3;
}

.universe-hud-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.universe-hud-domain {
  font-size: 0.75rem;
  color: var(--uni-text-2);
  font-weight: 500;
}

.universe-hud-mastery {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-weight: 500;
}

.mastery-deep {
  background: rgba(34, 197, 94, 0.1);
  color: var(--vp-c-green-1, #22c55e);
}

.mastery-solid {
  background: rgba(59, 130, 246, 0.1);
  color: var(--vp-c-blue-1, #3b82f6);
}

.mastery-surface {
  background: rgba(234, 179, 8, 0.1);
  color: var(--vp-c-yellow-1, #eab308);
}

.universe-hud-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-bottom: 0.6rem;
}

.universe-tag {
  font-size: 0.68rem;
  padding: 0.12rem 0.4rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--uni-text-2);
  border: 1px solid var(--uni-border);
}

.universe-importance {
  display: flex;
  gap: 3px;
  margin-bottom: 0.7rem;
  font-size: 0.6rem;
  color: var(--uni-text-3);
}

.universe-importance .filled {
  color: var(--uni-brand);
}

.universe-hud-open {
  display: block;
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--uni-border);
  border-radius: 8px;
  background: var(--uni-bg);
  color: var(--uni-text-1);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  text-align: center;
  margin-bottom: 0.7rem;
  font-family: inherit;
  transition: border-color 0.15s;
}

.universe-hud-open:hover {
  border-color: var(--uni-text-3);
}

.universe-quick-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.universe-quick-links button {
  padding: 0.25rem 0.55rem;
  border: 1px solid var(--uni-border);
  border-radius: 6px;
  background: transparent;
  color: var(--uni-text-2);
  font-size: 0.72rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, color 0.15s;
}

.universe-quick-links button:hover {
  background: var(--uni-brand-soft);
  color: var(--uni-text-1);
}

/* ── Responsive ── */
@media (max-width: 640px) {
  .universe-hud {
    position: fixed;
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-height: 45vh;
    border-radius: var(--uni-radius) var(--uni-radius) 0 0;
  }
}
</style>
