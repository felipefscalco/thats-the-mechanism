// Export a curated icon set to assets/library/icons/{lucide,tabler}/*.svg (brand stroke colour). lucide: ISC; tabler: MIT.
import React from "react"; import { renderToStaticMarkup } from "react-dom/server";
import * as L from "lucide-react"; import * as T from "@tabler/icons-react";
import fs from "node:fs"; import path from "node:path"; import { fileURLToPath } from "node:url";
const R = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../assets/library/icons");
const lucide = ["ScanLine", "QrCode", "Smartphone", "Disc3", "Zap", "ArrowUp", "ArrowDown", "Scale", "Weight", "Cog", "Sun", "Sunset", "Eye", "Waves", "Atom", "Check", "X", "Ruler", "Gauge", "Lightbulb"];
const tabler = ["IconElevator", "IconBuildingSkyscraper", "IconCrane", "IconQrcode", "IconSun", "IconSunset2", "IconWaveSine", "IconAtom2", "IconEngine", "IconBarbell"];
let n = 0;
for (const [set, names, lib] of [["lucide", lucide, L], ["tabler", tabler, T]]) {
  fs.mkdirSync(path.join(R, set), { recursive: true });
  for (const nm of names) { const C = lib[nm]; if (!C) { console.log("missing", set, nm); continue; }
    fs.writeFileSync(path.join(R, set, `${nm}.svg`), renderToStaticMarkup(React.createElement(C, { size: 96, color: "#F3EFE6", strokeWidth: 2 }))); n++; }
}
console.log("icons", n);
