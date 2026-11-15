import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import {
  Sparkle,
  ArrowUp,
  X,
  BookmarkSimple,
  ArrowRight,
} from "@phosphor-icons/react";
import { useMutation } from "@tanstack/react-query";
import { api, streamTutor } from "../api";
import type { Scene } from "../types";
import { useApp } from "../context";
import { useNavigate } from "react-router-dom";
export default function Tutor({
  lesson,
  experiment,
  step = 0,
  code,
  submission,
  onScene,
}: {
  lesson?: string;
  experiment?: Scene;
  step?: number;
  code?: string;
  submission?: string;
  onScene?: (s: Scene) => void;
}) {
  const { notify, user, reload } = useApp();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false),
    [draftAnswer, setDraftAnswer] = useState(""),
    [text, setText] = useState(""),
    [mode, setMode] = useState("explain"),
    [messages, setMessages] = useState<
      { role: string; text: string; scene?: Scene }[]
    >([]);
  const mutation = useMutation({
    mutationFn: async (message: string) => {
      const request = {
        message,
        mode,
        lesson,
        experiment,
        step,
        code,
        submission,
        history: messages
          .slice(-8)
          .map((m) => ({ role: m.role, text: m.text.slice(0, 1500) })),
      };
      if (mode === "visualize")
        return api<{ text: string; scene?: Scene }>("/tutor", request);
      const answer = await streamTutor(request, setDraftAnswer);
      return { text: answer };
    },
    onSuccess: (data) => {
      setDraftAnswer("");
      setMessages((m) => [...m, { role: "tutor", ...data }]);
    },
  });
  const send = (message: string) => {
    if (!message.trim() || mutation.isPending || !user) return;
    setDraftAnswer("");
    setMessages((m) => [...m, { role: "you", text: message }]);
    setText("");
    mutation.mutate(message);
  };
  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <button className="button tutor-button">
          <Sparkle size={18} weight="duotone" />
          Ask 1on1
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="overlay" />
        <Dialog.Content className="tutor-drawer">
          <div className="drawer-heading">
            <span className="tutor-mark">
              <Sparkle size={23} weight="duotone" />
            </span>
            <div>
              <Dialog.Title>Your thinking partner.</Dialog.Title>
              <Dialog.Description>
                A little guidance, right where you need it.
              </Dialog.Description>
            </div>
            <Dialog.Close className="icon-btn" aria-label="Close tutor">
              <X size={20} />
            </Dialog.Close>
          </div>
          <div className="tutor-modes">
            <button
              className={mode === "explain" ? "active" : ""}
              onClick={() => setMode("explain")}
            >
              Talk it through
            </button>
            <button
              className={mode === "visualize" ? "active" : ""}
              onClick={() => setMode("visualize")}
            >
              Visualize an idea
            </button>
          </div>
          <div className="chat-messages">
            {!messages.length && (
              <div className="tutor-welcome">
                <h3>You don’t have to figure it out alone.</h3>
                <p>
                  I can explain the step you’re looking at, help you find a bug,
                  or turn a concept into an experiment.
                </p>
                {[
                  "Explain the current step in simpler terms",
                  "Give me a hint without the solution",
                  "What edge case am I missing?",
                ].map((s) => (
                  <button key={s} onClick={() => send(s)} disabled={!user}>
                    {s}
                    <ArrowRight size={16} />
                  </button>
                ))}
                {!user && (
                  <p className="inline-alert">Sign in to use your tutor.</p>
                )}
              </div>
            )}
            {messages.map((m, i) => (
              <div className={"chat-message " + m.role} key={i}>
                <small>{m.role === "you" ? "You" : "1on1 · Gemini"}</small>
                <div className="chat-text">{m.text}</div>
                {m.scene && (
                  <button
                    className="button secondary small"
                    onClick={() => {
                      if (onScene && lesson === "lesson-" + m.scene!.algorithm)
                        onScene(m.scene!);
                      else
                        navigate(
                          "/learn/lesson-" +
                            m.scene!.algorithm +
                            "?scene=" +
                            encodeURIComponent(JSON.stringify(m.scene)),
                        );
                      setOpen(false);
                    }}
                  >
                    Open experiment <ArrowRight size={15} />
                  </button>
                )}
                {m.role === "tutor" && (
                  <button
                    className="save-answer"
                    onClick={async () => {
                      try {
                        await api("/notes", {
                          title: "A note from 1on1",
                          text: m.text,
                          lesson: lesson ?? "",
                          ...(m.scene ? { experiment: m.scene } : {}),
                        });
                        reload();
                        notify("Explanation saved to your notebook");
                      } catch (e) {
                        notify((e as Error).message);
                      }
                    }}
                  >
                    <BookmarkSimple size={14} />
                    Save to notebook
                  </button>
                )}
              </div>
            ))}
            {!!draftAnswer && (
              <div className="chat-message tutor">
                <small>1on1 · Gemini</small>
                <div className="chat-text">{draftAnswer}</div>
              </div>
            )}
            {mutation.isPending && !draftAnswer && (
              <p className="thinking" role="status">
                Thinking through the idea<span>…</span>
              </p>
            )}
            {mutation.isError && (
              <p className="inline-alert" role="alert">
                {mutation.error.message}
              </p>
            )}
          </div>
          <form
            className="tutor-compose"
            onSubmit={(e) => {
              e.preventDefault();
              send(text);
            }}
          >
            <label className="sr-only" htmlFor="tutor-question">
              Ask your tutor
            </label>
            <textarea
              id="tutor-question"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={
                mode === "visualize"
                  ? "Try “show binary search for 7 in 1, 3, 5, 7, 9”"
                  : "What would you like to understand?"
              }
              maxLength={8000}
            />
            <button
              className="send-button"
              aria-label="Send question"
              disabled={!text.trim() || mutation.isPending || !user}
            >
              <ArrowUp size={20} />
            </button>
          </form>
          <p className="tutor-footnote">
            AI guidance can be imperfect. The experiment’s steps are computed in
            Java.
          </p>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
