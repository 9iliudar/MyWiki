import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const WIKI_PAGES_DIR = path.resolve(__dirname, "../../wiki/MyWiki");
const WEB_PAGES_DIR = path.resolve(__dirname, "../pages");
const DATA_DIR = path.resolve(__dirname, "../data");

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function walkMarkdownFiles(dir, base = dir) {
  const files = [];
  if (!fs.existsSync(dir)) return files;

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".")) continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkMarkdownFiles(fullPath, base));
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      files.push({
        fullPath,
        relativePath: path.relative(base, fullPath),
      });
    }
  }
  return files;
}

function routeFromSlug(slug) {
  return `/pages/${slug}.html`;
}

function main() {
  ensureDir(WEB_PAGES_DIR);
  ensureDir(DATA_DIR);

  const files = walkMarkdownFiles(WIKI_PAGES_DIR);
  const allMeta = [];

  for (const file of files) {
    const srcPath = file.fullPath;
    const relativePath = file.relativePath;
    const content = fs.readFileSync(srcPath, "utf-8");
    const { data } = matter(content);
    const slug = relativePath.replace(/\\/g, "/").replace(/\.md$/, "");
    const name = path.basename(relativePath, ".md");
    const category = path.dirname(relativePath).replace(/\\/g, "/") || "General";
    const route = routeFromSlug(slug);

    allMeta.push({
      name,
      slug,
      route,
      category,
      title: data.title || name,
      tags: data.tags || [],
      related: data.related || [],
      sources: data.sources || [],
      created: data.created || "",
      updated: data.updated || "",
      evolution: data.evolution || [],
    });

    const targetPath = path.join(WEB_PAGES_DIR, `${slug}.md`);
    ensureDir(path.dirname(targetPath));

    const bodyAfterFrontmatter = content.replace(/^---[\s\S]*?---\s*/, "");
    const hasH1 = /^#\s+/m.test(bodyAfterFrontmatter);
    if (!hasH1 && (data.title || name)) {
      const title = data.title || name;
      const injected = content.replace(/^(---[\s\S]*?---\s*)/, `$1\n# ${title}\n\n`);
      fs.writeFileSync(targetPath, injected, "utf-8");
    } else {
      fs.copyFileSync(srcPath, targetPath);
    }
  }

  fs.writeFileSync(
    path.join(DATA_DIR, "wiki-meta.json"),
    JSON.stringify(allMeta, null, 2),
    "utf-8"
  );

  const routeByName = {};
  const routeByTitle = {};
  for (const page of allMeta) {
    routeByName[page.name] = page.route;
    routeByTitle[page.title] = page.route;
  }

  fs.writeFileSync(
    path.join(DATA_DIR, "route-map.json"),
    JSON.stringify({ routeByName, routeByTitle }, null, 2),
    "utf-8"
  );

  const nameSet = new Set(allMeta.map((p) => p.name));
  const titleToName = {};
  for (const page of allMeta) {
    titleToName[page.title] = page.name;
    titleToName[page.name] = page.name;
  }

  const nodes = allMeta.map((p) => ({ id: p.name, title: p.title, tags: p.tags, category: p.category }));
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
    for (const rel of page.related) {
      const target = rel.replace(/^\[\[/, "").replace(/\]\]$/, "");
      if (nameSet.has(target)) addEdge(page.name, target);
    }

    const srcPath = path.join(WIKI_PAGES_DIR, page.slug + ".md");
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

  console.log(`Prepared ${files.length} pages across ${new Set(allMeta.map((p) => p.category)).size} categories`);
}

main();
