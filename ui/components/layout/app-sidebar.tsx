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
import { useEffect, useMemo, useState, useCallback } from "react";
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

  const doLoad = useCallback(async () => {
    let mounted = true;
      try {
        setLoading(true);
        setError(null);
        const res = await api.getSessionsCached({ limit: 30, skip: 0 });
        const list = (res?.data || []).slice(0, 10);
        if (mounted) setSessions(list);
        const tasks = list.map(async (s) => {
          const r = await api.getHistoryCached({ session_id: s.session_id, limit: 1, page: 1 });
          const item: HistoryItem | undefined = r?.data?.[0];
          return { sid: s.session_id, txt: item?.query ? String(item.query) : "New chat" };
        });
        const results = await Promise.all(tasks);
        if (mounted) {
          const m: Record<string, string> = {};
          results.forEach((r) => (m[r.sid] = r.txt));
          setPreviews(m);
        }
      } catch (e: any) {
        if (mounted) setError(e?.message || "Lỗi tải lịch sử");
      } finally {
        if (mounted) setLoading(false);
      }
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    const cleanup = doLoad();
    const onStorage = (e: StorageEvent) => {
      if (e.key === "history_updated_at") {
        doLoad();
      }
    };
    window.addEventListener("storage", onStorage);
    const interval = setInterval(() => { doLoad(); }, 60000);
    return () => {
      cleanup && typeof cleanup === "function" && cleanup();
      window.removeEventListener("storage", onStorage);
      clearInterval(interval);
    };
  }, [doLoad]);

  const activeSessionId = useMemo(() => searchParams.get("session_id") || "", [searchParams]);

  return (
  <Sidebar className="border-r bg-white">
    <SidebarContent>
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
              const p = previews[s.session_id] || "New chat";
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
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
  </Sidebar>
);
}