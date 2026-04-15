<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import * as d3 from "d3";
import routeMap from "../../../data/route-map.json";
import { cleanDisplayName } from "../utils/displayTitle";

interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  title: string;
  tags: string[];
}

interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
}

const container = ref<HTMLDivElement | null>(null);
let simulation: d3.Simulation<GraphNode, GraphEdge> | null = null;
let resizeObserver: ResizeObserver | null = null;

function routeForNode(node: GraphNode) {
  return (
    (routeMap as any).routeByName?.[node.id] ||
    (routeMap as any).routeByTitle?.[node.title] ||
    `/pages/${node.id}.html`
  );
}

onMounted(async () => {
  if (!container.value) return;

  let graphData: { nodes: GraphNode[]; edges: GraphEdge[] };
  try {
    const data = await import("../../../data/graph.json");
    graphData = data.default || data;
  } catch {
    return;
  }

  const width = container.value.clientWidth;
  const height = container.value.clientHeight;

  const svg = d3
    .select(container.value)
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", [0, 0, width, height]);

  // Defs for subtle glow filter
  const defs = svg.append("defs");
  const filter = defs.append("filter").attr("id", "node-glow");
  filter
    .append("feGaussianBlur")
    .attr("stdDeviation", "1.5")
    .attr("result", "coloredBlur");
  const feMerge = filter.append("feMerge");
  feMerge.append("feMergeNode").attr("in", "coloredBlur");
  feMerge.append("feMergeNode").attr("in", "SourceGraphic");

  const connectionCount: Record<string, number> = {};
  graphData.nodes.forEach((n) => (connectionCount[n.id] = 0));
  graphData.edges.forEach((e) => {
    const src = typeof e.source === "string" ? e.source : e.source.id;
    const tgt = typeof e.target === "string" ? e.target : e.target.id;
    connectionCount[src] = (connectionCount[src] || 0) + 1;
    connectionCount[tgt] = (connectionCount[tgt] || 0) + 1;
  });

  // Build adjacency set for hover highlighting
  const adjacency = new Set<string>();
  graphData.edges.forEach((e) => {
    const src = typeof e.source === "string" ? e.source : e.source.id;
    const tgt = typeof e.target === "string" ? e.target : e.target.id;
    adjacency.add(`${src}--${tgt}`);
    adjacency.add(`${tgt}--${src}`);
  });

  // Constellation layout: compute per-category cluster centers on an ellipse
  const categories = [...new Set(graphData.nodes.map((n: any) => n.category || n.tags?.[0] || "General"))];
  const clusterRadius = Math.min(width, height) * 0.22;
  const clusterCenters: Record<string, { x: number; y: number }> = {};
  categories.forEach((cat, i) => {
    const angle = (i * 2 * Math.PI) / categories.length - Math.PI / 2;
    clusterCenters[cat] = {
      x: width / 2 + Math.cos(angle) * clusterRadius,
      y: height / 2 + Math.sin(angle) * clusterRadius,
    };
  });

  // Assign category to each node for cluster force
  const nodeCategory: Record<string, string> = {};
  graphData.nodes.forEach((n: any) => {
    nodeCategory[n.id] = n.category || n.tags?.[0] || "General";
  });

  simulation = d3
    .forceSimulation<GraphNode>(graphData.nodes)
    .force(
      "link",
      d3
        .forceLink<GraphNode, GraphEdge>(graphData.edges)
        .id((d) => d.id)
        .distance(200)
    )
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2).strength(0.03))
    // Cluster force: pull nodes toward their category center
    .force("clusterX", d3.forceX<GraphNode>((d) => clusterCenters[nodeCategory[d.id]]?.x ?? width / 2).strength(0.12))
    .force("clusterY", d3.forceY<GraphNode>((d) => clusterCenters[nodeCategory[d.id]]?.y ?? height / 2).strength(0.12))
    // Boundary force: soft wall to keep nodes in viewport
    .force("boundX", d3.forceX(width / 2).strength(0.015))
    .force("boundY", d3.forceY(height / 2).strength(0.015));

  // Root group for pan/zoom
  const rootGroup = svg.append("g");

  const linkColor = "rgba(128, 128, 128, 0.15)";
  const linkHighlight = "var(--vp-c-text-3)";
  const nodeColor = "var(--vp-c-text-3)";
  const nodeHighlight = "var(--vp-c-text-2)";

  const linkGroup = rootGroup.append("g");
  const link = linkGroup
    .selectAll("line")
    .data(graphData.edges)
    .join("line")
    .attr("stroke", linkColor)
    .attr("stroke-width", 0.8);

  const nodeGroup = rootGroup.append("g");
  const node = nodeGroup
    .selectAll("circle")
    .data(graphData.nodes)
    .join("circle")
    .attr("r", (d) => 3 + (connectionCount[d.id] || 0) * 0.7)
    .attr("fill", nodeColor)
    .attr("filter", "url(#node-glow)")
    .attr("cursor", "pointer")
    .on("click", (_, d) => {
      window.location.href = routeForNode(d);
    })
    .on("mouseenter", (_, d) => {
      link
        .attr("stroke", (l: any) => {
          const srcId =
            typeof l.source === "string" ? l.source : l.source.id;
          const tgtId =
            typeof l.target === "string" ? l.target : l.target.id;
          if (srcId === d.id || tgtId === d.id) return linkHighlight;
          return linkColor;
        })
        .attr("stroke-width", (l: any) => {
          const srcId =
            typeof l.source === "string" ? l.source : l.source.id;
          const tgtId =
            typeof l.target === "string" ? l.target : l.target.id;
          if (srcId === d.id || tgtId === d.id) return 1.5;
          return 0.8;
        });
      node.attr("opacity", (n) => {
        if (n.id === d.id) return 1;
        if (adjacency.has(`${d.id}--${n.id}`)) return 1;
        return 0.25;
      });
      node.attr("fill", (n) => {
        if (n.id === d.id || adjacency.has(`${d.id}--${n.id}`)) return nodeHighlight;
        return nodeColor;
      });
      label.attr("opacity", (n) => {
        if (n.id === d.id) return 1;
        if (adjacency.has(`${d.id}--${n.id}`)) return 1;
        return 0.12;
      });
    })
    .on("mouseleave", () => {
      link.attr("stroke", linkColor).attr("stroke-width", 0.8);
      node.attr("opacity", 1).attr("fill", nodeColor);
      label.attr("opacity", 1);
    })
    .call(
      d3
        .drag<SVGCircleElement, GraphNode>()
        .on("start", (event, d) => {
          if (!event.active) simulation!.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation!.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );

  const labelGroup = rootGroup.append("g");
  const label = labelGroup
    .selectAll("text")
    .data(graphData.nodes)
    .join("text")
    .text((d) => cleanDisplayName(d.title))
    .attr("font-size", "12px")
    .attr("font-family", "system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif")
    .attr("dx", 10)
    .attr("dy", 4)
    .attr("fill", "var(--vp-c-text-2)")
    .attr("pointer-events", "none");

  // Auto-fit: after simulation cools, zoom to fit all nodes with padding
  let hasFitted = false;
  const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.3, 4])
    .on("zoom", (event) => {
      rootGroup.attr("transform", event.transform);
    });

  function fitToView() {
    const pad = 60;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    graphData.nodes.forEach((n: any) => {
      if (n.x < minX) minX = n.x;
      if (n.y < minY) minY = n.y;
      if (n.x > maxX) maxX = n.x;
      if (n.y > maxY) maxY = n.y;
    });
    const bw = maxX - minX + pad * 2;
    const bh = maxY - minY + pad * 2;
    const scale = Math.min(width / bw, height / bh, 1.5);
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const tx = width / 2 - cx * scale;
    const ty = height / 2 - cy * scale;
    svg.transition().duration(600).call(
      zoomBehavior.transform,
      d3.zoomIdentity.translate(tx, ty).scale(scale)
    );
  }

  svg.call(zoomBehavior);

  simulation.on("tick", () => {
    link
      .attr("x1", (d: any) => d.source.x)
      .attr("y1", (d: any) => d.source.y)
      .attr("x2", (d: any) => d.target.x)
      .attr("y2", (d: any) => d.target.y);
    node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
    label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);

    // Auto-fit once when simulation nearly settled
    if (!hasFitted && simulation!.alpha() < 0.05) {
      hasFitted = true;
      fitToView();
    }
  });

  // Handle resize
  resizeObserver = new ResizeObserver(() => {
    if (!container.value) return;
    const w = container.value.clientWidth;
    const h = container.value.clientHeight;
    svg.attr("viewBox", [0, 0, w, h]);
    // Recompute cluster centers for new dimensions
    const newRadius = Math.min(w, h) * 0.22;
    categories.forEach((cat, i) => {
      const angle = (i * 2 * Math.PI) / categories.length - Math.PI / 2;
      clusterCenters[cat] = {
        x: w / 2 + Math.cos(angle) * newRadius,
        y: h / 2 + Math.sin(angle) * newRadius,
      };
    });
    simulation
      ?.force("center", d3.forceCenter(w / 2, h / 2).strength(0.03))
      .force("clusterX", d3.forceX<GraphNode>((d) => clusterCenters[nodeCategory[d.id]]?.x ?? w / 2).strength(0.12))
      .force("clusterY", d3.forceY<GraphNode>((d) => clusterCenters[nodeCategory[d.id]]?.y ?? h / 2).strength(0.12))
      .force("boundX", d3.forceX(w / 2).strength(0.015))
      .force("boundY", d3.forceY(h / 2).strength(0.015));
    hasFitted = false;
    simulation?.alpha(0.3).restart();
  });
  resizeObserver.observe(container.value);
});

onUnmounted(() => {
  simulation?.stop();
  resizeObserver?.disconnect();
});
</script>

<template>
  <div ref="container" class="graph-canvas"></div>
</template>

<style scoped>
.graph-canvas {
  position: fixed;
  top: var(--vp-nav-height, 64px);
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: calc(100vh - var(--vp-nav-height, 64px));
  background: var(--vp-c-bg);
  overflow: hidden;
  z-index: 1;
}
</style>
