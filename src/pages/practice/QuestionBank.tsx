import { useState } from "react";
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
  const [q, setQ] = useState(""),
    [source, setSource] = useState(""),
    [difficulty, setDifficulty] = useState(""),
    [page, setPage] = useState(0);
  const query = new URLSearchParams({ q, source, difficulty, company, page: String(page), size: String(SIZE) });
  const bank = useQuery({
    queryKey: ["bank", query.toString()],
    queryFn: () => api<BankPage>("/bank?" + query),
    placeholderData: (previous) => previous,
  });
  const reset = <T,>(set: (v: T) => void) => (v: T) => {
    set(v);
    setPage(0);
  };
  const pages = bank.data ? Math.max(1, Math.ceil(bank.data.total / SIZE)) : 1;
  return (
    <div className="question-bank">
      <div className="practice-filters">
        <div className="search-field">
          <MagnifyingGlass size={17} />
          <input aria-label="Search the question bank" placeholder="Find a question…" value={q} onChange={(e) => reset(setQ)(e.target.value)} />
        </div>
        <select aria-label="Source" value={source} onChange={(e) => reset(setSource)(e.target.value)}>
          <option value="">All sources</option>
          <option value="1on1">1on1 (solve here)</option>
          <option>Codeforces</option>
          <option>LeetCode</option>
        </select>
        <select aria-label="Difficulty" value={difficulty} onChange={(e) => reset(setDifficulty)(e.target.value)}>
          <option value="">All difficulties</option>
          {["Easy", "Medium", "Hard"].map((d) => (
            <option key={d}>{d}</option>
          ))}
        </select>
        {company && (
          <button
            className="button secondary small"
            onClick={() => {
              params.delete("company");
              setParams(params);
              setPage(0);
            }}
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
                        <a href={item.url} target="_blank" rel="noopener noreferrer">
                          {item.title} <ArrowUpRight size={13} aria-label="opens on the original site" />
                        </a>
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
                          {item.tags.slice(0, 3).map((t) => (
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
            <button className="button secondary small" disabled={page === 0} onClick={() => setPage(page - 1)}>
              Previous
            </button>
            <span>
              Page {page + 1} of {pages.toLocaleString()}
            </span>
            <button className="button secondary small" disabled={page + 1 >= pages} onClick={() => setPage(page + 1)}>
              Next
            </button>
          </div>
        </>
      )}
      <p className="muted bank-credit">{BANK_CREDIT}</p>
    </div>
  );
}
