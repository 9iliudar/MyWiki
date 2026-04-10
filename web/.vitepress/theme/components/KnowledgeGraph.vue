<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import * as d3 from "d3";
import routeMap from "../../../data/route-map.json";
import { stripIpaFromTitle } from "../utils/displayTitle";

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

  // Defs for glow filter
  const defs = svg.append("defs");
  const filter = defs.append("filter").attr("id", "node-glow");
  filter
    .append("feGaussianBlur")
    .attr("stdDeviation", "3")
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

  simulation = d3
    .forceSimulation<GraphNode>(graphData.nodes)
    .force(
      "link",
      d3
        .forceLink<GraphNode, GraphEdge>(graphData.edges)
        .id((d) => d.id)
        .distance(180)
    )
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width / 2, height / 2).strength(0.05))
    .force("x", d3.forceX(width / 2).strength(0.02))
    .force("y", d3.forceY(height / 2).strength(0.02));

  // Root group for pan/zoom
  const rootGroup = svg.append("g");

  svg.call(
    d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 4])
      .on("zoom", (event) => {
        rootGroup.attr("transform", event.transform);
      })
  );

  const linkGroup = rootGroup.append("g");
  const link = linkGroup
    .selectAll("line")
    .data(graphData.edges)
    .join("line")
    .attr("stroke", "rgba(139, 92, 246, 0.3)")
    .attr("stroke-width", 1);

  const nodeGroup = rootGroup.append("g");
  const node = nodeGroup
    .selectAll("circle")
    .data(graphData.nodes)
    .join("circle")
    .attr("r", (d) => 3 + (connectionCount[d.id] || 0) * 0.8)
    .attr("fill", (d) =>
      (connectionCount[d.id] || 0) > 0 ? "#8b5cf6" : "var(--vp-c-text-3)"
    )
    .attr("filter", "url(#node-glow)")
    .attr("cursor", "pointer")
    .on("click", (_, d) => {
      window.location.href = routeForNode(d);
    })
    .on("mouseenter", (_, d) => {
      // Highlight connected edges
      link
        .attr("stroke", (l: any) => {
          const srcId =
            typeof l.source === "string" ? l.source : l.source.id;
          const tgtId =
            typeof l.target === "string" ? l.target : l.target.id;
          if (srcId === d.id || tgtId === d.id) return "#8b5cf6";
          return "rgba(139, 92, 246, 0.3)";
        })
;
      // Highlight connected nodes
      node.attr("opacity", (n) => {
        if (n.id === d.id) return 1;
        if (adjacency.has(`${d.id}--${n.id}`)) return 1;
        return 0.3;
      });
      label.attr("opacity", (n) => {
        if (n.id === d.id) return 1;
        if (adjacency.has(`${d.id}--${n.id}`)) return 1;
        return 0.15;
      });
    })
    .on("mouseleave", () => {
      link.attr("stroke", "rgba(139, 92, 246, 0.3)");
      node.attr("opacity", 1);
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
    .text((d) => stripIpaFromTitle(d.title))
    .attr("font-size", "13px")
    .attr("font-family", "system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif")
    .attr("dx", 10)
    .attr("dy", 4)
    .attr("fill", "var(--vp-c-text-1)")
    .attr("pointer-events", "none");

  simulation.on("tick", () => {
    link
      .attr("x1", (d: any) => d.source.x)
      .attr("y1", (d: any) => d.source.y)
      .attr("x2", (d: any) => d.target.x)
      .attr("y2", (d: any) => d.target.y);
    node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
    label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
  });

  // Handle resize
  resizeObserver = new ResizeObserver(() => {
    if (!container.value) return;
    const w = container.value.clientWidth;
    const h = container.value.clientHeight;
    svg.attr("viewBox", [0, 0, w, h]);
    simulation
      ?.force("center", d3.forceCenter(w / 2, h / 2).strength(0.15))
      .force("x", d3.forceX(w / 2).strength(0.05))
      .force("y", d3.forceY(h / 2).strength(0.05));
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
