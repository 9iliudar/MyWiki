<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import * as d3 from "d3";

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
  const height = 500;

  const svg = d3
    .select(container.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height]);

  const connectionCount: Record<string, number> = {};
  graphData.nodes.forEach((n) => (connectionCount[n.id] = 0));
  graphData.edges.forEach((e) => {
    const src = typeof e.source === "string" ? e.source : e.source.id;
    const tgt = typeof e.target === "string" ? e.target : e.target.id;
    connectionCount[src] = (connectionCount[src] || 0) + 1;
    connectionCount[tgt] = (connectionCount[tgt] || 0) + 1;
  });

  simulation = d3
    .forceSimulation<GraphNode>(graphData.nodes)
    .force(
      "link",
      d3.forceLink<GraphNode, GraphEdge>(graphData.edges).id((d) => d.id).distance(80)
    )
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2));

  const link = svg
    .append("g")
    .selectAll("line")
    .data(graphData.edges)
    .join("line")
    .attr("stroke", "var(--vp-c-divider)")
    .attr("stroke-width", 1);

  const node = svg
    .append("g")
    .selectAll("circle")
    .data(graphData.nodes)
    .join("circle")
    .attr("r", (d) => 5 + (connectionCount[d.id] || 0) * 2)
    .attr("fill", "var(--vp-c-text-2)")
    .attr("cursor", "pointer")
    .on("click", (_, d) => {
      window.location.href = `/pages/${d.id}.html`;
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

  const label = svg
    .append("g")
    .selectAll("text")
    .data(graphData.nodes)
    .join("text")
    .text((d) => d.title)
    .attr("font-size", "11px")
    .attr("font-family", "system-ui, sans-serif")
    .attr("dx", 10)
    .attr("dy", 4)
    .attr("fill", "var(--vp-c-text-1)");

  simulation.on("tick", () => {
    link
      .attr("x1", (d: any) => d.source.x)
      .attr("y1", (d: any) => d.source.y)
      .attr("x2", (d: any) => d.target.x)
      .attr("y2", (d: any) => d.target.y);
    node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
    label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
  });
});

onUnmounted(() => {
  simulation?.stop();
});
</script>

<template>
  <div class="knowledge-graph">
    <h1>知识图谱</h1>
    <div ref="container" class="graph-container"></div>
  </div>
</template>

<style scoped>
.knowledge-graph {
  max-width: 960px;
  margin: 0 auto;
  padding: 1rem;
  font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.graph-container {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  overflow: hidden;
  min-height: 500px;
  background: var(--vp-c-bg);
}
</style>
