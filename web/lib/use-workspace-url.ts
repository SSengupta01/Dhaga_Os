"use client";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
export function useWorkspaceUrl(){
  const params=useSearchParams(),router=useRouter(),path=usePathname();
  return {params,change:(values:Record<string,string>)=>{const next=new URLSearchParams(params.toString());Object.entries(values).forEach(([k,v])=>v?next.set(k,v):next.delete(k));router.push(`${path}?${next}`,{scroll:false})}};
}
