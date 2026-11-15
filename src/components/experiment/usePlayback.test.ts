import { describe, it, expect } from "vitest";
import { playbackReducer } from "./usePlayback";
const start = { index: 0, count: 7, playing: false, speed: 900, instant: true };
describe("playback state transitions", () => {
  it("seeking during playback cancels autoplay and clamps to the exact target", () => {
    const playing = playbackReducer(start, { type: "toggle" });
    const sought = playbackReducer(playing, { type: "seek", index: 99 });
    expect(sought).toMatchObject({ index: 6, playing: false, instant: true });
  });
  it("the final tick stops and manual backward steps remain bounded", () => {
    expect(
      playbackReducer({ ...start, index: 5, playing: true }, { type: "tick" }),
    ).toMatchObject({ index: 6, playing: false });
    expect(playbackReducer(start, { type: "step", by: -1 }).index).toBe(0);
  });
  it("new traces cannot inherit queued playback from the old input", () => {
    expect(
      playbackReducer(
        { ...start, index: 6, playing: true },
        { type: "load", count: 3, index: 99 },
      ),
    ).toMatchObject({ index: 2, count: 3, playing: false, instant: true });
  });
});
