export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, { cache: "no-store", ...options,
    headers: { "content-type": "application/json", ...(options?.headers || {}) } });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = data.detail;
    throw new Error(typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export type Policy = { id: string; label: string; text: string; required_facts: string[]; approval_required: boolean; failure_reason: string };
export type Meta = { seed_version: string; policy_version: string; policy_disclaimer: string; policies: Policy[]; model_mode: string; models: { classifier: string; evaluator: string } };
export type Ticket = { id: string; customer_id: string; order_id: string | null; channel: string; message: string; language: string; scenario: string | null; status: string; created_at: string; messages: { sender: string; text: string; at: string }[] };
export type Trace = { stage?: string; kind?: string; result?: string; role?: string; status?: string; model?: string; reason?: string; latency_ms?: number; tokens?: Record<string, number>; [key: string]: unknown };
export type Run = { id: string; ticket_id: string; intent: string; decision: string; proposed_reply: string; proposed_action: string | null; reason_codes: string[]; verified_facts: Record<string, unknown>; policy_id: string | null; trace: Trace[]; cost_usd: number; created_at: string };
export type Product = { id: string; sku: string; name: string; vendor_id: string; category: string; colour: string | null; fabric: string | null; price: number; inventory: Record<string, number>; raw_attributes: Record<string, unknown>; field_provenance: Record<string, unknown>; images: string[]; workflow: { blockers: string[]; [key: string]: unknown }; status: string; target_drop: string };
