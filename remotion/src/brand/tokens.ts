import { loadFont as loadDisplay } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadSans } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

export const DISPLAY = loadDisplay("normal", { weights: ["500", "700"], subsets: ["latin"] }).fontFamily;
export const SANS = loadSans("normal", { weights: ["600", "800", "900"], subsets: ["latin"] }).fontFamily;
export const MONO = loadMono("normal", { weights: ["500", "700"], subsets: ["latin"] }).fontFamily;

export const C = {
  ink: "#0D0E12", ink2: "#171A22", ink3: "#232734", line: "#3A3F4E",
  paper: "#F3EFE6", dim: "#8B91A1", amber: "#FFB020", red: "#FF5A4E", green: "#3DDC97",
};
export type Pillar = { name: string; color: string };
export const PILLARS = {
  tech: { name: "TECH", color: "#4CC9F0" },
  eng: { name: "ENGINEERING", color: "#7BD389" },
  sci: { name: "PHYSICS", color: "#9B8CFF" },
  philo: { name: "PHILOSOPHY", color: "#FF7AB6" },
} satisfies Record<string, Pillar>;

/** 1080x1920 layout. Platform UI (YT Shorts / Reels / TikTok) covers ~top 220px,
 *  ~bottom 360px and a right-hand button column (x>900) from y≈900 down. */
export const LAYOUT = {
  W: 1080, H: 1920, FPS: 30,
  stageTop: 290, stageBottom: 1190,      // diagram "world"
  captionTop: 1222,                       // captions 1222-1430
  deckTop: 1462, deckBottom: 1552,        // chapter + progress deck (bottom safe limit 1560)
  safeLeft: 60, safeRight: 900,           // keep text left of the right button column
  minText: 30,                            // px, anti-slideshow rule: text >= 30px on 1080 stage
};
