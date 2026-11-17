import { useQuery } from "@tanstack/react-query";
import { api } from "../../api";
import type { PrepGuideSummary, PrepTrack } from "../../types";

export function usePrep() {
  return useQuery({
    queryKey: ["prep"],
    queryFn: () => api<{ tracks: PrepTrack[]; guides: PrepGuideSummary[] }>("/prep"),
    staleTime: 60_000,
  });
}
