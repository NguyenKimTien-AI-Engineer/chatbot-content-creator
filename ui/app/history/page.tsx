"use client";

import { useEffect, useRef, useState } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { Header } from "@/components/layout/header";
import { api, SessionInfo } from "@/lib/api";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function HistoryPage() {
  const [items, setItems] = useState<SessionInfo[]>([]);
  const [previews, setPreviews] = useState<Record<string, string>>({});
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const limit = 15;
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const load = async (initial = false) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getSessions({ limit, skip: initial ? 0 : (page - 1) * limit });
      const data = res?.data || [];
      setItems((prev) => {
        const merged = initial ? data : [...prev, ...data];
        const seen = new Set<string>();
        return merged.filter((x) => {
          const id = x.session_id || "";
          if (seen.has(id)) return false;
          seen.add(id);
          return true;
        });
      });
      setHasMore(data.length === limit);
      setPage((p) => (initial ? 2 : p + 1));
      const m: Record<string, string> = {};
      data.forEach((s) => { m[s.session_id] = s.preview || "New chat"; });
      setPreviews((prev) => (initial ? m : { ...prev, ...m }));
    } catch (e: any) {
      setError(e?.message || "Lỗi tải lịch sử");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sid: string) => {
    try {
      setLoading(true);
      await api.deleteSession(sid);
      setItems((prev) => prev.filter((x) => x.session_id !== sid));
      const { [sid]: _, ...rest } = previews;
      setPreviews(rest);
      try { localStorage.setItem('history_updated_at', String(Date.now())); } catch {}
    } catch (e: any) {
      setError(e?.message || "Xóa lịch sử thất bại");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem("history_page_cache") : null;
      if (raw) {
        const cache = JSON.parse(raw);
        const ttl = 10 * 60 * 1000;
        if (Date.now() - (cache.ts || 0) < ttl) {
          setItems(Array.isArray(cache.items) ? cache.items : []);
          setPreviews(typeof cache.previews === "object" && cache.previews ? cache.previews : {});
          setHasMore(Boolean(cache.hasMore));
          setPage(Number(cache.page) || 2);
          return;
        }
      }
    } catch {}
    load(true);
  }, []);

  useEffect(() => {
    try {
      const toStore = { ts: Date.now(), items, previews, hasMore, page };
      localStorage.setItem("history_page_cache", JSON.stringify(toStore));
    } catch {}
  }, [items, previews, hasMore, page]);

  useEffect(() => {
    if (!hasMore) return;
    const el = sentinelRef.current;
    if (!el) return;
    const obs = new IntersectionObserver((entries) => {
      const [e] = entries;
      if (e.isIntersecting && !loading) {
        load(false);
      }
    }, { root: null, rootMargin: "200px", threshold: 0 });
    obs.observe(el);
    return () => { obs.disconnect(); };
  }, [hasMore, loading, page]);

  return (
    <SidebarProvider>
      <div className="flex min-h-screen">
        <AppSidebar />
        <div className="flex-1">
          <Header />
          <main className="p-6 space-y-4">
            <h1 className="text-xl font-semibold">Lịch sử</h1>
            {error && <div className="text-red-600">{error}</div>}
            <div className="grid grid-cols-1 gap-3">
              {items.map((s) => {
                const p = s.preview || previews[s.session_id] || "New chat";
                const preview = p.length > 80 ? p.slice(0, 80) + "…" : p;
                const time = s.last_activity || s.updated_at || s.created_at || "";
                return (
                  <Card key={`${s.session_id}`} className="p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <Link href={`/chat?session_id=${encodeURIComponent(s.session_id)}`} className="block flex-1">
                        <div className="flex items-center justify-between">
                          <div className="text-gray-800 truncate whitespace-nowrap max-w-[32rem]">{preview}</div>
                          {time && <Badge variant="outline">{String(time)}</Badge>}
                        </div>
                      </Link>
                      <button
                        onClick={() => handleDelete(s.session_id)}
                        className="ml-3 px-3 py-1 rounded border text-red-600 hover:bg-red-50"
                        disabled={loading}
                      >
                        Xóa
                      </button>
                    </div>
                  </Card>
                );
              })}
              {!loading && items.length === 0 && (
                <div className="text-gray-500">Không có lịch sử</div>
              )}
            </div>
            {hasMore && (
              <div ref={sentinelRef} className="py-4 text-center text-gray-400">
                {loading ? "Đang tải…" : "Cuộn để tải thêm"}
              </div>
            )}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}