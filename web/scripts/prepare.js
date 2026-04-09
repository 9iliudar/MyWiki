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

    // Inject h1 title if not present in body
    const bodyAfterFrontmatter = content.replace(/^---[\s\S]*?---\s*/, "");
    const hasH1 = /^#\s+/m.test(bodyAfterFrontmatter);
    if (!hasH1 && (data.title || name)) {
      const title = data.title || name;
      const injected = content.replace(
        /^(---[\s\S]*?---\s*)/,
        `$1\n# ${title}\n\n`
      );
      fs.writeFileSync(path.join(WEB_PAGES_DIR, file), injected, "utf-8");
    } else {
      fs.copyFileSync(srcPath, path.join(WEB_PAGES_DIR, file));
    }
  }

  fs.writeFileSync(
    path.join(DATA_DIR, "wiki-meta.json"),
    JSON.stringify(allMeta, null, 2),
    "utf-8"
  );

  const nameSet = new Set(allMeta.map(p => p.name));
  // Map Chinese titles to file names for wikilink resolution
  const titleToName = {};
  for (const p of allMeta) {
    titleToName[p.title] = p.name;
    titleToName[p.name] = p.name;
  }
  const nodes = allMeta.map(p => ({ id: p.name, title: p.title, tags: p.tags }));
  const edgeSet = new Set();
  const edges = [];

  function addEdge(source, target) {
    if (source === target) return;
    const key = [source, target].sort().join("||");
    if (edgeSet.has(key)) return;
    edgeSet.add(key);
    edges.push({ source, target });
  }

  for (const page of allMeta) {
    // From frontmatter related field
    for (const rel of page.related) {
      const target = rel.replace(/^\[\[/, "").replace(/\]\]$/, "");
      if (nameSet.has(target)) addEdge(page.name, target);
    }
    // From body [[wikilinks]]
    const srcPath = path.join(WIKI_PAGES_DIR, page.name + ".md");
    const body = fs.readFileSync(srcPath, "utf-8");
    const wikilinks = body.match(/\[\[([^\]]+)\]\]/g) || [];
    for (const link of wikilinks) {
      const raw = link.slice(2, -2);
      const target = titleToName[raw] || raw;
      if (nameSet.has(target)) addEdge(page.name, target);
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
