import React, { createContext, useContext } from "react";
/** Global frame for episode artwork. Shots wrap content in Sequences (local frames);
 *  artwork reads the global frame from here so it can be frozen (LoopBack renders the hook at frame 0). */
export const GlobalFrame = createContext<number | null>(null);
export const useG = () => {
  const f = useContext(GlobalFrame);
  if (f === null) throw new Error("useG() outside <EpisodeShell>");
  return f;
};
export const AtFrame: React.FC<{ f: number; children: React.ReactNode }> = ({ f, children }) => (
  <GlobalFrame.Provider value={f}>{children}</GlobalFrame.Provider>
);

/** r10 ambient clock (component for the critic rule "debris, particles and fluid streams never freeze mid-air", e07).
 *  useG() freezes during the r9 payoff hold so the LAYOUT settles; useAmbient() keeps running there, so continuous
 *  motion (particles, steam, water, waves, rings) never hangs in mid-air. LoopBack pins it to 0 with the hook, so the
 *  loop seam stays exact. Use useG() for layout/state, useAmbient() only for looping ambient motion. */
export const AmbientFrame = createContext<number | null>(null);
export const useAmbient = () => {
  const a = useContext(AmbientFrame);
  const g = useG();
  return a ?? g;
};
export const AtAmbient: React.FC<{ f: number; children: React.ReactNode }> = ({ f, children }) => (
  <AmbientFrame.Provider value={f}>{children}</AmbientFrame.Provider>
);
