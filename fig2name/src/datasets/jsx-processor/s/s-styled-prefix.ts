export function sanitize_remove_styled_prefix(n: string): string {
  // remove 'Styled' prefix
  if (n.startsWith("Styled")) {
    return n.slice(6);
  }

  return n;
}
