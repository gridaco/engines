import { ParseResult } from "@babel/parser";
import traverse from "@babel/traverse";
import * as t from "@babel/types";

export default function q_imports(ast: ParseResult<t.File>) {
  const imports = new Map<string, string[]>();
  traverse(ast, {
    enter(path) {
      if (t.isImportDeclaration(path.node)) {
        imports.set(
          path.node.source.value,
          path.node.specifiers.map((s) => s.local.name)
        );
      }
    },
  });

  return imports;
}
