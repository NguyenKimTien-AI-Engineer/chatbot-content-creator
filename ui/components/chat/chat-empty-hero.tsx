"use client";

import { cn } from "@/lib/utils";
import { useTranslation } from "@/lib/i18n";

export const PROMPT_IDS = [
  "marketing",
  "product",
  "caption",
  "hashtag",
  "customer",
  "trend",
  "story",
  "consult",
] as const;

export type PromptId = (typeof PROMPT_IDS)[number];

type ChatEmptyGreetingProps = {
  displayName?: string;
};

export function ChatEmptyGreeting(_props: ChatEmptyGreetingProps) {
  const { t } = useTranslation();

  return (
    <div className="mb-8 text-center">
      <h1 className="text-[1.75rem] md:text-[2rem] font-normal tracking-tight text-neutral-800">
        {t.chat.emptyHeadline}
      </h1>
    </div>
  );
}

type ChatQuickPromptBarProps = {
  onSelectPrompt: (prompt: string, id: PromptId) => void;
  selectedPromptId?: PromptId | null;
};

export function ChatQuickPromptBar({ onSelectPrompt, selectedPromptId }: ChatQuickPromptBarProps) {
  const { t } = useTranslation();

  return (
    <div className="mt-5 w-full">
      <div className="flex flex-wrap items-center justify-center gap-2">
        {PROMPT_IDS.map((id) => {
          const item = t.chat.prompts[id];
          const active = selectedPromptId === id;
          return (
            <button
              key={id}
              type="button"
              onClick={() => onSelectPrompt(item.prompt, id)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full border px-3.5 py-2 text-sm transition-colors",
                active
                  ? "border-neutral-300 bg-[var(--gpt-hover)] text-neutral-900"
                  : "border-[var(--gpt-border)] bg-white text-neutral-700 hover:bg-[var(--gpt-hover)]"
              )}
            >
              {item.title}
              {id === "marketing" && (
                <span className="ml-0.5 text-[10px] font-medium uppercase text-[var(--gpt-muted)]">
                  {t.common.popular}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
