"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Bell,
  LogOut,
  Search,
  Settings,
  UserCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useSettingsStore } from "@/store/settings-store";
import { useTranslation } from "@/lib/i18n";
import { cn } from "@/lib/utils";

function getInitials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "M";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function LanguageToggle() {
  const { locale, setLocale } = useTranslation();

  return (
    <div className="flex items-center rounded-lg border border-[var(--gpt-border)] bg-[var(--gpt-sidebar)] p-0.5">
      {(["en", "vi"] as const).map((lang) => (
        <button
          key={lang}
          type="button"
          onClick={() => setLocale(lang)}
          className={cn(
            "rounded-md px-2.5 py-1 text-xs font-medium uppercase transition-colors",
            locale === lang
              ? "bg-white text-neutral-900 shadow-sm"
              : "text-[var(--gpt-muted)] hover:text-neutral-900"
          )}
        >
          {lang}
        </button>
      ))}
    </div>
  );
}

export function Header() {
  const settings = useSettingsStore((s) => s.settings);
  const { t } = useTranslation();
  const [displayName, setDisplayName] = useState("User");
  const [email, setEmail] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setDisplayName(settings.displayName || "User");
    setEmail(settings.email || "");
  }, [settings.displayName, settings.email]);

  const initials = getInitials(displayName);

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--gpt-border)] bg-white/80 px-4 py-2.5 backdrop-blur-md md:px-5">
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0 flex-1" />

        <div className="flex shrink-0 items-center gap-2 md:gap-2.5">
          <LanguageToggle />

          <div className="relative hidden sm:block">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
            <Input
              placeholder={t.header.search}
              className="h-9 w-48 border-[var(--gpt-border)] bg-[var(--gpt-sidebar)] pl-9 text-sm shadow-none focus-visible:ring-1 focus-visible:ring-neutral-300 md:w-56"
            />
          </div>

          <Button
            variant="outline"
            size="icon"
            disabled
            className="h-9 w-9 shrink-0 rounded-lg border-[var(--gpt-border)] bg-white text-neutral-400 shadow-none"
            title={t.header.notificationsSoon}
          >
            <Bell className="h-4 w-4" />
          </Button>

          <DropdownMenu open={open} onOpenChange={setOpen} modal={false}>
            <DropdownMenuTrigger asChild>
              <button
                type="button"
                aria-expanded={open}
                aria-haspopup="menu"
                className={cn(
                  "inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-[var(--gpt-border)] bg-white p-0 outline-none transition-colors",
                  "hover:bg-[var(--gpt-sidebar)]",
                  "focus-visible:ring-1 focus-visible:ring-neutral-300",
                  open && "bg-[var(--gpt-sidebar)]"
                )}
                title={displayName}
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-neutral-800 text-[11px] font-semibold text-white">
                  {initials}
                </span>
              </button>
            </DropdownMenuTrigger>

            <DropdownMenuContent
              align="end"
              sideOffset={8}
              collisionPadding={12}
              className="w-72 overflow-hidden rounded-xl border border-[var(--gpt-border)] bg-white p-0 shadow-lg"
            >
              <div className="border-b border-[var(--gpt-border)] bg-[var(--gpt-sidebar)] px-4 py-4">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-black text-sm font-semibold text-white">
                    {initials}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-neutral-900">
                      {displayName}
                    </p>
                    <p className="truncate text-xs text-[var(--gpt-muted)]">
                      {email || t.header.noEmail}
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-1.5">
                <DropdownMenuItem
                  disabled
                  className="cursor-not-allowed rounded-lg px-3 py-2.5 opacity-60 focus:bg-transparent"
                >
                  <UserCircle2 className="mr-3 h-4 w-4 text-neutral-400" />
                  <span className="flex-1 text-neutral-500">{t.header.personalInfo}</span>
                  <span className="text-[10px] font-medium uppercase tracking-wide text-neutral-400">
                    {t.header.comingSoon}
                  </span>
                </DropdownMenuItem>

                <DropdownMenuItem asChild className="cursor-pointer rounded-lg px-3 py-2.5">
                  <Link href="/settings" onClick={() => setOpen(false)}>
                    <Settings className="mr-3 h-4 w-4 text-neutral-700" />
                    <span className="flex-1 font-medium">{t.nav.settings}</span>
                  </Link>
                </DropdownMenuItem>
              </div>

              <DropdownMenuSeparator className="mx-0 bg-[var(--gpt-border)]" />

              <div className="p-1.5 pb-2">
                <DropdownMenuItem
                  disabled
                  className="cursor-not-allowed rounded-lg px-3 py-2.5 opacity-60 focus:bg-transparent"
                >
                  <LogOut className="mr-3 h-4 w-4 text-neutral-400" />
                  <span className="flex-1 text-neutral-500">{t.header.logout}</span>
                  <span className="text-[10px] font-medium uppercase tracking-wide text-neutral-400">
                    {t.header.comingSoon}
                  </span>
                </DropdownMenuItem>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
