"use client";

import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { cn } from "@/lib/utils";

type AppShellProps = {
  children: React.ReactNode;
  className?: string;
  contentClassName?: string;
};

export function AppShell({ children, className, contentClassName }: AppShellProps) {
  return (
    <SidebarProvider>
      <div className={cn("flex h-screen bg-white", className)}>
        <AppSidebar />
        <div
          className={cn(
            "flex min-w-0 flex-1 flex-col overflow-hidden bg-white",
            contentClassName
          )}
        >
          {children}
        </div>
      </div>
    </SidebarProvider>
  );
}
