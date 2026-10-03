import type { Metadata } from "next";
import Link from "next/link";
import { Activity, Headphones, MessageSquareText, PackageCheck, Workflow } from "lucide-react";
import "./styles.css";

export const metadata: Metadata = { title: "Dhaga-OS | Operations workspace", description: "Synthetic Dhaga & Co. operations demo" };

const links = [
  { href: "/", label: "Overview", icon: Activity },
  { href: "/cx", label: "CX Support", icon: Headphones },
  { href: "/reviews", label: "Review Intelligence", icon: MessageSquareText },
  { href: "/catalog", label: "Catalog Velocity Engine", icon: PackageCheck },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><div className="app-shell">
    <aside className="sidebar">
      <Link href="/" className="brand"><span className="brand-mark"><Workflow size={21} /></span><span><strong>Dhaga-OS</strong><small>OPERATIONS INTELLIGENCE</small></span></Link>
      <div className="sidebar-caption">WORKSPACE</div>
      <nav aria-label="Main navigation">{links.map(({ href, label, icon: Icon }) => <Link key={href} href={href} className="nav-link"><Icon size={18} strokeWidth={1.8} /><span>{label}</span></Link>)}</nav>
      <div className="sidebar-foot"><span className="live-dot" /> SYNTHETIC DEMO <p>Built around the Dhaga & Co. client brief. No live customer or company data.</p></div>
    </aside>
    <div className="main-frame"><header className="topbar"><div className="mobile-brand">Dhaga-OS</div><span className="topbar-label">OPERATIONS WORKSPACE</span><span className="topbar-tag">Demo environment</span></header><main>{children}</main></div>
  </div></body></html>;
}
