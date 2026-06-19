"use client";

import { Home, Settings, MessageSquare } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useTranslation } from "@/lib/i18n";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { ChatHistoryPanel } from "@/components/layout/chat-history-panel";

const menuItems = [
  { key: "home" as const, url: "/", icon: Home },
  { key: "chat" as const, url: "/chat", icon: MessageSquare },
  { key: "settings" as const, url: "/settings", icon: Settings },
];

export function AppSidebar() {
  const pathname = usePathname();
  const { t } = useTranslation();

  return (
    <Sidebar
      className="border-r border-[var(--gpt-border)] bg-[var(--gpt-sidebar)] [&_[data-sidebar=sidebar]]:border-0 [&_[data-sidebar=sidebar]]:bg-[var(--gpt-sidebar)] [&_[data-sidebar=sidebar]]:shadow-none"
    >
      <SidebarContent className="flex h-full flex-col px-2 py-3">
        <div className="mb-4 shrink-0 px-2 py-2">
          <span className="text-base font-semibold tracking-tight text-neutral-900">KAT</span>
        </div>

        <SidebarGroup className="shrink-0 p-0">
          <SidebarGroupContent>
            <SidebarMenu className="gap-0.5">
              {menuItems.map((item) => {
                const active = pathname === item.url;
                return (
                  <SidebarMenuItem key={item.key}>
                    <SidebarMenuButton
                      asChild
                      isActive={active}
                      className={cn(
                        "h-10 rounded-lg px-3 text-sm text-neutral-700 transition-colors",
                        "hover:bg-[var(--gpt-hover)] hover:text-neutral-900",
                        active && "bg-[var(--gpt-hover)] text-neutral-900 font-medium"
                      )}
                    >
                      <Link href={item.url}>
                        <item.icon className="mr-2 h-4 w-4" />
                        {t.nav[item.key]}
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <div className="mt-3 min-h-0 flex-1 border-t border-[var(--gpt-border)] pt-3">
          <ChatHistoryPanel />
        </div>
      </SidebarContent>
    </Sidebar>
  );
}
