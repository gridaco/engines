export function sanitize_tokenize_uppoer_camel_case(n: string): string {
  // tokenize upper camel case
  const tokens = n.split(/(?=[A-Z])/);
  return tokens.join("-").toLowerCase();
}

export function sanitize_tokenize_number(n: string): string {
  // tokenize number
  const tokens = n.split(/(?=[0-9])/);
  return tokens.join("-").toLowerCase();
}

export function sanitize_tokenize_identifier(n: string): string {
  return sanitize_tokenize_number(sanitize_tokenize_uppoer_camel_case(n));
}
