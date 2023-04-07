const fs = require("fs");

// from https://developer.mozilla.org/en-US/docs/Web/CSS/font-family
const generic = [
  "serif",
  "sans-serif",
  "monospace",
  "cursive",
  "fantasy",
  "system-ui",
  "ui-serif",
  "ui-sans-serif",
  "ui-monospace",
  "ui-rounded",
  "emoji",
  "math",
  "fangsong",
];

// place fonts.json in the same directory as this script
// you can download it from https://raw.githubusercontent.com/GoogleForCreators/web-stories-wp/main/packages/fonts/src/fonts.json
async function main() {
  const json = require("./fonts.json");

  // the json is a array of {family: "<font name>", fallbacks: ["<fallback name>"]}
  // we want to convert it to a map of {<font name>: ["<fallback name>"]}

  const map = json.reduce((acc, { family, fallbacks }) => {
    acc[family] = fallbacks.filter((f) => generic.includes(f));
    return acc;
  }, {});

  // write the map to a file
  fs.writeFileSync("font-fallbacks-map.json", JSON.stringify(map));
}

main();
