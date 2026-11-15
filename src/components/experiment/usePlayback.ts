import { useEffect, useReducer } from "react";

type State = {
  index: number;
  count: number;
  playing: boolean;
  speed: number;
  instant: boolean;
};
type Action =
  | { type: "load"; count: number; index: number }
  | { type: "step"; by: number }
  | { type: "seek"; index: number }
  | { type: "toggle" }
  | { type: "pause" }
  | { type: "speed"; value: number }
  | { type: "tick" };
export function playbackReducer(state: State, action: Action): State {
  const clamp = (index: number) =>
    Math.max(0, Math.min(state.count - 1, index));
  switch (action.type) {
    case "load":
      return {
        ...state,
        count: action.count,
        index: Math.max(0, Math.min(action.count - 1, action.index)),
        playing: false,
        instant: true,
      };
    case "step":
      return {
        ...state,
        index: clamp(state.index + action.by),
        playing: false,
        instant: false,
      };
    case "seek":
      return {
        ...state,
        index: clamp(action.index),
        playing: false,
        instant: true,
      };
    case "toggle":
      return {
        ...state,
        index: state.index >= state.count - 1 ? 0 : state.index,
        playing: !state.playing && state.count > 1,
        instant: false,
      };
    case "pause":
      return { ...state, playing: false };
    case "speed":
      return { ...state, speed: action.value };
    case "tick": {
      const index = clamp(state.index + 1);
      return {
        ...state,
        index,
        playing: index < state.count - 1,
        instant: false,
      };
    }
  }
}
export function usePlayback() {
  const [state, dispatch] = useReducer(playbackReducer, {
    index: 0,
    count: 0,
    playing: false,
    speed: 900,
    instant: true,
  });
  useEffect(() => {
    if (!state.playing) return;
    const timer = setTimeout(() => dispatch({ type: "tick" }), state.speed);
    return () => clearTimeout(timer);
  }, [state.playing, state.index, state.speed, state.count]);
  useEffect(() => {
    const hide = () => {
      if (document.hidden) dispatch({ type: "pause" });
    };
    document.addEventListener("visibilitychange", hide);
    return () => document.removeEventListener("visibilitychange", hide);
  }, []);
  return { state, dispatch };
}
