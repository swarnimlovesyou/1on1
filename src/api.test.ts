import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";
import { api, ApiError, resetCsrf, streamTutor } from "./api";
beforeEach(() => {
  resetCsrf();
  vi.stubGlobal("fetch", vi.fn());
});
afterEach(() => vi.unstubAllGlobals());
describe("Java API boundary", () => {
  it("assembles actual streamed tutor tokens and requires completion", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ csrf: "test-token" })),
      )
      .mockResolvedValueOnce(
        new Response(
          'event:token\ndata:{"text":"A window "}\n\nevent:token\ndata:{"text":"shares work."}\n\nevent:done\ndata:{"ok":true}\n\n',
        ),
      );
    const onToken = vi.fn();
    expect(await streamTutor({ message: "Why?" }, onToken)).toBe(
      "A window shares work.",
    );
    expect(onToken).toHaveBeenLastCalledWith("A window shares work.");
  });
  it("never labels an interrupted tutor stream as complete", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ csrf: "test-token" })),
      )
      .mockResolvedValueOnce(
        new Response('event:token\ndata:{"text":"Partial answer"}\n\n'),
      );
    await expect(streamTutor({ message: "Why?" }, () => {})).rejects.toThrow(
      "interrupted",
    );
  });
  it("reports a free-tier provider limit inside a stream", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ csrf: "test-token" })),
      )
      .mockResolvedValueOnce(
        new Response(
          'event:error\ndata:{"message":"Free-tier quota exhausted"}\n\n',
        ),
      );
    await expect(streamTutor({ message: "Why?" }, () => {})).rejects.toThrow(
      "quota",
    );
  });
  it("obtains the server CSRF token before a mutating request", async () => {
    const fetcher = vi.mocked(fetch);
    fetcher
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ csrf: "test-token" })),
      )
      .mockResolvedValueOnce(new Response(JSON.stringify({ ok: true })));
    await api("/notes", { text: "A thought" });
    expect(fetcher.mock.calls[1][1]).toMatchObject({
      credentials: "include",
      method: "POST",
      headers: { "X-CSRF-TOKEN": "test-token" },
    });
  });
  it("surfaces a service failure instead of treating it as success", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify({ message: "Runner unavailable" }), {
        status: 503,
      }),
    );
    await expect(api("/system")).rejects.toMatchObject({
      message: "Runner unavailable",
      status: 503,
    });
  });
  it("reports invalid JSON error responses with a recovery message", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response("upstream unavailable", { status: 502 }),
    );
    await expect(api("/system")).rejects.toBeInstanceOf(ApiError);
  });
});
