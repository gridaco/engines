export function sanitize_css_value(v: string): string {
  if (/^\s*$/.test(v)) return null;

  return v
    .split("\n")
    .map((s) => s.trim())
    .join("\n");
}
