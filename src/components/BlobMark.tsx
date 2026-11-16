export type BlobState = "idle" | "thinking" | "answered" | "error" | "offline";

const label: Record<BlobState, string> = {
  idle: "Ready",
  thinking: "Thinking",
  answered: "Answered",
  error: "Something went wrong",
  offline: "AI tutor unavailable",
};

/** The Blob: a small companion whose posture reflects what the tutor is doing. Motion is decorative only. */
export default function BlobMark({
  state = "idle",
  size = 41,
}: {
  state?: BlobState;
  size?: number;
}) {
  return (
    <span
      className={"blob-mark " + state}
      style={{ width: size, height: size }}
      role="img"
      aria-label={"1on1 tutor: " + label[state]}
    >
      <svg viewBox="0 0 40 40" aria-hidden="true">
        <path
          className="blob-body"
          d="M20 5c8.5 0 15 5.6 15 14.2C35 28 28.6 35 20 35S5 28.6 5 19.6C5 11 11.5 5 20 5z"
        />
        <g className="blob-eyes">
          <ellipse cx="15" cy="18.5" rx="1.9" ry="2.4" />
          <ellipse cx="25" cy="18.5" rx="1.9" ry="2.4" />
        </g>
        <path className="blob-mouth" d="M16.5 25c2 1.6 5 1.6 7 0" />
      </svg>
    </span>
  );
}
