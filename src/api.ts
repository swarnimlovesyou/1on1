let csrf = "";
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}
export async function api<T>(
  path: string,
  body?: unknown,
  method?: string,
  signal?: AbortSignal,
): Promise<T> {
  const verb = method ?? (body === undefined ? "GET" : "POST");
  if (verb !== "GET" && !csrf) {
    const r = await fetch("/api/v1/auth/session", { credentials: "include" });
    const data = await r.json();
    csrf = data.csrf;
  }
  const r = await fetch("/api/v1" + path, {
    method: verb,
    credentials: "include",
    signal,
    headers: {
      "Content-Type": "application/json",
      ...(csrf ? { "X-CSRF-TOKEN": csrf } : {}),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const data = await r.json().catch(() => ({
    message: "The server could not be reached. Check the connection and retry.",
  }));
  if (data.csrf) csrf = data.csrf;
  if (!r.ok) {
    if (r.status === 403) csrf = "";
    throw new ApiError(
      data.message ?? "The request could not be completed.",
      r.status,
    );
  }
  return data;
}
export function resetCsrf() {
  csrf = "";
}
export async function streamTutor(
  body: unknown,
  onToken: (text: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  if (!csrf) await api("/auth/session");
  const response = await fetch("/api/v1/tutor/stream", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-TOKEN": csrf },
    body: JSON.stringify(body),
    signal,
  });
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ message: "The tutor is temporarily unavailable." }));
    throw new ApiError(error.message, response.status);
  }
  const reader = response.body?.getReader();
  if (!reader) throw new Error("The answer stream was unavailable.");
  const decoder = new TextDecoder();
  let buffer = "",
    answer = "",
    done = false;
  while (true) {
    const chunk = await reader.read();
    if (chunk.done) break;
    buffer += decoder.decode(chunk.value, { stream: true });
    let boundary: number;
    while ((boundary = buffer.indexOf("\n\n")) >= 0) {
      const event = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const name = event
        .split("\n")
        .find((line) => line.startsWith("event:"))
        ?.slice(6)
        .trim();
      const payload = event
        .split("\n")
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trim())
        .join("\n");
      if (!payload) continue;
      const data = JSON.parse(payload);
      if (name === "error")
        throw new Error(data.message ?? "The tutor was interrupted.");
      if (name === "token") {
        answer += data.text;
        onToken(answer);
      }
      if (name === "done") done = true;
    }
  }
  if (!done) throw new Error("The answer was interrupted. Please try again.");
  return answer;
}
export function download(name: string, value: unknown) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(
    new Blob([JSON.stringify(value, null, 2)], { type: "application/json" }),
  );
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}
/** A file upload (multipart) with the same session, CSRF and error handling as api(). */
export async function upload<T>(path: string, file: File): Promise<T> {
  if (!csrf) await api("/auth/session");
  const body = new FormData();
  body.append("file", file);
  const r = await fetch("/api/v1" + path, {
    method: "POST",
    credentials: "include",
    headers: csrf ? { "X-CSRF-TOKEN": csrf } : {},
    body,
  });
  const data = await r.json().catch(() => ({
    message: "The server could not be reached. Check the connection and retry.",
  }));
  if (!r.ok) {
    if (r.status === 403) csrf = "";
    throw new ApiError(data.message ?? "The upload could not be completed.", r.status);
  }
  return data;
}
