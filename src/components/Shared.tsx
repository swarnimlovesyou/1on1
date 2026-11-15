import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  ArrowClockwise,
  WarningCircle,
  BookmarkSimple,
} from "@phosphor-icons/react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../api";
import { useApp } from "../context";
export function Loading() {
  return (
    <div className="loading" role="status" aria-label="Loading">
      <div className="skeleton wide" />
      <div className="skeleton" />
      <div className="skeleton panel" />
      <span className="sr-only">Loading your workspace</span>
    </div>
  );
}
export function ErrorState({
  error,
  retry,
}: {
  error: unknown;
  retry?: () => void;
}) {
  return (
    <div className="error-state" role="alert">
      <WarningCircle size={22} />
      <div>
        <strong>We couldn’t finish that.</strong>
        <p>{error instanceof Error ? error.message : "Please try again."}</p>
        {retry && (
          <button className="button secondary small" onClick={retry}>
            <ArrowClockwise size={16} />
            Try again
          </button>
        )}
      </div>
    </div>
  );
}
export function PageHeading({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}
export function Gate({ children }: { children: ReactNode }) {
  const { user } = useApp();
  return user ? (
    <>{children}</>
  ) : (
    <div className="empty sign-in-empty">
      <span className="empty-symbol">1:1</span>
      <h2>Make this space yours.</h2>
      <p>
        Save your notes, build a practice plan, and pick up exactly where you
        left off.
      </p>
      <Link to="/signup" className="button primary">
        Create your account <ArrowRight size={17} />
      </Link>
      <Link to="/login" className="text-link">
        Already learning here? Sign in
      </Link>
    </div>
  );
}
export function Bookmark({ id }: { id: string }) {
  const { user, progress, reload, notify } = useApp();
  const selected = progress.bookmarks.includes(id);
  const mutation = useMutation({
    mutationFn: () =>
      api("/progress", {
        bookmarks: selected
          ? progress.bookmarks.filter((x) => x !== id)
          : [...progress.bookmarks, id],
      }),
    onSuccess: () => {
      reload();
      notify(selected ? "Bookmark removed" : "Saved to your notebook");
    },
    onError: (e) => notify(e.message),
  });
  return (
    <button
      className={"icon-btn " + (selected ? "selected" : "")}
      aria-label={selected ? "Remove bookmark" : "Bookmark for later"}
      aria-pressed={selected}
      onClick={() =>
        user
          ? mutation.mutate()
          : notify("Sign in to save this to your notebook.")
      }
      disabled={mutation.isPending}
    >
      <BookmarkSimple size={20} weight={selected ? "fill" : "regular"} />
    </button>
  );
}
