import type { Metadata } from "next";
import "./styles.css";
import { Navigation } from "@/components/navigation";

export const metadata: Metadata = { title: "Dhaga-OS | Operations workspace", description: "Synthetic Dhaga & Co. operations demo" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><div className="app-shell">
    <Navigation />
    <div className="main-frame"><header className="topbar"><div className="mobile-brand">Dhaga-OS</div><span className="topbar-label">OPERATIONS WORKSPACE</span><span className="topbar-tag">Demo environment</span></header><main>{children}</main></div>
  </div></body></html>;
}
