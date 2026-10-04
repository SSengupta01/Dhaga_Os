"use client";

import { useState } from "react";
import { ArrowUpRight, Check, CheckCheck, ChevronDown, Clock3, FileText, Pencil, Play, ShieldCheck, ShieldAlert, Sparkles } from "lucide-react";
import type { Meta } from "@/lib/api";
import { Card, EmptyState, Pill } from "@/components/ui";
import { AuditEntry, TicketDetail, decisionLabel, decisionTone, formatDate, readable } from "./types";

type Decision = "approve" | "edit" | "escalate";
type Props = { detail: TicketDetail; meta: Meta | null; busy: boolean; editedReply: string; setEditedReply: (value: string) => void; onRun: () => void; onDecide: (action: Decision) => void; onWorkflow: () => void; audit: AuditEntry[] };
const approvable = new Set(["create_return_request", "create_exchange_request", "create_refund_request", "create_cancellation_request"]);

export function Conversation({ detail, busy, editedReply, setEditedReply, onRun, onDecide, onWorkflow, audit }: Props) {
  const [editing, setEditing] = useState(false);
  const { ticket, run } = detail;
  const canApprove = !!run && run.decision === "approval_required" && approvable.has(run.proposed_action || "") && run.reason_codes.length === 0;
  const canEdit = run?.decision === "approval_required";
  const canEscalate = run?.decision === "approval_required" || run?.decision === "escalate";
  const messages = ticket.messages?.length ? ticket.messages : [{ sender: "customer", text: ticket.message, at: ticket.created_at }];
  return <Card className="cx-conversation">
    <div className="cx-contact-header"><span className="cx-avatar">{(ticket.customer_name || ticket.customer_id).slice(0, 2).toUpperCase()}</span><div><h2>{ticket.customer_name || ticket.customer_id}</h2><p>{ticket.id} <span>·</span> {ticket.channel === "FRESHDESK" ? "Freshdesk" : "WhatsApp"}</p></div><Pill tone={decisionTone(run?.decision)}>{decisionLabel(run?.decision)}</Pill></div>
    <div className="cx-chat-history"><div className="cx-chat-date">{formatDate(ticket.created_at)} IST · {ticket.language}</div>{messages.map((message, index) => <div className={`cx-message ${message.sender === "customer" ? "customer" : "agent"}`} key={`${message.at}-${index}`}><span>{message.sender === "customer" ? "Customer" : readable(message.sender)}</span><p>{message.text}</p><small>{formatDate(message.at)} IST</small></div>)}</div>
    {!run ? <div className="cx-ready-state"><span className="cx-icon-tile"><Sparkles size={22} /></span><h3>Ready to investigate</h3><p>The agent will verify ownership, retrieve facts, and apply the relevant demo policy.</p><button className="primary-button" disabled={busy} onClick={onRun}><Play size={16} />{busy ? "Investigating case…" : "Run support agent"}</button></div> : <div className="cx-proposal">
      <div className="cx-section-heading"><h3><Sparkles size={16} /> Agent response</h3><button className="text-button" onClick={onWorkflow}>View workflow <ArrowUpRight size={14} /></button></div>
      <div className="cx-proposal-meta"><Pill tone="blue">{readable(run.intent).toUpperCase()}</Pill>{run.proposed_action && <span>{readable(run.proposed_action)}</span>}</div>
      <p className="cx-proposed-text">{run.proposed_reply}</p>
      {run.reason_codes.length > 0 && <div className="cx-blocker"><ShieldAlert size={17} /><div><strong>{run.decision === "escalate" ? "Human investigation required" : "Review required"}</strong>{run.reason_codes.map(reason => <span key={reason}>{readable(reason).toLowerCase()}</span>)}</div></div>}
      {(canEscalate || canEdit) && <><div className="cx-decision-actions"><button className="primary-button" disabled={busy || !canApprove} onClick={() => onDecide("approve")} title={!canApprove ? "This case has no action that can be approved under the available facts and policy." : "Simulate this approved action"}><Check size={16} />Approve action</button><button className="secondary-button" disabled={busy || !canEdit} onClick={() => setEditing(!editing)}><Pencil size={15} />Edit reply</button><button className="secondary-button" disabled={busy || !canEscalate} onClick={() => onDecide("escalate")}>Escalate</button></div>{editing && canEdit && <div className="cx-edit-reply"><label htmlFor="cx-edited-reply">Reviewed reply</label><textarea id="cx-edited-reply" value={editedReply} onChange={event => setEditedReply(event.target.value)} rows={5} /><button className="primary-button" disabled={busy || !editedReply.trim()} onClick={() => onDecide("edit")}>Save reviewed reply</button><small>Saving records a human-edited reply. It does not approve an order action.</small></div>}<p className="cx-safe-note"><ShieldCheck size={14} />All decisions are simulated and recorded in the audit trail.</p></>}
      {!canEscalate && <div className="cx-completion"><CheckCheck size={17} /><span>{decisionLabel(run.decision)} · No live customer or order was changed.</span></div>}
    </div>}
    {audit.length > 0 && <details className="cx-audit"><summary><Clock3 size={15} /> Decision history <span>{audit.length}</span><ChevronDown size={14} /></summary><ol>{audit.map((entry, index) => <li key={`${entry.at}-${index}`}><strong>{readable(entry.action)} · {entry.actor}</strong><span>{decisionLabel(entry.before)} → {decisionLabel(entry.after)}</span><small>{formatDate(entry.at)} IST</small></li>)}</ol></details>}
  </Card>;
}

