import { createContext, useContext } from "react";
import type { User, Progress } from "./types";
export const AppContext = createContext<{
  user: User | null;
  progress: Progress;
  progressReady: boolean;
  notify: (s: string) => void;
  reload: () => void;
}>({
  user: null,
  progress: {} as Progress,
  progressReady: false,
  notify: () => {},
  reload: () => {},
});
export const useApp = () => useContext(AppContext);
