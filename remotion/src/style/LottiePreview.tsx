import React, { useEffect, useState } from "react";
import { AbsoluteFill, cancelRender, continueRender, delayRender, getInputProps, staticFile } from "remotion";
import { Lottie, LottieAnimationData } from "@remotion/lottie";
/** Preview/thumbnail of a library Lottie (assets/library/lottie). Props: { name }. Also the usage pattern for episodes. */
export const LottiePreview: React.FC = () => {
  const { name = "gear_spin" } = getInputProps() as { name?: string };
  const [handle] = useState(() => delayRender("lottie"));
  const [data, setData] = useState<LottieAnimationData | null>(null);
  useEffect(() => { fetch(staticFile(`library/${name}.json`)).then((r) => r.json()).then((j) => { setData(j); continueRender(handle); }).catch((e) => cancelRender(e)); }, [handle, name]);
  return <AbsoluteFill style={{ background: "#171A22" }}>{data && <Lottie animationData={data} loop />}</AbsoluteFill>;
};
