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
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
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
    title: "Chat",
    url: "/chat",
    icon: MessageSquare,
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
  {
    title: "Cài đặt",
    url: "#",
    icon: Settings,
  },
];

export function AppSidebar() {
  const pathname = usePathname();

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
                  <Link href={item.url}>
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.title}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
  </Sidebar>
);
}