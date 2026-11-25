import React, { useMemo } from "react";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { LAYOUT } from "./tokens";

/** Pixel-aligned orthographic 3D layer: (x, y) in stage pixels map 1:1 onto the 1080x1920 frame, so 3D hero objects
 *  line up with the 2D SVG overlays drawn on top. Render with --gl=swangle (set in remotion.config.ts). */
export const Ortho3D: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThreeCanvas width={LAYOUT.W} height={LAYOUT.H} orthographic
    camera={{ left: -LAYOUT.W / 2, right: LAYOUT.W / 2, top: LAYOUT.H / 2, bottom: -LAYOUT.H / 2, near: -2000, far: 2000, position: [0, 0, 1000] }}
    style={{ position: "absolute", inset: 0 }}>
    {children}
  </ThreeCanvas>
);

/** Low-poly lit planet: faceted shading gives depth; the light direction draws a real day/night terminator. */
export const Planet: React.FC<{ x: number; y: number; r: number; spin: number; light: [number, number, number]; land: string; sea: string }> =
  ({ x, y, r, spin, light, land, sea }) => {
    const geo = useMemo(() => {
      const g = new THREE.IcosahedronGeometry(1, 4);
      const pos = g.attributes.position; const cols: number[] = [];
      const cl = new THREE.Color(land), cs = new THREE.Color(sea);
      for (let i = 0; i < pos.count; i += 3) {
        const cx = (pos.getX(i) + pos.getX(i + 1) + pos.getX(i + 2)) / 3, cy = (pos.getY(i) + pos.getY(i + 1) + pos.getY(i + 2)) / 3, cz = (pos.getZ(i) + pos.getZ(i + 1) + pos.getZ(i + 2)) / 3;
        const n = Math.sin(cx * 4.1 + 1.3) * Math.cos(cy * 3.7) + Math.sin(cz * 5.3 + cy * 2.1) * 0.6; // deterministic "continents"
        const c = n > 0.35 ? cl : cs;
        for (let k = 0; k < 3; k++) cols.push(c.r, c.g, c.b);
      }
      const ng = g.toNonIndexed(); ng.setAttribute("color", new THREE.Float32BufferAttribute(cols, 3)); ng.computeVertexNormals();
      return ng;
    }, [land, sea]);
    const X = x - LAYOUT.W / 2, Y = LAYOUT.H / 2 - y;
    return (
      <>
        <ambientLight intensity={0.12} />
        <directionalLight position={light} intensity={4.5} />
        <mesh geometry={geo} position={[X, Y, 0]} scale={r} rotation={[0.35, spin, 0.1]}>
          <meshStandardMaterial vertexColors flatShading roughness={0.85} metalness={0} />
        </mesh>
      </>
    );
  };
