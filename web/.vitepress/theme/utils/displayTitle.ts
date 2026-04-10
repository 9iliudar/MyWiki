export function stripIpaFromTitle(title: string) {
  return title
    .replace(/\s*\/[^/\n]+\/(?=\s*[）)])?/g, "")
    .replace(/\s{2,}/g, " ")
    .replace(/（\s+/g, "（")
    .replace(/\s+）/g, "）")
    .trim();
}
