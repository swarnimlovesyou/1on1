import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { MagnifyingGlass } from "@phosphor-icons/react";
import { api } from "../../api";
import { Loading, ErrorState } from "../../components/Shared";
import { BANK_CREDIT } from "./QuestionBank";

/** Company lists open the question bank filtered to that company. Community-reported, never "asked at". */
export default function Companies() {
  const [q, setQ] = useState("");
  const companies = useQuery({
    queryKey: ["bank-companies"],
    queryFn: () => api<{ name: string; count: number }[]>("/bank/companies"),
    staleTime: Infinity,
  });
  if (companies.isLoading) return <Loading />;
  if (companies.error) return <ErrorState error={companies.error} />;
  const rows = companies.data!.filter((c) => c.name.toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="companies">
      <p className="muted">
        Community-reported (LeetCode company tags, 2022 snapshot). These are questions people reported seeing, not
        confirmed interview content.
      </p>
      <div className="practice-filters">
        <div className="search-field">
          <MagnifyingGlass size={17} />
          <input aria-label="Search companies" placeholder="Find a company…" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
      </div>
      <div className="company-grid">
        {rows.map((c) => (
          <Link key={c.name} to={"/practice?tab=bank&company=" + encodeURIComponent(c.name)} className="company-card">
            <strong>{c.name}</strong>
            <small>{c.count} questions</small>
          </Link>
        ))}
      </div>
      <p className="muted bank-credit">{BANK_CREDIT}</p>
    </div>
  );
}
