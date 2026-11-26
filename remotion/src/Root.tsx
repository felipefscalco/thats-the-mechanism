import React from "react";
import { Composition } from "remotion";
import { QRVideo } from "./episodes/QR";
import { ElevatorVideo } from "./episodes/Elevator";
import { SkyVideo } from "./episodes/Sky";
import durations from "./durations.json";
import { IceDemoVideo } from "./episodes/IceDemo";
import { StyleFrame } from "./style/StyleFrames";
import { LottiePreview } from "./style/LottiePreview";
import { ANCVideo } from "./episodes/ANC";
// @new-episode-imports

const fps = 30;
const frames = (s: number) => Math.ceil(s * fps);
const portrait = { fps, width: 1080, height: 1920 } as const;
export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="QR" component={QRVideo} durationInFrames={frames(durations["01-qr-code"])} {...portrait} />
    <Composition id="Elevator" component={ElevatorVideo} durationInFrames={frames(durations["02-elevator"])} {...portrait} />
    <Composition id="Sky" component={SkyVideo} durationInFrames={frames(durations["03-sky"])} {...portrait} />
    <Composition id="IceDemo" component={IceDemoVideo} durationInFrames={frames((durations as Record<string, number>)["04-ice-demo"] ?? 10)} {...portrait} />
    <Composition id="LottiePreview" component={LottiePreview} durationInFrames={60} fps={30} width={512} height={512} />
    <Composition id="StyleFrame" component={StyleFrame} durationInFrames={90} {...portrait} />
    <Composition id="ANC" component={ANCVideo} durationInFrames={frames((durations as Record<string, number>)["05-anc-headphones"] ?? 10)} {...portrait} />
    {/* @new-episode-compositions */}
  </>
);
