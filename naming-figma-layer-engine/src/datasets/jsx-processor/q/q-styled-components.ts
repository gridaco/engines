import { ParseResult } from "@babel/parser";
import traverse from "@babel/traverse";
import * as t from "@babel/types";
import q_imports from "./q-imports";

function q_imports_styled(ast: ParseResult<t.File>) {
  const imports = q_imports(ast);
  const _m_styled_components = imports.get("styled-components");
  const _m_emotion_styled = imports.get("@emotion/styled");
  const _m_linaria_react = imports.get("linaria/react");

  if (
    _m_styled_components &&
    _m_styled_components.find((s) => s === "styled")
  ) {
    return _m_styled_components[0];
  }

  if (_m_emotion_styled && _m_emotion_styled.find((s) => s === "styled")) {
    return _m_emotion_styled[0];
  }

  if (_m_linaria_react && _m_linaria_react.find((s) => s === "styled")) {
    return _m_linaria_react[0];
  }
}

export default function q_styled_components(ast: ParseResult<t.File>) {
  const styled = q_imports_styled(ast);

  const declarations = Array<{
    name: string;
    el: string;
    value: string;
  }>();

  if (styled) {
    // find styled components declarations with format <<const X = styled.x`...`>>
    traverse(ast, {
      enter(path) {
        if (
          t.isVariableDeclarator(path.node) &&
          path.node.id.type === "Identifier" &&
          path.node.init.type === "TaggedTemplateExpression" &&
          path.node.init.tag.type === "MemberExpression" &&
          path.node.init.tag.object.type === "Identifier" &&
          path.node.init.tag.property.type === "Identifier" &&
          path.node.init.tag.object.name === styled
        ) {
          const name = path.node.id.name;
          const el = path.node.init.tag.property.name;
          const value = path.node.init.quasi.quasis
            .map((q) => q.value.raw)
            .join("");

          declarations.push({ name, el, value });
        }
      },
    });
  }

  return declarations;
}
