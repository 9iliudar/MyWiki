export function stripIpaFromTitle(title: string) {
  return title
    .replace(/\s*\/[^/\n]+\/(?=\s*[）)])?/g, "")
    .replace(/\s{2,}/g, " ")
    .replace(/（\s+/g, "（")
    .replace(/\s+）/g, "）")
    .trim();
}

/**
 * Aggressive cleanup for short display contexts (graph nodes, universe pills).
 * Strips IPA, removes parenthetical full-names, and truncates.
 */
export function cleanDisplayName(title: string, maxLen = 14): string {
  let name = stripIpaFromTitle(title);
  // Remove （full name） or (full name) parenthetical expansions
  name = name.replace(/[（(][^）)]+[）)]/g, "").trim();
  if (name.length > maxLen) name = name.slice(0, maxLen - 1) + "…";
  return name;
}
