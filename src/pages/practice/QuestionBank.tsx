import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, MagnifyingGlass } from "@phosphor-icons/react";
import { api } from "../../api";
import CompanyTags from "../../components/CompanyTags";
import type { BankPage } from "../../types";
import { Loading, ErrorState } from "../../components/Shared";
import FamilyMark from "../../components/FamilyMark";
import { familyOfProblem } from "../../families";

export const BANK_CREDIT =
  "Titles and links only, never statements: Codeforces (official API), AtCoder (via AtCoder Problems), CSES and LeetCode. Pattern tags: NeetCode (MIT © 2022 neetcode-gh). Company lists: community-reported LeetCode tags, data as of May 2022 (MIT © 2022 Huan Xu).";

const SIZE = 25;

/** Our problems plus external question metadata; external rows open on their own site. */
export default function QuestionBank() {
  const [params, setParams] = useSearchParams();
  const company = params.get("company") ?? "";
  const q = params.get("q") ?? "",
    source = params.get("source") ?? "",
    difficulty = params.get("difficulty") ?? "",
    topic = params.get("topic") ?? "",
    sort = params.get("sort") ?? "",
    page = Number(params.get("page") ?? 0) || 0;
  // build from the URL as it is now, so a filter chosen while a search is pending is never lost
  // the router's updater can hand back a stale copy when two updates land together, so read the address bar
  const set = (key: string, value: string) => {
    const next = new URLSearchParams(window.location.search);
    if (value) next.set(key, value);
    else next.delete(key);
    if (key !== "page") next.delete("page");
    setParams(next, { replace: true });
  };
  const [typed, setTyped] = useState(q);
  const sent = useRef(q);
  // back and forward change q without typing; our own debounced writes must not overwrite newer keystrokes
  useEffect(() => {
    if (q !== sent.current) {
      sent.current = q;
      setTyped(q);
    }
  }, [q]);
  // search once typing pauses, not on every keystroke
  useEffect(() => {
    if (typed === q) return;
    const t = setTimeout(() => {
      sent.current = typed;
      set("q", typed);
    }, 250);
    return () => clearTimeout(t);
  }, [typed]);
  const topics = useQuery({ queryKey: ["bank-topics"], queryFn: () => api<string[]>("/bank/topics"), staleTime: Infinity });
  const query = new URLSearchParams({ q, source, difficulty, topic, company, sort, page: String(page), size: String(SIZE) });
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
          <option>AtCoder</option>
          <option>CSES</option>
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
        <select aria-label="Sort" value={sort} onChange={(e) => set("sort", e.target.value)}>
          <option value="">{company ? "Most reported" : "Suggested order"}</option>
          <option value="easiest">Easiest first</option>
          <option value="hardest">Hardest first</option>
          <option value="title">A to Z</option>
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
                  <tr key={item.id} className="bank-row">
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
                      <CompanyTags companies={item.companies} />
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
