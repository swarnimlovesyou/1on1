import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api";
import { ErrorState } from "../../components/Shared";

type Pairing = { id: string; label: string; createdAt: string; lastUsedAt?: string };

/** Lets a learner give one external assistant (through the MCP adapter) read access to their study context and notes. */
export default function AssistantPairing() {
  const qc = useQueryClient();
  const [label, setLabel] = useState("Claude Desktop");
  const pairings = useQuery({ queryKey: ["pairings"], queryFn: () => api<Pairing[]>("/pairing") });
  const create = useMutation({
    mutationFn: () => api<{ token: string; label: string }>("/pairing", { label }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pairings"] }),
  });
  const revoke = useMutation({
    mutationFn: (id: string) => api(`/pairing/${id}`, undefined, "DELETE"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pairings"] }),
  });
  const config = create.data && JSON.stringify({ mcpServers: { "1on1": { command: "node", args: ["<path to 1on1>/mcp/server.mjs"], env: { ONEONONE_TOKEN: create.data.token } } } }, null, 2);
  return (
    <section className="assistant-pairing">
      <h2>Connect an assistant</h2>
      <p className="form-note">
        An assistant such as Claude Desktop can read your next step, reviews due and notes, search the sources you uploaded, and save notes for you. It cannot grade, change your account or see anyone else. Revoke it here at any time.
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          create.mutate();
        }}
      >
        <label>
          Assistant or device
          <input value={label} maxLength={60} required onChange={(e) => setLabel(e.target.value)} />
        </label>
        <button className="button primary small" disabled={create.isPending}>
          Make a token
        </button>
      </form>
      {create.error && <ErrorState error={create.error} />}
      {config && (
        <div className="pairing-token" role="status">
          <p>
            <strong>Copy this now; it won't be shown again.</strong> Add it to your assistant's MCP settings:
          </p>
          <pre>{config}</pre>
          <button className="button small" type="button" onClick={() => navigator.clipboard?.writeText(config)}>
            Copy settings
          </button>
        </div>
      )}
      {!!pairings.data?.length && (
        <ul className="pairing-list">
          {pairings.data.map((p) => (
            <li key={p.id}>
              <span>
                <strong>{p.label}</strong>
                <small>{p.lastUsedAt ? "Last used " + new Date(p.lastUsedAt).toLocaleString() : "Not used yet"}</small>
              </span>
              <button className="button small" type="button" disabled={revoke.isPending} onClick={() => revoke.mutate(p.id)} aria-label={`Revoke ${p.label}`}>
                Revoke
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
