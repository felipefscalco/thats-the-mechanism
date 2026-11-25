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
