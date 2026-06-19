"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { MessageSquarePlus, Trash2 } from "lucide-react";
import { api, ConversationItem } from "@/lib/api";
import { useChatStore } from "@/store/chat-store";
import { useSettingsStore } from "@/store/settings-store";
import { useTranslation } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

function formatTitle(item: ConversationItem) {
  const preview = (item.preview || "").trim();
  if (preview) return preview.length > 42 ? `${preview.slice(0, 42)}…` : preview;
  return item.conversation_id.slice(0, 10);
}

export function ChatHistoryPanel() {
  const { t } = useTranslation();
  const pathname = usePathname();
  const router = useRouter();
  const userId = useSettingsStore((s) => s.settings.userId || "default");
  const sessionId = useChatStore((s) => s.sessionId);
  const setSessionId = useChatStore((s) => s.setSessionId);
  const startNewChat = useChatStore((s) => s.startNewChat);
  const historyVersion = useChatStore((s) => s.historyVersion);
  const refreshHistory = useChatStore((s) => s.refreshHistory);

  const [items, setItems] = useState<ConversationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const resp = await api.historiesList(userId, 1, 50);
      setItems(resp?.data?.items || []);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    load();
  }, [load, historyVersion]);

  const handleSelect = (id: string) => {
    setSessionId(id);
    if (pathname !== "/chat") {
      router.push("/chat");
    }
  };

  const handleNewChat = () => {
    startNewChat();
    refreshHistory();
    if (pathname !== "/chat") {
      router.push("/chat");
    }
  };

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    try {
      await api.historiesDelete(pendingDelete);
      if (sessionId === pendingDelete) {
        startNewChat();
      }
      refreshHistory();
    } finally {
      setPendingDelete(null);
    }
  };

  return (
    <>
      <div className="flex h-full min-h-0 flex-col">
        <div className="mb-2 flex items-center justify-between px-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-400">
            {t.chat.historyTitle}
          </span>
          <button
            type="button"
            onClick={handleNewChat}
            className="inline-flex h-7 w-7 items-center justify-center rounded-md text-neutral-600 transition-colors hover:bg-[var(--gpt-hover)] hover:text-neutral-900"
            title={t.chat.newChat}
          >
            <MessageSquarePlus className="h-4 w-4" />
          </button>
        </div>

        <ScrollArea className="flex-1 min-h-0">
          {loading ? (
            <p className="px-2 py-1 text-xs text-neutral-500">{t.chat.historyLoading}</p>
          ) : items.length === 0 ? (
            <p className="px-2 py-1 text-xs text-neutral-500">{t.chat.historyEmpty}</p>
          ) : (
            <ul className="space-y-0.5 pb-2">
              {items.map((item) => {
                const active = sessionId === item.conversation_id;
                return (
                  <li key={item.conversation_id}>
                    <div
                      className={cn(
                        "group flex items-center gap-1 rounded-lg px-2 py-2 text-left transition-colors",
                        active
                          ? "bg-[var(--gpt-hover)] text-neutral-900"
                          : "text-neutral-700 hover:bg-[var(--gpt-hover)]"
                      )}
                    >
                      <button
                        type="button"
                        onClick={() => handleSelect(item.conversation_id)}
                        className="min-w-0 flex-1 truncate text-left text-sm"
                      >
                        {formatTitle(item)}
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setPendingDelete(item.conversation_id);
                        }}
                        className="hidden h-6 w-6 shrink-0 items-center justify-center rounded-md text-neutral-400 hover:bg-white hover:text-red-600 group-hover:inline-flex"
                        title={t.chat.historyDelete}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </ScrollArea>

        {pathname !== "/chat" && (
          <Link
            href="/chat"
            className="mt-2 block rounded-lg border border-[var(--gpt-border)] px-2 py-2 text-center text-xs font-medium text-neutral-700 hover:bg-[var(--gpt-hover)]"
          >
            {t.chat.openChatLink}
          </Link>
        )}
      </div>

      <Dialog open={!!pendingDelete} onOpenChange={(o) => !o && setPendingDelete(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.chat.historyDeleteTitle}</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-neutral-600">{t.chat.historyDeleteDesc}</p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setPendingDelete(null)}>
              {t.common.cancel}
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              {t.chat.historyDelete}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
