// Renders all round-4 style frames as PNG stills from one bundle.
// Look A mechanism/end = the real episode composition (v4 code with contrast fixes) at that moment; everything else = StyleFrame comp.
// Usage: node remotion/style_frames.mjs <outDir> <realframes.json>
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path"; import fs from "node:fs"; import { fileURLToPath } from "node:url";
const R = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const [out, rf] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
const real = JSON.parse(fs.readFileSync(rf, "utf8"));
const serveUrl = await bundle({ entryPoint: path.join(R, "remotion/src/index.ts"), publicDir: path.join(R, "remotion/public"), rspack: true });
const chromiumOptions = { gl: "swangle" };
const ids = { qr: "QR", elevator: "Elevator", sky: "Sky" };
const jobs = [];
for (const ep of ["qr", "elevator", "sky"]) for (const look of ["A", "B"]) for (const kind of ["hook", "mechanism", "proof", "end"]) jobs.push({ ep, look, kind });
const t0 = Date.now(); const times = {};
for (const j of jobs) {
  const t = Date.now();
  const useReal = j.look === "A" && (j.kind === "mechanism" || j.kind === "end");
  const id = useReal ? ids[j.ep] : "StyleFrame"; const inputProps = useReal ? {} : j;
  const composition = await selectComposition({ serveUrl, id, inputProps, chromiumOptions });
  const frame = useReal ? real[ids[j.ep]][j.kind === "mechanism" ? "mech" : "end"] : 60;
  const file = path.join(out, `${j.ep}_${j.look}_${["hook", "mechanism", "proof", "end"].indexOf(j.kind) + 1}-${j.kind}.png`);
  await renderStill({ composition, serveUrl, inputProps, chromiumOptions, frame, output: file, imageFormat: "png", logLevel: "error" });
  times[path.basename(file)] = Date.now() - t;
}
console.log(JSON.stringify({ n: jobs.length, total_s: (Date.now() - t0) / 1000, times }));
