import { useState, useEffect, useRef } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import {
  ArrowUp,
  X,
  BookmarkSimple,
  ArrowRight,
} from "@phosphor-icons/react";
import { useMutation, useQuery } from "@tanstack/react-query";
import BlobMark, { type BlobState } from "./BlobMark";
import { api, streamTutor } from "../api";
import type { Scene } from "../types";
import { useApp } from "../context";
import { useNavigate } from "react-router-dom";
export default function Tutor({
  lesson,
  problem,
  experiment,
  step = 0,
  language,
  code,
  submission,
  onScene,
}: {
  lesson?: string;
  problem?: string;
  experiment?: Scene;
  step?: number;
  language?: string;
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
    [stopped, setStopped] = useState(false),
    [historyReady, setHistoryReady] = useState(false),
    [historyError, setHistoryError] = useState(""),
    [historyRetry, setHistoryRetry] = useState(0),
    [messages, setMessages] = useState<
      { role: string; text: string; scene?: Scene }[]
    >([]);
  const contextId = lesson ?? problem ?? "workspace";
  const system = useQuery({
    queryKey: ["system"],
    queryFn: () => api<{ ai: boolean }>("/system"),
    staleTime: 60_000,
  });
  // known before the learner types, so they aren't left to discover it from an error
  const aiOff = system.data?.ai === false;
  const [level, setLevel] = useState(0);
  // questions that fit where the learner is; hint-style ones start the graduated ladder at level 1
  const suggestions: { text: string; level: number }[] = lesson
    ? [
        { text: `Explain step ${step + 1} in simpler terms`, level: 0 },
        { text: "What must stay true at this step, and why?", level: 0 },
        { text: "Give me a hint for this lesson's challenge", level: 1 },
      ]
    : problem
      ? [
          { text: "Give me a hint without the solution", level: 1 },
          submission
            ? { text: "Why might my last run have failed?", level: 1 }
            : { text: "Is my plan on the right track?", level: 0 },
          { text: "What edge case am I missing?", level: 0 },
        ]
      : [
          { text: "Explain a concept I'm stuck on", level: 0 },
          { text: "Give me a hint without the solution", level: 1 },
          { text: "What should I practise next?", level: 0 },
        ];
  const hydrated = useRef(false),
    savedConversation = useRef(""),
    abort = useRef<AbortController | undefined>(undefined);
  useEffect(() => {
    hydrated.current = false;
    setHistoryReady(false);
    setHistoryError("");
    setMessages([]);
    setDraftAnswer("");
    setStopped(false);
    const controller = new AbortController();
    if (user)
      api<{ messages: { role: string; text: string; scene?: Scene }[] }>(
        "/conversations/" + contextId,
        undefined,
        "GET",
        controller.signal,
      )
        .then((data) => {
          savedConversation.current = JSON.stringify(data.messages);
          hydrated.current = true;
          setHistoryReady(true);
          setMessages(data.messages);
        })
        .catch((error) => {
          if (!controller.signal.aborted)
            setHistoryError(
              "Your tutor history could not be loaded. " + error.message,
            );
        });
    return () => {
      controller.abort();
      abort.current?.abort();
    };
  }, [contextId, user?.id, historyRetry]);
  useEffect(() => {
    if (!user || !hydrated.current) return;
    const latest = messages.slice(-20),
      key = JSON.stringify(latest);
    if (key === savedConversation.current) return;
    const timer = setTimeout(() => {
      api("/conversations/" + contextId, { messages: latest }, "PUT")
        .then(() => {
          savedConversation.current = key;
        })
        .catch((error) =>
          notify("Your tutor history could not be saved. " + error.message),
        );
    }, 500);
    return () => clearTimeout(timer);
  }, [messages, contextId, user?.id]);
  const mutation = useMutation({
    mutationFn: async ({
      message,
      level,
    }: {
      message: string;
      level: number;
    }) => {
      const request = {
        message,
        ...(level ? { level } : {}),
        mode,
        lesson,
        experiment,
        step,
        problem,
        language,
        code,
        submission,
        history: messages
          .slice(-8)
          .map((m) => ({ role: m.role, text: m.text.slice(0, 1500) })),
      };
      const controller = new AbortController();
      abort.current = controller;
      if (mode === "visualize")
        return api<{ text: string; scene?: Scene }>(
          "/tutor",
          request,
          "POST",
          controller.signal,
        );
      const answer = await streamTutor(
        request,
        setDraftAnswer,
        controller.signal,
      );
      return { text: answer };
    },
    onSuccess: (data) => {
      setDraftAnswer("");
      setMessages((m) => [...m, { role: "tutor", ...data }]);
    },
  });
  const send = (message: string, nextLevel = 0) => {
    if (!message.trim() || mutation.isPending || !user || !historyReady || aiOff)
      return;
    setDraftAnswer("");
    setStopped(false);
    setLevel(nextLevel);
    setMessages((m) => [...m, { role: "you", text: message }]);
    setText("");
    mutation.mutate({ message, level: nextLevel });
  };
  const blob: BlobState = aiOff
    ? "offline"
    : mutation.isPending
      ? "thinking"
      : mutation.isError
        ? "error"
        : messages.at(-1)?.role === "tutor"
          ? "answered"
          : "idle";
  const lastIsAnswer = messages.at(-1)?.role === "tutor" && !mutation.isPending;
  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <button className="button tutor-button">
          <BlobMark state={blob} size={20} />
          Ask 1on1
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="overlay" />
        <Dialog.Content className="tutor-drawer">
          <div className="drawer-heading">
            <BlobMark key={blob + messages.length} state={blob} />
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
          {aiOff && (
            <p className="inline-alert tutor-offline" role="status">
              The AI tutor isn’t set up on this server, so it can’t answer
              right now. The authored hints, the Coach tab and every challenge
              still work, and your saved conversation is still here.
            </p>
          )}
          <div className="chat-messages">
            {user && !historyReady && !historyError && (
              <p role="status">Loading your conversation…</p>
            )}
            {historyError && (
              <div className="inline-alert" role="alert">
                <p>{historyError}</p>
                <button
                  className="button secondary small"
                  onClick={() => setHistoryRetry((value) => value + 1)}
                >
                  Retry conversation
                </button>
              </div>
            )}
            {!messages.length && (
              <div className="tutor-welcome">
                <h3>You don’t have to figure it out alone.</h3>
                <p>
                  I can explain the step you’re looking at, help you find a bug,
                  or turn a concept into an experiment.
                </p>
                {suggestions.map((s) => (
                  <button
                    key={s.text}
                    onClick={() => send(s.text, s.level)}
                    disabled={!user || !historyReady || aiOff}
                  >
                    {s.text}
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
                <small>{m.role === "you" ? "You" : "1on1 tutor"}</small>
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
                          ...(!lesson && problem ? { problem } : {}),
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
                <small>1on1 tutor</small>
                <div className="chat-text">{draftAnswer}</div>
              </div>
            )}
            {mutation.isPending && !draftAnswer && (
              <p className="thinking" role="status">
                Thinking through the idea<span>…</span>
              </p>
            )}
            {stopped && (
              <p className="inline-alert" role="status">
                Response stopped. You can ask another question.
              </p>
            )}
            {mutation.isError && !stopped && (
              <p className="inline-alert" role="alert">
                {mutation.error.message}
              </p>
            )}
          </div>
          {lastIsAnswer && level > 0 && level < 4 && !aiOff && (
            <button
              className="button secondary small still-stuck"
              onClick={() =>
                send("I'm still stuck. A bit more help, please.", level + 1)
              }
            >
              Still stuck? More help ({level + 1} of 4)
            </button>
          )}
          {lastIsAnswer && level === 4 && (
            <p className="tutor-footnote">
              That’s as far as hints go. Ask for the full solution if you want
              it, or try the step yourself first.
            </p>
          )}
          {!!messages.length && !mutation.isPending && !aiOff && (
            <div className="tutor-chips">
              {suggestions.map((s) => (
                <button
                  key={s.text}
                  onClick={() => send(s.text, s.level)}
                  disabled={!user || !historyReady}
                >
                  {s.text}
                </button>
              ))}
            </div>
          )}
          {mutation.isPending && (
            <button
              className="button secondary small"
              onClick={() => {
                abort.current?.abort();
                setStopped(true);
                setDraftAnswer("");
              }}
            >
              Stop response
            </button>
          )}
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
              disabled={
                !text.trim() ||
                mutation.isPending ||
                !user ||
                !historyReady ||
                aiOff
              }
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
