// r7 key stills: render chosen frames of a composition as PNG from one bundle (no video encode, no audio).
// Usage: node remotion/stills.mjs <CompositionId> <outDir> <frames: comma list; negative = from the end, e.g. 0,9,29,mid,-1> [scale=0.5] [propsJson={}]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path"; import fs from "node:fs"; import { fileURLToPath } from "node:url";
const R = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const [id, out, list = "0,-1", scale = "0.5", props = "{}"] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(R, "remotion/src/index.ts"), publicDir: path.join(R, "remotion/public"), rspack: true });
const chromiumOptions = { gl: "swangle" };
const inputProps = JSON.parse(props);
const composition = await selectComposition({ serveUrl, id, inputProps, chromiumOptions });
const D = composition.durationInFrames;
const res = [];
for (const tok of list.split(",")) {
  const f = tok === "mid" ? Math.floor(D / 2) : Number(tok) < 0 ? D + Number(tok) : Number(tok);
  const output = path.join(out, `still_${tok.replace("-", "m")}.png`);
  await renderStill({ composition, serveUrl, inputProps, chromiumOptions, frame: f, output, scale: Number(scale), logLevel: "error" });
  res.push({ tok, frame: f, output });
}
console.log(JSON.stringify({ id, durationInFrames: D, fps: composition.fps, stills: res }));
