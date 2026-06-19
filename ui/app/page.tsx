"use client";

import Link from "next/link";
import {
  MessageSquare,
  Settings,
  FileText,
  BarChart3,
  Sparkles,
  Edit3,
  ArrowRight,
  Clock,
  LayoutTemplate,
} from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Header } from "@/components/layout/header";
import { useTranslation } from "@/lib/i18n";
import { cn } from "@/lib/utils";

type FeatureId = "chat" | "settings" | "fanpage" | "plan" | "branding" | "prompt";

type FeatureCard = {
  id: FeatureId;
  icon: typeof MessageSquare;
  href?: string;
  available: boolean;
  primary?: boolean;
};

const FEATURES: FeatureCard[] = [
  { id: "chat", icon: MessageSquare, href: "/chat", available: true, primary: true },
  { id: "settings", icon: Settings, href: "/settings", available: true },
  { id: "fanpage", icon: FileText, available: false },
  { id: "plan", icon: BarChart3, available: false },
  { id: "branding", icon: Sparkles, available: false },
  { id: "prompt", icon: Edit3, available: false },
];

export default function HomePage() {
  const { t } = useTranslation();

  return (
    <AppShell>
      <Header />

      <main className="flex-1 overflow-y-auto min-h-0">
        <div className="mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-10">
          <section className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-3">
              {t.home.features}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {FEATURES.map((feature) => {
                const Icon = feature.icon;
                const meta = t.home.featuresList[feature.id];
                const inner = (
                  <div
                    className={cn(
                      "group relative flex h-full flex-col rounded-[1.15rem] p-5 transition-all",
                      "ring-1 ring-[var(--gpt-border)]",
                      feature.available
                        ? "bg-white hover:bg-[var(--gpt-sidebar)] cursor-pointer"
                        : "bg-[var(--gpt-sidebar)] opacity-70 cursor-not-allowed"
                    )}
                  >
                    <div className="flex items-start justify-between gap-3 mb-4">
                      <span
                        className={cn(
                          "flex h-11 w-11 items-center justify-center rounded-xl transition-colors",
                          feature.available
                            ? "bg-neutral-900 text-white group-hover:scale-105 dark:bg-white dark:text-neutral-900"
                            : "bg-neutral-200 text-neutral-500 dark:bg-neutral-800 dark:text-neutral-500"
                        )}
                      >
                        <Icon className="h-5 w-5" />
                      </span>
                      <span
                        className={cn(
                          "rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
                          feature.available
                            ? "bg-neutral-900 text-white dark:bg-white dark:text-neutral-900"
                            : "bg-neutral-200 text-neutral-500 dark:bg-neutral-800 dark:text-neutral-500"
                        )}
                      >
                        {feature.available ? (feature.primary ? t.home.ready : t.home.open) : t.header.comingSoon}
                      </span>
                    </div>
                    <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-1.5">
                      {meta.title}
                    </h3>
                    <p className="text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed flex-1">
                      {meta.description}
                    </p>
                    {feature.available && (
                      <span className="mt-4 inline-flex items-center text-sm font-medium text-neutral-900 dark:text-neutral-100">
                        {t.home.access}
                        <ArrowRight className="ml-1.5 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                      </span>
                    )}
                  </div>
                );

                if (feature.available && feature.href) {
                  return (
                    <Link key={feature.id} href={feature.href} className="block h-full">
                      {inner}
                    </Link>
                  );
                }

                return (
                  <div key={feature.id} aria-disabled="true" className="h-full">
                    {inner}
                  </div>
                );
              })}
            </div>
          </section>

          <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="rounded-[1.15rem] bg-white/60 p-6 ring-1 ring-black/[0.05] shadow-[0_1px_4px_rgba(0,0,0,0.04)] dark:bg-neutral-900/40 dark:ring-white/[0.06]">
              <div className="flex items-center gap-2 mb-4">
                <LayoutTemplate className="h-5 w-5 text-neutral-700 dark:text-neutral-300" />
                <h2 className="font-semibold text-neutral-900 dark:text-neutral-100">{t.home.quickStart}</h2>
              </div>
              <ul className="space-y-3 text-sm text-neutral-600 dark:text-neutral-400">
                <li className="flex gap-3">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-neutral-900 dark:bg-white" />
                  {t.home.quickStartChat}
                </li>
                <li className="flex gap-3">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-neutral-400" />
                  {t.home.quickStartSettings}
                </li>
                <li className="flex gap-3">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-neutral-300" />
                  {t.home.quickStartDev}
                </li>
              </ul>
            </div>

            <div className="rounded-[1.15rem] bg-neutral-50/80 p-6 ring-1 ring-black/[0.04] opacity-75 dark:bg-neutral-900/25 dark:ring-white/[0.04]">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-neutral-400" />
                  <h2 className="font-semibold text-neutral-500 dark:text-neutral-400">{t.home.stats}</h2>
                </div>
                <span className="text-[10px] font-semibold uppercase tracking-wide text-neutral-400">
                  {t.home.statsSoon}
                </span>
              </div>
              <div className="space-y-3 text-sm">
                {[
                  t.home.contentCreated,
                  t.home.templatesUsed,
                  t.home.timeSaved,
                ].map((label) => (
                  <div key={label} className="flex justify-between text-neutral-400">
                    <span>{label}</span>
                    <span className="font-medium">{t.home.dash}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      </main>
    </AppShell>
  );
}
