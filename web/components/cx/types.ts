import type { Run, Ticket } from "@/lib/api";

export type QueueTicket = Ticket & {
  customer_name?: string;
  synthetic_intent?: string;
  latest_run?: Pick<Run, "id" | "intent" | "decision" | "reason_codes" | "proposed_action" | "created_at"> | null;
};
export type TicketDetail = { ticket: QueueTicket; run: Run | null };
export type AuditEntry = { action: string; actor: string; before: string; after: string; at: string };
export type QueueResult = { items: QueueTicket[]; total: number; limit: number; offset: number };
export type CXAnalytics = {
  meta: { source_kind: string; as_of: string; timezone: string; window: { start: string | null; end: string | null; clock: string }; sample_count: number; total_count: number; excluded_count: number; unavailable_reason: string | null };
  processed_count: number;
  unprocessed_count: number;
  intents: { intent: string; count: number; percent: number }[];
  outcomes: { date: string; simulated_sent: number; simulated_approved: number; approval_required: number; escalate: number; total: number; [key: string]: string | number }[];
  confidence: { label: string; min: number; max: number; count: number }[];
  confidence_sample_count: number;
  confidence_unavailable_reason: string | null;
};

export const readable = (value: string) => value.replaceAll("_", " ");
export const decisionLabel = (value?: string) => ({ simulated_sent: "Reply simulated", simulated_approved: "Action approved", simulated_edited: "Reply edited", approval_required: "Needs approval", escalate: "Needs investigation", human_escalated: "Escalated" }[value || ""] || "Unprocessed");
export const decisionTone = (value?: string): "good" | "warn" | "bad" | "neutral" => value === "simulated_sent" || value === "simulated_approved" || value === "simulated_edited" ? "good" : value === "escalate" || value === "human_escalated" ? "bad" : value === "approval_required" ? "warn" : "neutral";
export const formatDate = (value: string) => new Date(/Z$|[+-]\d{2}:\d{2}$/.test(value) ? value : `${value}Z`).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kolkata" });

