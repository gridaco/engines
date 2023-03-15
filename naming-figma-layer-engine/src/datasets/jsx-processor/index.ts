import sqlite3 from "sqlite3";
import { open } from "sqlite";
import fs from "fs";
import path from "path";
import { parse } from "@babel/parser";
import assert from "assert";
import q_styled_components from "./q/q-styled-components";
import { sanitize_remove_styled_prefix } from "./s/s-styled-prefix";
import { sanitize_tokenize_identifier } from "./s/s-tokenize-identifier";
import { sanitize_css_value } from "./s/s-value";

interface DSRFile {
  repo: string;
  path: string;
  language: string;
  content: string;
}

async function main() {
  const file = path.resolve(__dirname, "../../../data/raw/s.db");

  // ensure file exists
  assert(fs.existsSync(file));

  const db = await open({
    filename: file,
    driver: sqlite3.Database,
  });

  const set = [];

  // read the first item from the database, the language is [jsx, tsx, js, ts]
  await db.each<DSRFile>(
    `SELECT * FROM files WHERE language LIKE '%x';`,
    (err, res) => {
      try {
        const _ = handle(res);
        if (_?.length > 0) {
          _.forEach((s) => {
            const name = sanitize_tokenize_identifier(
              sanitize_remove_styled_prefix(s.name)
            );

            const value = sanitize_css_value(s.value);

            if (!value) {
              return;
            }

            set.push({
              id: `${res.repo}::${res.path}::${s.name}`,
              repo: res.repo,
              path: res.path,
              name_o: s.name,
              name_t: name,
              el: s.el,
              value: value,
            });
          });
        }
      } catch (e) {}
    }
  );

  // write file to disk
  fs.writeFileSync(
    path.resolve(__dirname, "./out/styled-components.json"),
    JSON.stringify(set, null, 2)
  );

  console.log("done", set.length);
}

function handle({ path, content, language }: DSRFile) {
  const ast = parse(content, {
    sourceFilename: path,
    sourceType: "module",
    plugins: language.includes("ts") ? ["jsx", "typescript"] : ["flow", "jsx"],
  });

  return q_styled_components(ast);
}

// main

if (require.main === module) {
  main();
}
