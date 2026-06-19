"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  User,
  Bot,
  MessageSquare,
  Sparkles,
  Globe,
  Palette,
  Bell,
  Database,
  Info,
  Save,
  RotateCcw,
  Download,
  Upload,
  Trash2,
  CheckCircle2,
  XCircle,
  Loader2,
  ChevronRight,
  Settings2,
  KeyRound,
  Zap,
  Shield,
  ExternalLink,
} from "lucide-react";
import { toast } from "sonner";
import { useTranslation } from "@/lib/i18n";

import { AppShell } from "@/components/layout/app-shell";
import { Header } from "@/components/layout/header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  AppSettings,
  applyTheme,
  DEFAULT_SETTINGS,
  syncLegacyStorage,
  useSettingsStore,
} from "@/store/settings-store";
import { testApiConnection } from "@/lib/settings-api";
import { cn } from "@/lib/utils";

type SectionId =
  | "profile"
  | "ai"
  | "chatbot"
  | "brand"
  | "api"
  | "appearance"
  | "notifications"
  | "data"
  | "about";

const SECTIONS: { id: SectionId; label: string; icon: typeof User; description: string }[] = [
  { id: "profile", label: "Hồ sơ", icon: User, description: "Thông tin cá nhân & tài khoản" },
  { id: "ai", label: "AI & Model", icon: Bot, description: "Mô hình Gemini và tham số" },
  { id: "chatbot", label: "Chatbot", icon: MessageSquare, description: "Hành vi trò chuyện & RAG" },
  { id: "brand", label: "Thương hiệu", icon: Sparkles, description: "Tone & ngôn ngữ nội dung" },
  { id: "api", label: "Kết nối API", icon: Globe, description: "Backend & endpoint" },
  { id: "appearance", label: "Giao diện", icon: Palette, description: "Theme và hiển thị" },
  { id: "notifications", label: "Thông báo", icon: Bell, description: "Cảnh báo & âm thanh" },
  { id: "data", label: "Dữ liệu", icon: Database, description: "Lưu trữ & xuất nhập" },
  { id: "about", label: "Giới thiệu", icon: Info, description: "Phiên bản & tài liệu" },
];

