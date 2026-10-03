"use client";
import { useEffect, useState } from "react";
import { MessageSquareText, Search } from "lucide-react";
import { api } from "@/lib/api";
import { Card, EmptyState, ErrorState, PageTitle, Pill, Stat } from "@/components/ui";

type ReviewRow = { product_id: string; sku: string; name: string; category: string; review_count: number; negative_count: number; top_issue: string | null; issue_count: number; alert: boolean };
type ReviewOverview = { demo: boolean; total_reviews: number; products: ReviewRow[] };
type Evidence = { id: string; rating: number; text: string; date: string; analysis: { issues: string[]; sentiment: string } };
type Detail = { product: { id: string; name: string; sku: string; vendor_id: string }; evidence: Evidence[] };
type Investigation = { id: string; product_id: string; issue_code: string; status: string; owner: string; notes: string };

export default function ReviewsPage() {
  const [data, setData] = useState<ReviewOverview | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [query, setQuery] = useState("");
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { api<ReviewOverview>("/reviews/overview").then(setData).catch(e => setError(e.message)); }, []);
  useEffect(() => { api<{items: Investigation[]}>("/reviews/investigations").then(x => setInvestigations(x.items)).catch(() => {}); }, []);
  async function select(id: string) { try { setDetail(await api<Detail>(`/reviews/products/${id}`)); } catch (e) { setError((e as Error).message); } }
  async function investigate() { if (!detail) return; const issue = detail.evidence.flatMap(e => e.analysis?.issues || [])[0] || "other"; try { await api("/reviews/investigations", { method: "POST", body: JSON.stringify({ product_id: detail.product.id, issue_code: issue, owner: "Demo Category Team", notes: "Review customer evidence and product specification." }) }); setInvestigations((await api<{items: Investigation[]}>("/reviews/investigations")).items); } catch (e) { setError((e as Error).message); } }
  async function analyze(id: string) { try { await api(`/reviews/${id}/analyze`, { method: "POST" }); if (detail) await select(detail.product.id); } catch (e) { setError(`Model extraction: ${(e as Error).message}`); } }
  const products = data?.products.filter(p => `${p.name} ${p.sku} ${p.category}`.toLowerCase().includes(query.toLowerCase())) || [];
  return <div className="page-wrap"><PageTitle eyebrow="VOICE OF CUSTOMER / 03" title="Review Intelligence" subtitle="See recurring product-quality signals and the customer words behind them." right={<Pill tone="blue">Synthetic review analysis</Pill>} />
    <div className="notice"><MessageSquareText size={19} /><div><strong>Evidence first.</strong> Counts and issue tags are computed from seeded reviews. These are demo signals for investigation, not conclusions about real Dhaga products or vendors.</div></div>
    {error ? <ErrorState message={error} /> : !data ? <div className="loading">Loading reviews…</div> : <><div className="stats-grid three"><Stat label="REVIEWS INGESTED" value={data.total_reviews} detail="Synthetic dataset" /><Stat label="PRODUCTS MAPPED" value={data.products.length} detail="Shared catalog IDs" /><Stat label="INVESTIGATION FLAGS" value={data.products.filter(p => p.alert).length} detail="Volume and negative-rate rule" /></div>
      <div className="review-grid"><Card className="table-card"><div className="table-toolbar"><div><h2>Product signals</h2><p>Open a product to inspect supporting reviews. Alert rule: at least five recent reviews and a rising negative rate.</p></div><label className="search-box"><Search size={16} /><input aria-label="Search products" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search product or SKU" /></label></div>
        <div className="table-scroll"><table><thead><tr><th>PRODUCT</th><th>REVIEWS</th><th>NEGATIVE</th><th>TOP ISSUE</th><th>STATUS</th></tr></thead><tbody>{products.map(p => <tr onClick={() => select(p.product_id)} key={p.product_id} className={detail?.product.id === p.product_id ? "active-row" : ""}><td><strong>{p.name}</strong><small>{p.sku} · {p.category}</small></td><td>{p.review_count}</td><td>{p.negative_count}</td><td>{p.top_issue?.replaceAll("_", " ") || "—"}</td><td><Pill tone={p.alert ? "warn" : "neutral"}>{p.alert ? "Investigate" : "Monitor"}</Pill></td></tr>)}</tbody></table></div></Card>
        <Card title={detail ? detail.product.name : "Review evidence"} subtitle={detail ? `${detail.product.sku} · ${detail.product.vendor_id}` : "Select a product"} className="evidence-card">{!detail ? <EmptyState>Select a product to see its review evidence.</EmptyState> : <><div className="action-row"><button className="primary-button" onClick={investigate}>Open investigation</button></div><div className="evidence-list">{detail.evidence.slice(0, 12).map(r => <div className="evidence-item" key={r.id}><div><span className="stars">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span><small>{r.date}</small></div><p>“{r.text}”</p><div className="tag-row">{r.analysis?.issues?.map(issue => <Pill key={issue} tone="warn">{issue.replaceAll("_", " ")}</Pill>)}</div><button className="text-button" onClick={() => analyze(r.id)}>Re-analyze with live model</button></div>)}</div></>}</Card></div>
      <div className="section-spaced"><Card title="Investigation queue" subtitle="Human decisions, not vendor verdicts">{investigations.length ? investigations.map(item => <div className="context-row" key={item.id}><div><span>{item.product_id} · {item.issue_code.replaceAll("_", " ")}</span><small>{item.owner} · {item.id}</small></div><Pill tone="warn">{item.status}</Pill></div>) : <EmptyState>No investigations opened yet.</EmptyState>}</Card></div>
    </>}
  </div>;
}
