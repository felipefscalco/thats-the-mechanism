// Render every Nth frame of a composition as PNG with given input props (default {probe:true}), one bundle.
// Usage: node remotion/probe_frames.mjs <CompositionId> <outDir> [everyNth=6] [scale=0.5] [propsJson]
import { bundle } from "@remotion/bundler";
import { renderFrames, selectComposition } from "@remotion/renderer";
import path from "node:path"; import fs from "node:fs"; import { fileURLToPath } from "node:url";
const R = path.resolve(path.dirname(fileURLToPath(import.meta.url)), ".."); // remotion/probe_frames.mjs -> project root
const [id, out, nth = "6", scale = "0.5", props = '{"probe":true}'] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(R, "remotion/src/index.ts"), publicDir: path.join(R, "remotion/public"), rspack: true });
const inputProps = JSON.parse(props);
const chromiumOptions = { gl: "swangle" };
const composition = await selectComposition({ serveUrl, id, inputProps, chromiumOptions });
await renderFrames({ composition, serveUrl, inputProps, chromiumOptions, outputDir: out, imageFormat: "png", everyNthFrame: Number(nth), scale: Number(scale),
  concurrency: 6, onStart: () => {}, onFrameUpdate: () => {}, logLevel: "error" });
console.log(JSON.stringify({ id, out, durationInFrames: composition.durationInFrames, fps: composition.fps, nth: Number(nth) }));