const CHAT_MODELS = [
  { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash", badge: "Khuyên dùng" },
  { value: "gemini-2.5-flash-lite", label: "Gemini 2.5 Flash Lite", badge: "Nhanh" },
  { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro", badge: "Mạnh" },
];

function SettingRow({
  label,
  description,
  children,
}: {
  label: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="space-y-1 pr-4">
        <Label className="text-sm font-medium text-gray-900 dark:text-gray-100">{label}</Label>
        {description ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
        ) : null}
      </div>
      <div className="shrink-0 sm:max-w-md sm:w-full">{children}</div>
    </div>
  );
}

export default function SettingsPage() {
  const { t } = useTranslation();
  const { settings, isDirty, setSetting, patchSettings, resetSettings, markClean, exportSettings, importSettings } =
    useSettingsStore();

  const [activeSection, setActiveSection] = useState<SectionId>("profile");
  const [draft, setDraft] = useState<AppSettings>(settings);
  const [apiStatus, setApiStatus] = useState<"idle" | "loading" | "ok" | "error">("idle");
  const [apiMessage, setApiMessage] = useState("");
  const [apiLatency, setApiLatency] = useState<number | null>(null);
  const [resetOpen, setResetOpen] = useState(false);
  const [clearOpen, setClearOpen] = useState(false);
  const importRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setDraft(settings);
  }, [settings]);

  useEffect(() => {
    try {
      const storedPrompt = localStorage.getItem("edited_main_prompt");
      if (storedPrompt && !settings.customMainPrompt) {
        patchSettings({ customMainPrompt: storedPrompt });
      }
    } catch {
      // ignore
    }
  }, [patchSettings, settings.customMainPrompt]);

  const updateDraft = useCallback(<K extends keyof AppSettings>(key: K, value: AppSettings[K]) => {
    setDraft((prev) => ({ ...prev, [key]: value }));
    setSetting(key, value);
  }, [setSetting]);

  const handleSave = () => {
    syncLegacyStorage(draft);
    applyTheme(draft.theme);
    markClean();
    toast.success("Đã lưu cài đặt");
  };

  const handleReset = () => {
    resetSettings();
    setDraft(DEFAULT_SETTINGS);
    syncLegacyStorage(DEFAULT_SETTINGS);
    applyTheme(DEFAULT_SETTINGS.theme);
    setResetOpen(false);
    toast.success("Đã khôi phục mặc định");
  };

  const handleTestApi = async () => {
    setApiStatus("loading");
    const result = await testApiConnection(draft);
    setApiLatency(result.latency);
    setApiMessage(result.message);
    setApiStatus(result.ok ? "ok" : "error");
    toast[result.ok ? "success" : "error"](result.ok ? "Kết nối API thành công" : "Không kết nối được API");
  };

  const handleExport = () => {
    const blob = new Blob([exportSettings()], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "mekongai-settings.json";
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Đã xuất cài đặt");
  };

  const handleImport = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      const ok = importSettings(String(reader.result || ""));
      if (ok) {
        setDraft(useSettingsStore.getState().settings);
        toast.success("Đã nhập cài đặt");
      } else {
        toast.error("File cài đặt không hợp lệ");
      }
    };
    reader.readAsText(file);
  };

  const handleClearData = () => {
    const keys = [
      "content-store",
      "mekongai-settings",
      "edited_main_prompt",
      "chat_selected_conversation",
      "temp_main_prompt",
      "use_temp_main_prompt",
    ];
    keys.forEach((k) => localStorage.removeItem(k));
    sessionStorage.clear();
    setClearOpen(false);
    toast.success("Đã xóa dữ liệu cục bộ");
  };

  const activeMeta = SECTIONS.find((s) => s.id === activeSection)!;

  return (
    <AppShell>
        <Header />

          <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 min-h-0">
            {/* Hero */}
            <div className="rounded-2xl border border-[var(--gpt-border)] bg-white p-6 md:p-8 mb-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Settings2 className="h-5 w-5 text-neutral-500" />
                    <span className="text-sm font-medium text-[var(--gpt-muted)]">{t.settings.hub}</span>
                  </div>
                  <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900">{t.settings.title}</h1>
                  <p className="mt-2 text-[var(--gpt-muted)] max-w-2xl">
                    {t.settings.subtitle}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {isDirty ? (
                    <Badge variant="outline" className="border-amber-200 bg-amber-50 text-amber-800">
                      {t.settings.unsaved}
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="border-[var(--gpt-border)] bg-[var(--gpt-sidebar)] text-neutral-700">
                      {t.settings.synced}
                    </Badge>
                  )}
                  <Badge variant="outline" className="border-[var(--gpt-border)] bg-white text-neutral-700">
                    {t.settings.geminiApi}
                  </Badge>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-[280px_1fr] gap-6">
              {/* Nav */}
              <Card className="h-fit xl:sticky xl:top-24 border-0 shadow-[0_1px_8px_rgba(0,0,0,0.04)] ring-1 ring-black/[0.05] dark:ring-white/[0.06] dark:bg-neutral-900/60">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Danh mục</CardTitle>
                  <CardDescription>Chọn mục cần cấu hình</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <ScrollArea className="max-h-[60vh]">
                    <nav className="px-2 pb-2 space-y-1">
                      {SECTIONS.map((section) => {
                        const Icon = section.icon;
                        const active = activeSection === section.id;
                        return (
                          <button
                            key={section.id}
                            type="button"
                            onClick={() => setActiveSection(section.id)}
                            className={cn(
                              "w-full flex items-center gap-3 rounded-xl px-3 py-3 text-left transition-all",
                              active
                                ? "bg-neutral-100 text-neutral-900 shadow-sm ring-1 ring-neutral-200 dark:bg-neutral-800 dark:text-white dark:ring-neutral-700"
                                : "text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800/60"
                            )}
                          >
                            <div
                              className={cn(
                                "flex h-9 w-9 items-center justify-center rounded-lg",
                                active ? "bg-neutral-900 text-white dark:bg-white dark:text-neutral-900" : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"
                              )}
                            >
                              <Icon className="h-4 w-4" />
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="font-medium text-sm">{section.label}</div>
                              <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{section.description}</div>
                            </div>
                            <ChevronRight className={cn("h-4 w-4 shrink-0 opacity-40", active && "opacity-100")} />
                          </button>
                        );
                      })}
                    </nav>
                  </ScrollArea>
                </CardContent>
              </Card>

              {/* Content */}
              <div className="space-y-6">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 flex items-center justify-center">
                    <activeMeta.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">{activeMeta.label}</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{activeMeta.description}</p>
                  </div>
                </div>

                {activeSection === "profile" && (
                  <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                    <CardHeader>
                      <CardTitle>Thông tin cá nhân</CardTitle>
                      <CardDescription>Dùng để nhận diện phiên làm việc và lưu lịch sử</CardDescription>
                    </CardHeader>
                    <CardContent className="divide-y divide-gray-100 dark:divide-gray-800">
                      <SettingRow label="Tên hiển thị" description="Xuất hiện ở header và sidebar">
                        <Input
                          value={draft.displayName}
                          onChange={(e) => updateDraft("displayName", e.target.value)}
                          placeholder="Tên của bạn"
                        />
                      </SettingRow>
                      <SettingRow label="Email" description="Tùy chọn, dùng cho thông báo">
                        <Input
                          type="email"
                          value={draft.email}
                          onChange={(e) => updateDraft("email", e.target.value)}
                          placeholder="email@example.com"
                        />
                      </SettingRow>
                      <SettingRow label="User ID" description="Định danh phiên chat & lịch sử trên backend">
                        <Input
                          value={draft.userId}
                          onChange={(e) => updateDraft("userId", e.target.value)}
                          placeholder="default"
                        />
                      </SettingRow>
                    </CardContent>
                  </Card>
                )}

                {activeSection === "ai" && (
                  <>
                    <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Zap className="h-5 w-5 text-neutral-700 dark:text-neutral-300" />
                          Mô hình Gemini
                        </CardTitle>
                        <CardDescription>Chọn model cho chat chính và tác vụ phụ</CardDescription>
                      </CardHeader>
                      <CardContent className="divide-y divide-gray-100 dark:divide-gray-800">
                        <SettingRow label="Model chat chính" description="Dùng cho trả lời chatbot">
                          <Select value={draft.chatModel} onValueChange={(v) => updateDraft("chatModel", v)}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                              {CHAT_MODELS.map((m) => (
                                <SelectItem key={m.value} value={m.value}>
                                  {m.label} · {m.badge}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </SettingRow>
                        <SettingRow label="Model phụ" description="Gợi ý, tóm tắt, tác vụ nhẹ">
                          <Select value={draft.miniModel} onValueChange={(v) => updateDraft("miniModel", v)}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                              {CHAT_MODELS.map((m) => (
                                <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </SettingRow>
                        <SettingRow label="Temperature" description={`Độ sáng tạo: ${draft.temperature}`}>
                          <Input
                            type="range"
                            min={0}
                            max={1}
                            step={0.1}
                            value={draft.temperature}
                            onChange={(e) => updateDraft("temperature", parseFloat(e.target.value))}
                            className="w-full accent-neutral-900 dark:accent-white"
                          />
                        </SettingRow>
                        <SettingRow label="Streaming" description="Phản hồi dần theo thời gian thực">
                          <Switch
                            checked={draft.streamingEnabled}
                            onCheckedChange={(v) => updateDraft("streamingEnabled", v)}
                          />
                        </SettingRow>
                      </CardContent>
                    </Card>
                    <Card className="border-dashed border-neutral-300 bg-neutral-50 dark:border-neutral-700 dark:bg-neutral-900/50">
                      <CardContent className="pt-6 flex gap-3 items-start">
                        <KeyRound className="h-5 w-5 text-neutral-700 dark:text-neutral-300 shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium text-neutral-900 dark:text-neutral-100">API Key Gemini</p>
                          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                            Khóa API được cấu hình trên server (.env). Frontend không lưu secret key để bảo mật.
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  </>
                )}

                {activeSection === "chatbot" && (
                  <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                    <CardHeader>
                      <CardTitle>Hành vi Chatbot</CardTitle>
                      <CardDescription>Tùy chỉnh trải nghiệm chat & truy xuất tri thức</CardDescription>
                    </CardHeader>
                    <CardContent className="divide-y divide-gray-100 dark:divide-gray-800">
                      <SettingRow label="Collection Qdrant" description="Vector DB cho RAG">
                        <Input
                          value={draft.defaultCollection}
                          onChange={(e) => updateDraft("defaultCollection", e.target.value)}
                          className="font-mono text-xs"
                        />
                      </SettingRow>
                      <SettingRow label="Tìm kiếm sản phẩm" description="Tự động gợi ý sản phẩm KAT trong chat">
                        <Switch
                          checked={draft.includeProducts}
                          onCheckedChange={(v) => updateDraft("includeProducts", v)}
                        />
                      </SettingRow>
                      <SettingRow label="Hiển thị tài liệu tham chiếu" description="Trích dẫn nguồn trong câu trả lời">
                        <Switch
                          checked={draft.showReferences}
                          onCheckedChange={(v) => updateDraft("showReferences", v)}
                        />
                      </SettingRow>
                      <SettingRow label="Tự lưu lịch sử chat" description="Đồng bộ hội thoại lên backend">
                        <Switch
                          checked={draft.autoSaveChat}
                          onCheckedChange={(v) => updateDraft("autoSaveChat", v)}
                        />
                      </SettingRow>
                      <SettingRow label="System instruction (user)" description="Hướng dẫn bổ sung cho từng phiên chat">
                        <Textarea
                          value={draft.systemInstructionUser}
                          onChange={(e) => updateDraft("systemInstructionUser", e.target.value)}
                          placeholder="Ví dụ: Luôn trả lời ngắn gọn, tập trung vào sản phẩm túi da..."
                          rows={4}
                        />
                      </SettingRow>
                      <SettingRow label="Custom main prompt" description="Prompt chính cho tạo nội dung fanpage">
                        <div className="space-y-2 w-full">
                          <Textarea
                            value={draft.customMainPrompt}
                            onChange={(e) => updateDraft("customMainPrompt", e.target.value)}
                            placeholder="Nhập prompt tùy chỉnh hoặc chỉnh sửa tại trang Custom Prompt..."
                            rows={5}
                          />
                          <Button variant="outline" size="sm" asChild>
                            <Link href="/custom-prompt">
                              Mở trình soạn Custom Prompt
                              <ExternalLink className="ml-2 h-3.5 w-3.5" />
                            </Link>
                          </Button>
                        </div>
                      </SettingRow>
                    </CardContent>
                  </Card>
                )}

                {activeSection === "brand" && (
                  <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                    <CardHeader>
                      <CardTitle>Thương hiệu & Nội dung</CardTitle>
                      <CardDescription>Ảnh hưởng tới tone và ngôn ngữ mặc định</CardDescription>
                    </CardHeader>
                    <CardContent className="divide-y divide-gray-100 dark:divide-gray-800">
                      <SettingRow label="Tên thương hiệu" description="Mặc định: KAT Leather">
                        <Input
                          value={draft.businessName}
                          onChange={(e) => updateDraft("businessName", e.target.value)}
                        />
                      </SettingRow>
                      <SettingRow label="Tone of voice" description="Phong cách viết content">
                        <Input
                          value={draft.brandTone}
                          onChange={(e) => updateDraft("brandTone", e.target.value)}
                        />
                      </SettingRow>
                      <SettingRow label="Ngôn ngữ mặc định" description="Ngôn ngữ ưu tiên khi tạo nội dung">
                        <Select
                          value={draft.defaultLanguage}
                          onValueChange={(v: "vi" | "en") => updateDraft("defaultLanguage", v)}
                        >
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="vi">{t.settings.vietnamese}</SelectItem>
                            <SelectItem value="en">{t.settings.english}</SelectItem>
                          </SelectContent>
                        </Select>
                      </SettingRow>
                    </CardContent>
                  </Card>
                )}

                {activeSection === "api" && (
                  <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                    <CardHeader>
                      <CardTitle>Kết nối Backend</CardTitle>
                      <CardDescription>Cấu hình proxy API giữa UI và FastAPI server</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>API Host</Label>
                          <Input
                            value={draft.apiHost}
                            onChange={(e) => updateDraft("apiHost", e.target.value)}
                            placeholder="localhost"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>API Port</Label>
                          <Input
                            value={draft.apiPort}
                            onChange={(e) => updateDraft("apiPort", e.target.value)}
                            placeholder="1979"
                          />
                        </div>
                      </div>

                      <div className="rounded-xl border bg-gray-50/80 dark:bg-gray-800/40 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium">Endpoint hiện tại</p>
                          <p className="text-xs font-mono text-gray-500 mt-1">
                            http://{draft.apiHost}:{draft.apiPort}
                          </p>
                          {apiStatus !== "idle" && (
                            <div className="flex items-center gap-2 mt-2 text-sm">
                              {apiStatus === "loading" && <Loader2 className="h-4 w-4 animate-spin text-neutral-600" />}
                              {apiStatus === "ok" && <CheckCircle2 className="h-4 w-4 text-neutral-900 dark:text-neutral-100" />}
                              {apiStatus === "error" && <XCircle className="h-4 w-4 text-neutral-500" />}
                              <span className={apiStatus === "ok" ? "text-neutral-900 dark:text-neutral-100" : apiStatus === "error" ? "text-neutral-600" : "text-gray-600"}>
                                {apiMessage}
                                {apiLatency != null ? ` · ${apiLatency}ms` : ""}
                              </span>
                            </div>
                          )}
                        </div>
                        <Button onClick={handleTestApi} disabled={apiStatus === "loading"}>
                          {apiStatus === "loading" ? (
                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Đang kiểm tra...</>
                          ) : (
                            "Kiểm tra kết nối"
                          )}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {activeSection === "appearance" && (
                  <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                    <CardHeader>
                      <CardTitle>Giao diện</CardTitle>
                      <CardDescription>Tùy chỉnh trải nghiệm nhìn thấy</CardDescription>
                    </CardHeader>
                    <CardContent className="divide-y divide-gray-100 dark:divide-gray-800">
                      <SettingRow label="Chế độ giao diện" description="Sáng, tối hoặc theo hệ thống">
                        <Select
                          value={draft.theme}
                          onValueChange={(v: "light" | "dark" | "system") => {
                            updateDraft("theme", v);
                            applyTheme(v);
                          }}
                        >
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="light">Sáng</SelectItem>
                            <SelectItem value="dark">Tối</SelectItem>
                            <SelectItem value="system">Theo hệ thống</SelectItem>
                          </SelectContent>
                        </Select>
                      </SettingRow>
                      <SettingRow label={t.settings.language} description={t.settings.languageDesc}>
                        <Select
                          value={draft.defaultLanguage}
                          onValueChange={(v: "vi" | "en") => updateDraft("defaultLanguage", v)}
                        >
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="en">{t.settings.english}</SelectItem>
                            <SelectItem value="vi">{t.settings.vietnamese}</SelectItem>
                          </SelectContent>
                        </Select>
                      </SettingRow>
                      <SettingRow label="Chế độ compact" description="Giảm khoảng cách trong giao diện chat">
                        <Switch
                          checked={draft.compactMode}
                          onCheckedChange={(v) => updateDraft("compactMode", v)}
                        />
                      </SettingRow>
                      <SettingRow label="Hiện timestamp" description="Thời gian trên từng tin nhắn chat">
                        <Switch
                          checked={draft.showTimestamps}
                          onCheckedChange={(v) => updateDraft("showTimestamps", v)}
                        />
                      </SettingRow>
                    </CardContent>
                  </Card>
                )}

                {activeSection === "notifications" && (
                  <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                    <CardHeader>
                      <CardTitle>Thông báo</CardTitle>
                      <CardDescription>Kiểm soát cảnh báo khi tạo nội dung xong</CardDescription>
                    </CardHeader>
                    <CardContent className="divide-y divide-gray-100 dark:divide-gray-800">
                      <SettingRow label="Thông báo desktop" description="Browser notification khi hoàn thành">
                        <Switch
                          checked={draft.desktopNotifications}
                          onCheckedChange={(v) => updateDraft("desktopNotifications", v)}
                        />
                      </SettingRow>
                      <SettingRow label="Âm thanh" description="Phát âm thanh khi có phản hồi mới">
                        <Switch
                          checked={draft.soundEnabled}
                          onCheckedChange={(v) => updateDraft("soundEnabled", v)}
                        />
                      </SettingRow>
                      <SettingRow label="Email digest" description="Tóm tắt hoạt động hàng tuần (sắp ra mắt)">
                        <Switch
                          checked={draft.emailDigest}
                          onCheckedChange={(v) => updateDraft("emailDigest", v)}
                          disabled
                        />
                      </SettingRow>
                    </CardContent>
                  </Card>
                )}

                {activeSection === "data" && (
                  <>
                    <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Shield className="h-5 w-5 text-neutral-700 dark:text-neutral-300" />
                          Quyền riêng tư
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="divide-y divide-gray-100 dark:divide-gray-800">
                        <SettingRow label="Lưu lịch sử chat" description="Cho phép backend ghi nhận hội thoại">
                          <Switch
                            checked={draft.saveChatHistory}
                            onCheckedChange={(v) => updateDraft("saveChatHistory", v)}
                          />
                        </SettingRow>
                        <SettingRow label="Phân tích ẩn danh" description="Giúp cải thiện chất lượng AI">
                          <Switch
                            checked={draft.analyticsEnabled}
                            onCheckedChange={(v) => updateDraft("analyticsEnabled", v)}
                          />
                        </SettingRow>
                      </CardContent>
                    </Card>

                    <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                      <CardHeader>
                        <CardTitle>Quản lý dữ liệu cục bộ</CardTitle>
                        <CardDescription>Xuất, nhập hoặc xóa cài đặt trên trình duyệt</CardDescription>
                      </CardHeader>
                      <CardContent className="flex flex-wrap gap-3">
                        <Button variant="outline" onClick={handleExport}>
                          <Download className="mr-2 h-4 w-4" />
                          Xuất JSON
                        </Button>
                        <Button variant="outline" onClick={() => importRef.current?.click()}>
                          <Upload className="mr-2 h-4 w-4" />
                          Nhập JSON
                        </Button>
                        <input
                          ref={importRef}
                          type="file"
                          accept="application/json"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) handleImport(file);
                            e.target.value = "";
                          }}
                        />
                        <Button variant="destructive" onClick={() => setClearOpen(true)}>
                          <Trash2 className="mr-2 h-4 w-4" />
                          Xóa cache
                        </Button>
                      </CardContent>
                    </Card>
                  </>
                )}

                {activeSection === "about" && (
                  <Card className="border-gray-200/80 shadow-sm dark:border-gray-800 dark:bg-gray-900/60">
                    <CardHeader>
                      <CardTitle>KAT Content Studio</CardTitle>
                      <CardDescription>Hệ thống RAG & tạo nội dung AI cho thương hiệu</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="rounded-xl border p-4 dark:border-gray-800">
                          <p className="text-xs text-gray-500 uppercase tracking-wide">Phiên bản UI</p>
                          <p className="text-lg font-semibold mt-1">0.1.0</p>
                        </div>
                        <div className="rounded-xl border p-4 dark:border-gray-800">
                          <p className="text-xs text-gray-500 uppercase tracking-wide">LLM Provider</p>
                          <p className="text-lg font-semibold mt-1">Google Gemini</p>
                        </div>
                        <div className="rounded-xl border p-4 dark:border-gray-800">
                          <p className="text-xs text-gray-500 uppercase tracking-wide">Backend</p>
                          <p className="text-lg font-semibold mt-1">FastAPI · Port {draft.apiPort}</p>
                        </div>
                        <div className="rounded-xl border p-4 dark:border-gray-800">
                          <p className="text-xs text-gray-500 uppercase tracking-wide">Framework UI</p>
                          <p className="text-lg font-semibold mt-1">Next.js 15</p>
                        </div>
                      </div>
                      <Separator />
                      <div className="flex flex-wrap gap-2">
                        <Button variant="outline" size="sm" asChild>
                          <Link href="/chat">{t.home.openChat}</Link>
                        </Button>
                        <Button variant="outline" size="sm" asChild>
                          <Link href="/">{t.nav.home}</Link>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Action bar */}
                <div className="sticky bottom-4 z-10">
                  <Card className="border-gray-200/80 shadow-lg backdrop-blur bg-white/90 dark:bg-gray-900/90 dark:border-gray-800">
                    <CardContent className="py-4 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {isDirty ? t.settings.saveHintDirty : t.settings.saveHintSaved}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        <Button variant="outline" onClick={() => setResetOpen(true)}>
                          <RotateCcw className="mr-2 h-4 w-4" />
                          {t.settings.reset}
                        </Button>
                        <Button onClick={handleSave} disabled={!isDirty} className="bg-neutral-900 hover:bg-neutral-800 text-white dark:bg-white dark:text-neutral-900 dark:hover:bg-neutral-200">
                          <Save className="mr-2 h-4 w-4" />
                          {t.settings.save}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </main>

      <Dialog open={resetOpen} onOpenChange={setResetOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Khôi phục mặc định?</DialogTitle>
            <DialogDescription>
              Tất cả cài đặt sẽ trở về giá trị ban đầu. Hành động này không thể hoàn tác.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setResetOpen(false)}>Hủy</Button>
            <Button variant="destructive" onClick={handleReset}>Khôi phục</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={clearOpen} onOpenChange={setClearOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Xóa dữ liệu cục bộ?</DialogTitle>
            <DialogDescription>
              Xóa cache, cài đặt và prompt tạm trên trình duyệt. Lịch sử trên server không bị ảnh hưởng.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setClearOpen(false)}>Hủy</Button>
            <Button variant="destructive" onClick={handleClearData}>Xóa dữ liệu</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