function FactValue({ value }: { value: unknown }) { return <>{typeof value === "boolean" ? value ? "Yes" : "No" : value === null || value === undefined ? "Unavailable" : typeof value === "object" ? JSON.stringify(value) : String(value)}</>; }

export function Evidence({ detail, meta }: Pick<Props, "detail" | "meta">) {
  const run = detail.run;
  const policy = meta?.policies.find(item => item.id === run?.policy_id);
  const classification = run?.trace.find(step => step.stage === "classification");
  const modelClassified = classification?.kind === "model";
  const confidence = modelClassified && typeof classification?.confidence === "number" ? classification.confidence : null;
  return <div className="cx-evidence">
    <Card className="cx-interpretation"><div className="cx-section-heading"><h3><Sparkles size={16} /> Interpretation</h3>{run && <Pill tone="blue">{modelClassified ? "Model" : "Rules"}</Pill>}</div>{!run ? <EmptyState>Run the agent to see intent and decision evidence.</EmptyState> : <><dl className="cx-fact-list"><div><dt>Detected intent</dt><dd>{readable(run.intent)}</dd></div><div><dt>Language</dt><dd>{detail.ticket.language}</dd></div><div><dt>Decision</dt><dd>{decisionLabel(run.decision)}</dd></div>{confidence !== null && <div><dt>Model confidence</dt><dd>{Math.round(confidence * 100)}%</dd></div>}</dl>{confidence !== null && <div className="cx-confidence-meter" role="meter" aria-label="Classifier confidence" aria-valuenow={Math.round(confidence * 100)} aria-valuemin={0} aria-valuemax={100}><span style={{ width: `${confidence * 100}%` }} /></div>}{!modelClassified && <p className="cx-panel-caption">{classification ? "Deterministic classification; no model confidence measurement." : "The case stopped before classification."}</p>}</>}</Card>
    <Card><div className="cx-section-heading"><h3><ShieldCheck size={16} /> Retrieved facts</h3><Pill tone="good">Demo data</Pill></div>{!run ? <EmptyState>Commerce facts will appear after verification.</EmptyState> : <dl className="cx-fact-list">{Object.entries(run.verified_facts).filter(([key]) => key !== "source").map(([key, value]) => <div key={key}><dt>{readable(key)}</dt><dd><FactValue value={value} /></dd></div>)}</dl>}</Card>
    <Card className="cx-policy-card"><div className="cx-section-heading"><h3><FileText size={16} /> Demo data and rules</h3></div><Pill tone="warn">Illustrative demo policy</Pill><h4>{policy?.label || (run ? "No supported policy" : "Policy selected after investigation")}</h4><p>{policy?.text || (run ? "Available facts or policy could not support this request. Inspect the reason in the agent response." : "Eligibility is decided in code from the facts retrieved for this case.")}</p>{policy && <dl className="cx-fact-list"><div><dt>Policy ID</dt><dd>{policy.id}</dd></div><div><dt>Human approval</dt><dd>{policy.approval_required ? "Required" : "Read-only response"}</dd></div></dl>}<details><summary>Policy and data provenance <ChevronDown size={14} /></summary><p>{meta?.policy_disclaimer || "Synthetic records and illustrative rules support this demo."}</p><p>Seed: {meta?.seed_version || "Loading…"}<br />Policy pack: {meta?.policy_version || "Loading…"}</p>{policy && <p>Required facts: {policy.required_facts.map(readable).join(", ")}</p>}</details></Card>
  </div>;
}
