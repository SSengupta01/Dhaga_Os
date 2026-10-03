"use client";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Check, Clock3, Play, ShieldAlert, Sparkles } from "lucide-react";
import { api, Meta, Run, Ticket } from "@/lib/api";
import type { components } from "@/lib/openapi.generated";
import { Card, EmptyState, ErrorState, PageTitle, Pill, Stat } from "@/components/ui";

type TicketDetail = { ticket: Ticket; run: Run | null };
const tone = (decision: string) => decision === "simulated_sent" || decision === "simulated_approved" ? "good" : decision === "escalate" || decision === "human_escalated" ? "bad" : "warn";
const label = (text: string) => text.replaceAll("_", " ");

export default function CXPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [detail, setDetail] = useState<TicketDetail | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [editedReply, setEditedReply] = useState("");
  const loadTickets = useCallback(async (all: boolean) => { const result = await api<{items: Ticket[]}>(`/cx/tickets?limit=${all ? 100 : 40}${all ? "" : "&scenario_only=true"}`); setTickets(result.items); setSelected(s => s || result.items[0]?.id || ""); }, []);
  useEffect(() => { loadTickets(showAll).catch(e => setError(e.message)); }, [loadTickets, showAll]);
  useEffect(() => { api<Meta>("/meta").then(setMeta).catch(() => {}); }, []);
  useEffect(() => { if (selected) api<TicketDetail>(`/cx/tickets/${selected}`).then(v => { setDetail(v); setEditedReply(v.run?.proposed_reply || ""); }).catch(e => setError(e.message)); }, [selected]);
  async function run() { if (!selected) return; setBusy(true); setError(""); try { await api<Run>(`/cx/tickets/${selected}/run`, { method: "POST" }); const result = await api<TicketDetail>(`/cx/tickets/${selected}`); setDetail(result); setEditedReply(result.run?.proposed_reply || ""); } catch (e) { setError((e as Error).message); } finally { setBusy(false); } }
  async function decide(action: "approve" | "edit" | "escalate") { if (!detail?.run) return; setBusy(true); setError(""); try { const payload: components["schemas"]["DecisionInput"] = { action, actor: "Demo Agent", edited_reply: action === "edit" ? editedReply : undefined }; await api<Run>(`/cx/runs/${detail.run.id}/decision`, { method: "POST", body: JSON.stringify(payload) }); setDetail(await api<TicketDetail>(`/cx/tickets/${selected}`)); } catch (e) { setError((e as Error).message); } finally { setBusy(false); } }
  const runData = detail?.run;
  const policy = meta?.policies.find(p => p.id === runData?.policy_id);
  return <div className="page-wrap">
    <PageTitle eyebrow="CUSTOMER EXPERIENCE / 02" title="CX Support" subtitle="A multi-intent agent workspace for verified answers and human-approved actions." right={<Pill tone="blue">Mock integrations · Synthetic cases</Pill>} />
    <div className="notice"><ShieldAlert size={19} /><div><strong>Decision boundary:</strong> read-only verified replies may be simulated as sent. Returns, exchanges, refunds, cancellations, and compensation need an agent. No real customer message or order change occurs.</div></div>
    {error && <ErrorState message={error} />}
    <div className="cx-grid"><Card className="queue-card"><div className="queue-header"><div><h2>Case queue</h2><p>Choose a scenario to inspect the agent&apos;s reasoning.</p></div><button className="text-button" onClick={() => setShowAll(!showAll)}>{showAll ? "Show scenarios" : "Browse 100 cases"}</button></div>
      <div className="queue-list">{tickets.map(t => <button key={t.id} onClick={() => setSelected(t.id)} className={`queue-item ${selected === t.id ? "selected" : ""}`}><div className="queue-top"><strong>{t.scenario ? label(t.scenario) : t.id}</strong><span>{t.channel === "FRESHDESK" ? "Ticket" : "WhatsApp"}</span></div><p>{t.message}</p><small>{t.id} · {t.language}</small></button>)}</div></Card>
      <div className="case-stack">{!detail ? <Card><EmptyState>Select a case from the queue.</EmptyState></Card> : <>
        <Card className="case-card"><div className="case-title"><div><span className="mini-label">CASE {detail.ticket.id} · {detail.ticket.channel}</span><h2>{detail.ticket.scenario ? label(detail.ticket.scenario) : "Customer request"}</h2></div><Pill tone="neutral">{detail.ticket.language}</Pill></div>
          <div className="message-bubble"><span>CUSTOMER MESSAGE</span><p>{detail.ticket.message}</p></div>
          <div className="case-meta"><div><span>CUSTOMER</span><strong>{detail.ticket.customer_id}</strong></div><div><span>LINKED ORDER</span><strong>{detail.ticket.order_id || "Missing"}</strong></div><div><span>SOURCE</span><strong>{detail.ticket.channel === "FRESHDESK" ? "Freshdesk-like" : "Gupshup-like"}</strong></div></div>
          {!runData ? <button className="primary-button" disabled={busy} onClick={run}><Play size={16} fill="currentColor" /> {busy ? "Running…" : "Run support agent"}</button> : <div className="result-panel"><div className="result-head"><div><Sparkles size={18} /><strong>Agent proposal</strong></div><Pill tone={tone(runData.decision)}>{label(runData.decision)}</Pill></div><div className="result-metrics"><span>Intent <strong>{label(runData.intent)}</strong></span><span>Action <strong>{runData.proposed_action ? label(runData.proposed_action) : "None"}</strong></span></div><p className="reply">{runData.proposed_reply}</p>{runData.reason_codes.length > 0 && <div className="reason-list">{runData.reason_codes.map(r => <Pill key={r} tone="bad">{r}</Pill>)}</div>}
            {(runData.decision === "approval_required" || runData.decision === "escalate") && <div className="decision-area"><textarea aria-label="Edit proposed reply" value={editedReply} onChange={e => setEditedReply(e.target.value)} /><div className="action-row"><button disabled={busy || !runData.proposed_action} onClick={() => decide("approve")} className="primary-button"><Check size={16} /> Approve action</button><button disabled={busy} onClick={() => decide("edit")} className="secondary-button">Save edited reply</button><button disabled={busy} onClick={() => decide("escalate")} className="secondary-button">Escalate</button></div><small>Demo decisions are audited. Approval simulates the action; it never contacts a customer or live system.</small></div>}</div>}
        </Card>
        {runData && <><Card title="Facts and policy" subtitle="Why this decision was made"><div className="facts-grid">{Object.entries(runData.verified_facts).map(([key, value]) => <div key={key}><span>{label(key)}</span><strong>{String(value ?? "Unknown")}</strong></div>)}</div><div className="policy-box"><span>POLICY · {meta?.policy_version}</span><strong>{policy?.label || "No supported policy"}</strong><p>{policy?.text || "The agent abstained because the available policy does not cover this case."}</p><small>{meta?.policy_disclaimer}</small></div></Card>
        <Card title="Execution trace" subtitle="Code, model, mocks, and guardrails"><div className="trace-list">{runData.trace.map((step, i) => <div className="trace-row" key={i}><span className="trace-index">{String(i + 1).padStart(2, "0")}</span><div><strong>{label(String(step.stage || step.role || "model call"))}</strong><small>{step.kind || step.model || "LangChain"}</small></div><Pill tone={step.result === "blocked" || step.status === "failed" ? "bad" : "neutral"}>{String(step.result || step.status || "done")}</Pill></div>)}</div><div className="trace-foot"><Clock3 size={15} /> Model calls and latency are recorded in each step when a live model is configured.</div></Card></>}
      </>}</div></div>
  </div>;
}
