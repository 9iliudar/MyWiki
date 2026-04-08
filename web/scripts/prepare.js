import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const WIKI_PAGES_DIR = path.resolve(__dirname, "../../wiki/pages");
const WEB_PAGES_DIR = path.resolve(__dirname, "../pages");
const DATA_DIR = path.resolve(__dirname, "../data");

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function main() {
  ensureDir(WEB_PAGES_DIR);
  ensureDir(DATA_DIR);

  const files = fs.readdirSync(WIKI_PAGES_DIR).filter(f => f.endsWith(".md"));
  const allMeta = [];

  for (const file of files) {
    const srcPath = path.join(WIKI_PAGES_DIR, file);
    const content = fs.readFileSync(srcPath, "utf-8");
    const { data } = matter(content);
    const name = file.replace(/\.md$/, "");

    allMeta.push({
      name,
      title: data.title || name,
      tags: data.tags || [],
      related: data.related || [],
      sources: data.sources || [],
      created: data.created || "",
      updated: data.updated || "",
      evolution: data.evolution || [],
    });

    fs.copyFileSync(srcPath, path.join(WEB_PAGES_DIR, file));
  }

  fs.writeFileSync(
    path.join(DATA_DIR, "wiki-meta.json"),
    JSON.stringify(allMeta, null, 2),
    "utf-8"
  );

  const nodes = allMeta.map(p => ({ id: p.name, title: p.title, tags: p.tags }));
  const edges = [];
  for (const page of allMeta) {
    for (const rel of page.related) {
      const target = rel.replace(/^\[\[/, "").replace(/\]\]$/, "");
      if (allMeta.some(p => p.name === target)) {
        edges.push({ source: page.name, target });
      }
    }
  }

  fs.writeFileSync(
    path.join(DATA_DIR, "graph.json"),
    JSON.stringify({ nodes, edges }, null, 2),
    "utf-8"
  );

  console.log(`Prepared ${files.length} pages, ${edges.length} edges`);
}

main();
