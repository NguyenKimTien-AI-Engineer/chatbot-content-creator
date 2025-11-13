"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Trash2, Plus, Search, Clock } from "lucide-react";
import { api, ConversationItem } from "@/lib/api";

interface Props {
  userId: string;
  selectedId?: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: (id: string) => void;
  mobileOpen?: boolean;
  onMobileOpenChange?: (open: boolean) => void;
}

export default function ChatHistorySidebar({ userId, selectedId, onSelectConversation, onNewConversation, mobileOpen: mobileOpenProp, onMobileOpenChange }: Props) {
  const [items, setItems] = useState<ConversationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<"updated_at" | "created_at">("updated_at");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);

  const load = async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.historiesList(userId, 1, 50);
      const list = resp?.data?.items || [];
      setItems(list);
    } catch (e: any) {
      setError("Không thể tải lịch sử chat");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [userId]);

  const filtered = useMemo(() => {
    const s = search.trim().toLowerCase();
    let arr = items;
    if (s) {
      arr = arr.filter((it) => {
        const text = `${it.preview || ""} ${it.conversation_id || ""}`.toLowerCase();
        return text.includes(s);
      });
    }
    arr = [...arr].sort((a, b) => {
      const av = (sortKey === "updated_at" ? a.updated_at : a.created_at) || "";
      const bv = (sortKey === "updated_at" ? b.updated_at : b.created_at) || "";
      return String(bv).localeCompare(String(av));
    });
    return arr;
  }, [items, search, sortKey]);

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    try {
      await api.historiesDelete(pendingDelete);
      setPendingDelete(null);
      await load();
    } catch {
      setPendingDelete(null);
    }
  };

  const startNewChat = async () => {
    const id = Math.random().toString(36).slice(2, 10);
    try {
      await api.historiesCreate({ conversation_id: id, user_id: userId });
    } catch {}
    try {
      localStorage.setItem("chat_selected_conversation", id);
      localStorage.setItem("chat_user_id", userId);
    } catch {}
    onNewConversation(id);
    await load();
    const nextOpen = false;
    setMobileOpen(nextOpen);
    if (onMobileOpenChange) onMobileOpenChange(nextOpen);
  };

  const renderList = () => (
    <div className="flex h-full flex-col">
      <div className="p-3 border-b bg-white">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Tìm kiếm..." className="pl-7" />
          </div>
          <Button variant="default" onClick={startNewChat} className="flex items-center gap-2" data-testid="new-chat-btn">
            <Plus className="w-4 h-4" />
            <span className="hidden md:inline">Chat mới</span>
          </Button>
        </div>
        <div className="mt-2">
          <Select value={sortKey} onValueChange={(v) => setSortKey(v as any)}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Sắp xếp" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="updated_at">Mới cập nhật</SelectItem>
              <SelectItem value="created_at">Mới tạo</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <ScrollArea className="flex-1">
        {loading ? (
          <div className="p-3 text-sm text-gray-500">Đang tải...</div>
        ) : error ? (
          <div className="p-3 text-sm text-red-600">{error}</div>
        ) : filtered.length === 0 ? (
          <div className="p-3 text-sm text-gray-500">Không có lịch sử</div>
        ) : (
          <ul className="p-2">
            {filtered.map((it) => (
              <li key={it.conversation_id} className={`group border rounded-md p-3 mb-2 cursor-pointer ${selectedId === it.conversation_id ? "bg-gray-100" : "bg-white"}`}>
                <div className="flex items-start justify-between gap-2" onClick={() => {
                  try {
                    localStorage.setItem("chat_selected_conversation", it.conversation_id);
                    localStorage.setItem("chat_user_id", userId);
                  } catch {}
                  onSelectConversation(it.conversation_id);
                  setMobileOpen(false);
                }}>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900 truncate">{it.conversation_id}</div>
                    <div className="text-xs text-gray-600 line-clamp-2 mt-1">{it.preview || ""}</div>
                    <div className="text-xs text-gray-400 mt-2 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>{it.updated_at || it.created_at || ""}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100" onClick={(e) => { e.stopPropagation(); setPendingDelete(it.conversation_id); }}>
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </ScrollArea>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden md:block w-80 border-r bg-white">
        {renderList()}
      </div>

      {/* Mobile sheet toggle button will be provided externally if needed; expose controlled open here */}
      <Sheet open={mobileOpenProp ?? mobileOpen} onOpenChange={(o) => { setMobileOpen(o); if (onMobileOpenChange) onMobileOpenChange(o); }}>
        <SheetContent side="left" className="w-[18rem] p-0">
          <SheetHeader className="sr-only">
            <SheetTitle>Lịch sử chat</SheetTitle>
          </SheetHeader>
          {renderList()}
        </SheetContent>
      </Sheet>

      {/* Confirm delete */}
      <Dialog open={!!pendingDelete} onOpenChange={(o) => !o && setPendingDelete(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Xóa cuộc trò chuyện?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-gray-600">Hành động này không thể hoàn tác.</p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setPendingDelete(null)}>Hủy</Button>
            <Button variant="destructive" onClick={confirmDelete}>Xóa</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}