"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowUpRight, BookOpen, Headphones, MessageSquareText, PackageCheck, ShieldCheck } from "lucide-react";
import { api, Meta } from "@/lib/api";
import { Card, ErrorState, PageTitle, Pill, Stat } from "@/components/ui";

type Overview = { demo: boolean; seed_version: string; cx: { total: number; intents: Record<string, number>; pending_approval: number }; reviews: { total: number; negative: number }; catalog: { total: number; states: Record<string, number> }; cost_line: { sampled_runs: number; mean_cost_usd: number | null; weekly_all_tickets_usd: number | null; weekly_wismo_usd: number | null; method: string }; verified_context: { label: string; value: string; source: string }[] };

export default function OverviewPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { Promise.all([api<Overview>("/overview"), api<Meta>("/meta")]).then(([a, b]) => { setData(a); setMeta(b); }).catch(e => setError(e.message)); }, []);
  return <div className="page-wrap">
    <PageTitle eyebrow="COMMAND CENTER / 01" title="Overview" subtitle="A shared view of what CX, Category, and Listing teams need to work on." right={<Pill tone="blue">Synthetic operating data</Pill>} />
    {error ? <ErrorState message={error} /> : !data ? <div className="loading">Loading operations…</div> : <>
      <div className="notice"><ShieldCheck size={19} /><div><strong>Two kinds of evidence.</strong> Operational counts below come from generated demo records. Client-brief figures are shown separately with their source.</div></div>
      <div className="stats-grid"><Stat label="SUPPORT CASES" value={data.cx.total} detail="Synthetic inbox" /><Stat label="WISMO CASES" value={data.cx.intents.wismo} detail="58% of demo cases" /><Stat label="REVIEWS" value={data.reviews.total} detail="Synthetic product feedback" /><Stat label="CATALOG SKUS" value={data.catalog.total} detail={`${data.catalog.states.blocked || 0} blocked`} /></div>
      <div className="section-label">TEAM WORKSPACES <span>What needs attention now</span></div>
      <div className="workspace-grid">
        <Link href="/cx" className="workspace-card"><div className="workspace-icon coral"><Headphones /></div><div className="workspace-kicker">CX TEAM</div><h2>Support agent</h2><p>Investigate customer cases, review proposed actions, and inspect guardrails.</p><div className="workspace-bottom"><span><strong>{data.cx.pending_approval}</strong> awaiting approval</span><ArrowUpRight size={19} /></div></Link>
        <Link href="/reviews" className="workspace-card"><div className="workspace-icon violet"><MessageSquareText /></div><div className="workspace-kicker">CATEGORY TEAM</div><h2>Review intelligence</h2><p>Spot recurring product issues and drill into customer evidence.</p><div className="workspace-bottom"><span><strong>{data.reviews.negative}</strong> low-rated reviews</span><ArrowUpRight size={19} /></div></Link>
        <Link href="/catalog" className="workspace-card"><div className="workspace-icon teal"><PackageCheck /></div><div className="workspace-kicker">LISTING TEAM</div><h2>Catalog velocity</h2><p>Find blocked SKUs, source conflicts, and the next drop risk.</p><div className="workspace-bottom"><span><strong>{data.catalog.states.blocked || 0}</strong> blocked SKUs</span><ArrowUpRight size={19} /></div></Link>
      </div>
      <div className="two-col"><Card title="Client-brief context" subtitle="Verified exercise facts"><div className="context-list">{data.verified_context.map(item => <div className="context-row" key={item.label}><div><span>{item.label}</span><small>{item.source}</small></div><strong>{item.value}</strong></div>)}</div></Card>
        <Card title="Demo data and rules" subtitle="Inspectable foundation"><div className="rules-summary"><div><span>SEED VERSION</span><strong>{data.seed_version}</strong></div><div><span>POLICY VERSION</span><strong>{meta?.policy_version}</strong></div><div><span>MODEL MODE</span><strong>{meta?.model_mode}</strong></div><div><span>MEASURED MODEL COST / CASE</span><strong>{data.cost_line.mean_cost_usd === null ? "Awaiting live sample" : `$${data.cost_line.mean_cost_usd.toFixed(6)}`}</strong></div><div><span>9,000 TICKETS / WEEK ESTIMATE</span><strong>{data.cost_line.weekly_all_tickets_usd === null ? "Awaiting live sample" : `$${data.cost_line.weekly_all_tickets_usd.toFixed(2)}`}</strong></div><div><span>5,220 WISMO / WEEK ESTIMATE</span><strong>{data.cost_line.weekly_wismo_usd === null ? "Awaiting live sample" : `$${data.cost_line.weekly_wismo_usd.toFixed(2)}`}</strong></div></div><p className="muted">{meta?.policy_disclaimer} {data.cost_line.method} Sample size: {data.cost_line.sampled_runs} model-using runs.</p><div className="rule-tags">{meta?.policies.map(p => <span key={p.id}>{p.id}</span>)}</div><div className="card-foot"><BookOpen size={16} /> Each CX case shows the policy and rule behind its decision.</div></Card></div>
    </>}
  </div>;
}
