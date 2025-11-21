"use client";

import { 
  Home, 
  FileText, 
  Settings, 
  Users, 
  BarChart3,
  Sparkles,
  Edit3,
  MessageSquare
} from "lucide-react";
import Link from "next/link";
import { usePathname, useSearchParams, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useEffect, useMemo, useState, useCallback, useRef } from "react";
import { api, SessionInfo, HistoryItem } from "@/lib/api";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const menuItems = [
  {
    title: "Trang chủ",
    url: "/",
    icon: Home,
  },
  {
    title: "New chat",
    url: "/chat",
    icon: MessageSquare,
  },
  {
    title: "Chat history",
    url: "/history",
    icon: FileText,
  },
  // {
  //   title: "Tạo nội dung Fanpage",
  //   url: "/fanpage",
  //   icon: FileText,
  // },
  // {
  //   title: "Custom Prompt",
  //   url: "/custom-prompt",
  //   icon: Edit3,
  // },
  // {
  //   title: "Kế hoạch nội dung",
  //   url: "#",
  //   icon: BarChart3,
  // },
  // {
  //   title: "Branding",
  //   url: "#",
  //   icon: Sparkles,
  // },
  // {
  //   title: "Quản lý người dùng",
  //   url: "#",
  //   icon: Users,
  // },
  // {
  //   title: "Cài đặt",
  //   url: "#",
  //   icon: Settings,
  // },
];

export function AppSidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [previews, setPreviews] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const limit = 20;
  const [hasMore, setHasMore] = useState(true);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const doLoad = useCallback(async () => {
    let mounted = true;
    try {
      setLoading(true);
      setError(null);
      const res = await api.getSessionsCached({ limit, skip });
      const list = res?.data || [];
      if (mounted) {
        setSessions((prev) => {
          const merged = skip === 0 ? list : [...prev, ...list];
          const seen = new Set<string>();
          return merged.filter((s) => {
            const id = s.session_id || "";
            if (seen.has(id)) return false;
            seen.add(id);
            return true;
          });
        });
        setHasMore((res?.data?.length || 0) === limit);
      }
      if (mounted) {
        const m: Record<string, string> = {};
        list.forEach((s) => { m[s.session_id] = s.preview || "New chat"; });
        setPreviews((prev) => (skip === 0 ? m : { ...prev, ...m }));
      }
    } catch (e: any) {
      if (mounted) setError(e?.message || "Lỗi tải lịch sử");
    } finally {
      if (mounted) setLoading(false);
    }
    return () => { mounted = false; };
  }, [limit, skip]);

  useEffect(() => {
    const cleanup = doLoad();
    return () => { cleanup && typeof cleanup === "function" && cleanup(); };
  }, [doLoad]);

  useEffect(() => {
    const ws = api.connectHistoryWS();
    if (!ws) return;
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data?.type === "session_update") {
          const sid: string = data.session_id;
          const preview: string = String(data.preview || "New chat");
          const updated_at: string = String(data.updated_at || new Date().toISOString());
          setPreviews((prev) => ({ ...prev, [sid]: preview }));
          setSessions((prev) => {
            const idx = prev.findIndex((s) => s.session_id === sid);
            const updated: SessionInfo = {
              session_id: sid,
              user_id: prev[idx]?.user_id || "",
              updated_at,
              last_activity: updated_at,
              created_at: prev[idx]?.created_at || undefined,
              preview,
            };
            const next = idx >= 0 ? [updated, ...prev.filter((s) => s.session_id !== sid)] : [updated, ...prev];
            return next.slice(0, 100);
          });
        }
      } catch {}
    };
    ws.onerror = () => {};
    return () => { try { ws.close(); } catch {} };
  }, []);

  useEffect(() => {
    if (!hasMore) return;
    const el = sentinelRef.current;
    if (!el) return;
    const obs = new IntersectionObserver((entries) => {
      const [e] = entries;
      if (e.isIntersecting && !loading) {
        setSkip((s) => s + limit);
      }
    }, { root: null, rootMargin: "200px", threshold: 0 });
    obs.observe(el);
    return () => { obs.disconnect(); };
  }, [hasMore, loading]);

  const activeSessionId = useMemo(() => searchParams.get("session_id") || "", [searchParams]);

  return (
  <Sidebar className="border-r bg-white">
    <SidebarContent className="flex flex-col h-full overflow-hidden">
      <SidebarGroup>
        <SidebarGroupLabel className="flex items-center text-lg font-semibold text-blue-700 px-4 py-6 gap-2">
          <img
            src="/logo.png"
            alt="MekongAI Logo"
            className="w-6 h-6 object-contain"
          />
          MEKONGAI
        </SidebarGroupLabel>

        <SidebarGroupContent>
          <SidebarMenu>
            {menuItems.map((item) => (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton
                  asChild
                  isActive={pathname === item.url}
                  className={cn(
                    "w-full justify-start px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-gray-900",
                    pathname === item.url && "bg-blue-50 text-blue-700 border-r-2 border-blue-600"
                  )}
                >
                  <Link
                    href={item.url}
                    onClick={(e) => {
                      if (item.title === "New chat") {
                        e.preventDefault();
                        const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
                        let out = "";
                        for (let i = 0; i < 15; i++) out += chars[Math.floor(Math.random() * chars.length)];
                        const sid = out;
                        router.push(`/chat?session_id=${encodeURIComponent(sid)}`);
                        return;
                      }
                    }}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.title}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <div className="flex-1 overflow-y-auto">
      <SidebarGroup>
        <SidebarGroupLabel className="flex items-center text-sm font-medium text-gray-700 px-4 py-2">
          Chats
        </SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            {loading && (
              <SidebarMenuItem>
                <div className="px-4 py-3 text-gray-500">Đang tải…</div>
              </SidebarMenuItem>
            )}
            {!loading && !error && sessions.map((s) => {
              const p = s.preview || previews[s.session_id] || "New chat";
              const text = p.length > 38 ? p.slice(0, 38) + "…" : p;
              const active = pathname === "/chat" && activeSessionId === s.session_id;
              return (
                <SidebarMenuItem key={`${s.session_id}`}>
                  <SidebarMenuButton
                    asChild
                    isActive={active}
                    className={cn(
                      "w-full justify-start px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-gray-900",
                      active && "bg-blue-50 text-blue-700 border-r-2 border-blue-600"
                    )}
                  >
                    <Link href={`/chat?session_id=${encodeURIComponent(s.session_id)}`}>
                      <MessageSquare className="mr-3 h-5 w-5" />
                      <span className="truncate whitespace-nowrap max-w-[12rem]">{text}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              );
            })}
            {!loading && !error && sessions.length === 0 && (
              <SidebarMenuItem>
                <div className="px-4 py-3 text-gray-500">Không có lịch sử</div>
              </SidebarMenuItem>
            )}
            {!loading && error && (
              <SidebarMenuItem>
                <div className="px-4 py-3 text-red-600">{error}</div>
              </SidebarMenuItem>
            )}
            <div ref={sentinelRef} />
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
      </div>
    </SidebarContent>
  </Sidebar>
);
}