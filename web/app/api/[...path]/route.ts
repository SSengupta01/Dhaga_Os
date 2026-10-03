import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const base = process.env.API_BASE_URL || "http://127.0.0.1:8000";
  const url = new URL(`${base.replace(/\/$/, "")}/${path.join("/")}`);
  url.search = request.nextUrl.search;
  const jar = await cookies();
  let demoSession = jar.get("dhaga_demo_session")?.value;
  if (!demoSession) demoSession = crypto.randomUUID();
  try {
    const upstream = await fetch(url, {
      method: request.method,
      headers: { "content-type": "application/json", "x-demo-session": demoSession,
        "x-internal-token": process.env.DEMO_SESSION_SECRET || "" },
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.text(),
      cache: "no-store",
    });
    const response = new NextResponse(await upstream.text(), { status: upstream.status,
      headers: { "content-type": upstream.headers.get("content-type") || "application/json" } });
    if (!jar.get("dhaga_demo_session")) response.cookies.set("dhaga_demo_session", demoSession, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", maxAge: 60 * 60 * 24 });
    return response;
  } catch {
    return NextResponse.json({ detail: "The API is unavailable. Start and seed the Python service." }, { status: 503 });
  }
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
