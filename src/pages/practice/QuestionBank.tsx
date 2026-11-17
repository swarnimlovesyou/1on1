import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, MagnifyingGlass } from "@phosphor-icons/react";
import { api } from "../../api";
import type { BankPage } from "../../types";
import { Loading, ErrorState } from "../../components/Shared";
import FamilyMark from "../../components/FamilyMark";
import { familyOfProblem } from "../../families";

export const BANK_CREDIT =
  "Questions from Codeforces and LeetCode, metadata only. Company lists: community-reported (LeetCode company tags, 2022 snapshot), MIT © 2022 Huan Xu.";

const SIZE = 25;

/** Our problems plus external question metadata; external rows open on their own site. */
export default function QuestionBank() {
  const [params, setParams] = useSearchParams();
  const company = params.get("company") ?? "";
  const q = params.get("q") ?? "",
    source = params.get("source") ?? "",
    difficulty = params.get("difficulty") ?? "",
    topic = params.get("topic") ?? "",
    page = Number(params.get("page") ?? 0) || 0;
  const set = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    if (key !== "page") next.delete("page");
    setParams(next, { replace: true });
  };
  const [typed, setTyped] = useState(q);
  // search once typing pauses, not on every keystroke
  useEffect(() => {
    if (typed === q) return;
    const t = setTimeout(() => set("q", typed), 250);
    return () => clearTimeout(t);
  }, [typed]);
  const topics = useQuery({ queryKey: ["bank-topics"], queryFn: () => api<string[]>("/bank/topics"), staleTime: Infinity });
  const query = new URLSearchParams({ q, source, difficulty, topic, company, page: String(page), size: String(SIZE) });
  const bank = useQuery({
    queryKey: ["bank", query.toString()],
    queryFn: () => api<BankPage>("/bank?" + query),
    placeholderData: (previous) => previous,
  });
  const pages = bank.data ? Math.max(1, Math.ceil(bank.data.total / SIZE)) : 1;
  return (
    <div className="question-bank">
      <div className="practice-filters">
        <div className="search-field">
          <MagnifyingGlass size={17} />
          <input aria-label="Search the question bank" placeholder="Find a question…" value={typed} onChange={(e) => setTyped(e.target.value)} />
        </div>
        <select aria-label="Source" value={source} onChange={(e) => set("source", e.target.value)}>
          <option value="">All sources</option>
          <option value="1on1">1on1 (solve here)</option>
          <option>Codeforces</option>
          <option>LeetCode</option>
        </select>
        <select aria-label="Difficulty" value={difficulty} onChange={(e) => set("difficulty", e.target.value)}>
          <option value="">All difficulties</option>
          {["Easy", "Medium", "Hard"].map((d) => (
            <option key={d}>{d}</option>
          ))}
        </select>
        <select aria-label="Topic" value={topic} onChange={(e) => set("topic", e.target.value)}>
          <option value="">All topics</option>
          {topics.data?.map((t) => (
            <option key={t}>{t}</option>
          ))}
        </select>
        {company && (
          <button
            className="button secondary small"
            onClick={() => set("company", "")}
          >
            {company} ×
          </button>
        )}
      </div>
      {bank.isLoading ? (
        <Loading />
      ) : bank.error ? (
        <ErrorState error={bank.error} />
      ) : (
        <>
          <p className="muted bank-count">
            {bank.data!.total.toLocaleString()} questions{company ? ` reported for ${company}` : ""}
          </p>
          <div className="table-scroll">
            <table className="problem-table bank-table">
              <thead>
                <tr>
                  <th>Question</th>
                  <th>Source</th>
                  <th>Difficulty</th>
                  <th>{company ? "Reports" : "Tags"}</th>
                </tr>
              </thead>
              <tbody>
                {bank.data!.items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <FamilyMark family={familyOfProblem(item.tags)} />
                      {item.source === "1on1" ? (
                        <Link to={item.url}>{item.title}</Link>
                      ) : (
                        <>
                          <Link to={"/practice/q/" + item.id}>{item.title}</Link>{" "}
                          <Link className="solve-here" to={"/practice/q/" + item.id}>
                            Solve here
                          </Link>{" "}
                          <a href={item.url} target="_blank" rel="noopener noreferrer" className="external-link">
                            <ArrowUpRight size={13} aria-hidden="true" />
                            <span className="sr-only">Open on {item.source}</span>
                          </a>
                        </>
                      )}
                    </td>
                    <td className="bank-source">{item.source}</td>
                    <td>
                      {item.difficulty && <span className={"difficulty " + item.difficulty.toLowerCase()}>{item.difficulty}</span>}
                    </td>
                    <td>
                      {company ? (
                        item.companies[company]
                      ) : (
                        <div className="table-tags">
                          {/* the filtered topic leads, so a match is visible even past the first three tags */}
                          {[...item.tags].sort((x, y) => Number(y === topic) - Number(x === topic)).slice(0, 3).map((t) => (
                            <span key={t}>{t}</span>
                          ))}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!bank.data!.items.length && (
            <div className="empty">
              <h2>No matching questions.</h2>
              <p>Change a filter to widen the search.</p>
            </div>
          )}
          <div className="bank-pager">
            <button className="button secondary small" disabled={page === 0} onClick={() => set("page", String(page - 1))}>
              Previous
            </button>
            <span>
              Page {page + 1} of {pages.toLocaleString()}
            </span>
            <button className="button secondary small" disabled={page + 1 >= pages} onClick={() => set("page", String(page + 1))}>
              Next
            </button>
          </div>
        </>
      )}
      <p className="muted bank-credit">{BANK_CREDIT}</p>
    </div>
  );
}
