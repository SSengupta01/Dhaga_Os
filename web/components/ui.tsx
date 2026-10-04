import type { ReactNode } from "react";

export function Eyebrow({ children }: { children: ReactNode }) { return <div className="eyebrow">{children}</div>; }
export function PageTitle({ eyebrow, title, subtitle, right }: { eyebrow: string; title: string; subtitle: string; right?: ReactNode }) { return <div className="page-title"><div><Eyebrow>{eyebrow}</Eyebrow><h1>{title}</h1><p>{subtitle}</p></div>{right}</div>; }
export function Card({ title, subtitle, children, className = "" }: { title?: string; subtitle?: string; children: ReactNode; className?: string }) { return <section className={`card ${className}`}>{title && <div className="card-head"><h2>{title}</h2>{subtitle && <span>{subtitle}</span>}</div>}{children}</section>; }
export function Pill({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "good" | "warn" | "bad" | "blue" }) { return <span className={`pill pill-${tone}`}>{children}</span>; }
export function Stat({ label, value, detail, tone = "" }: { label: string; value: string | number; detail?: string; tone?: string }) { return <div className={`stat ${tone}`}><div className="stat-label">{label}</div><strong>{value}</strong>{detail && <div className="stat-detail">{detail}</div>}</div>; }
export function ErrorState({ message }: { message: string }) { return <div className="error-state" role="alert"><strong>Request needs attention</strong><p>{message}</p></div>; }
export function EmptyState({ children }: { children: ReactNode }) { return <div className="empty-state">{children}</div>; }

export function LoadingState({label="Loading workspace…"}:{label?:string}) {return <div className="loading" role="status">{label}</div>}
export function Tabs({items,value,onChange}:{items:{id:string;label:string;count?:number}[];value:string;onChange:(value:string)=>void}){return <div className="tabs" aria-label="Workspace views">{items.map(item=><button key={item.id} aria-pressed={value===item.id} className={value===item.id?"active":""} onClick={()=>onChange(item.id)}>{item.label}{item.count!==undefined?` (${item.count})`:""}</button>)}</div>}
