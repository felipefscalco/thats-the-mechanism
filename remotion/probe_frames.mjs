// Render every Nth frame of a composition as PNG with given input props (default {probe:true}), one bundle.
// Usage: node remotion/probe_frames.mjs <CompositionId> <outDir> [everyNth=6] [scale=0.5] [propsJson] [outDir2 props2Json everyNth2] [outDir3 props3Json everyNth3]
import { bundle } from "@remotion/bundler";
import { renderFrames, selectComposition } from "@remotion/renderer";
import path from "node:path"; import fs from "node:fs"; import { fileURLToPath } from "node:url";
const R = path.resolve(path.dirname(fileURLToPath(import.meta.url)), ".."); // remotion/probe_frames.mjs -> project root
const [id, out, nth = "6", scale = "0.5", props = '{"probe":true}', out2, props2, nth2, out3, props3, nth3] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
if (out2) fs.mkdirSync(out2, { recursive: true });
if (out3) fs.mkdirSync(out3, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(R, "remotion/src/index.ts"), publicDir: path.join(R, "remotion/public"), rspack: true });
const chromiumOptions = { gl: "swangle" };
async function renderPass(dir, propsJson, every = nth) {
  const inputProps = JSON.parse(propsJson);
  const composition = await selectComposition({ serveUrl, id, inputProps, chromiumOptions });
  await renderFrames({ composition, serveUrl, inputProps, chromiumOptions, outputDir: dir, imageFormat: "png", everyNthFrame: Number(every), scale: Number(scale),
    concurrency: 6, onStart: () => {}, onFrameUpdate: () => {}, logLevel: "error" });
  return composition;
}
const composition = await renderPass(out, props);
if (out2 && props2) await renderPass(out2, props2, nth2 || nth);
if (out3 && props3) await renderPass(out3, props3, nth3 || nth); // r7 preview: normal look as stills (no MP4)
console.log(JSON.stringify({ id, out, out2: out2 || null, durationInFrames: composition.durationInFrames, fps: composition.fps, nth: Number(nth) }));
