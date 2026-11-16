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
  it("retries a write once with a fresh token when a first-visit session race made the old one stale", async () => {
    const fetcher = vi.mocked(fetch);
    fetcher
      .mockResolvedValueOnce(new Response(JSON.stringify({ csrf: "stale" })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ message: "Refresh the page" }), { status: 403 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ csrf: "fresh" })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ steps: [] })));
    expect(await api("/experiments", { algorithm: "sliding-window" })).toEqual({ steps: [] });
    expect((fetcher.mock.calls[3][1] as RequestInit).headers).toMatchObject({ "X-CSRF-TOKEN": "fresh" });
  });
  it("does not retry a write that is refused twice", async () => {
    const fetcher = vi.mocked(fetch);
    fetcher
      .mockResolvedValueOnce(new Response(JSON.stringify({ csrf: "a" })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ message: "No" }), { status: 403 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ csrf: "b" })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ message: "Still no" }), { status: 403 }));
    await expect(api("/admin/content", {})).rejects.toMatchObject({ status: 403, message: "Still no" });
    expect(fetcher).toHaveBeenCalledTimes(4);
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
