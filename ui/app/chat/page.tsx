"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, Smile, Plus } from "lucide-react";
import { AppSidebar } from "@/components/layout/app-sidebar";
import Image from "next/image";
import { Header } from "@/components/layout/header";
import { SidebarProvider } from "@/components/ui/sidebar";

type Role = "user" | "assistant" | "chart" | "reference";

interface ChatMessage {
  id: string;
  role: Role;
  content: string | any;
  timestamp: number;
}

const DEFAULT_COLLECTION = "CHATBOT_MekongAI_d41b1532-bf75-481d-ad6d-b7dac8cbae4d";
const CHART_SENTINEL = "### === GENERATE CHART === ###";

function generateRandomHistoryId(length = 15) {
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let out = "";
  for (let i = 0; i < length; i++) out += chars[Math.floor(Math.random() * chars.length)];
  return out;
}

function fixLinksInHtml(rawHtml: string): string {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(rawHtml, "text/html");
    const nodes = doc.querySelectorAll("group-link");
    nodes.forEach((group) => {
      const details = doc.createElement("details");
      const summary = doc.createElement("summary");
      summary.textContent = "📑";
      const div = doc.createElement("div");
      const ul = doc.createElement("ul");
      ul.style.listStyleType = "none";
      ul.style.paddingTop = "7px";
      ul.style.paddingBottom = "5px";
      ul.style.margin = "10px 0";
      ul.style.backgroundColor = "#f7f7f7";
      ul.style.borderRadius = "5px";
      group.querySelectorAll("a").forEach((a) => {
        const li = doc.createElement("li");
        li.style.marginBottom = "5px";
        const newA = doc.createElement("a");
        newA.href = a.getAttribute("href") || "#";
        newA.target = "_blank";
        newA.textContent = a.textContent || "link";
        newA.style.textDecoration = "none";
        newA.style.color = "#0068c9";
        li.appendChild(newA);
        ul.appendChild(li);
      });
      div.appendChild(ul);
      details.appendChild(summary);
      details.appendChild(div);
      group.replaceWith(details);
    });
    return doc.body.innerHTML;
  } catch (e) {
    return rawHtml;
  }
}
// Format assistant text into rich HTML: bold first line (title), convert bullet/numbered lines into lists, keep inline icons/emojis if present.
function formatAssistantHtml(raw: string): string {
  try {
    const normalized = String(raw || "").replace(/\r\n/g, "\n");
    if (!normalized.trim()) return "";

    const firstBreak = normalized.indexOf("\n");
    const head = (firstBreak >= 0 ? normalized.slice(0, firstBreak) : normalized).trim();
    const tail = firstBreak >= 0 ? normalized.slice(firstBreak + 1) : "";

    const boldInline = (s: string) =>
      s
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/_(.+?)_/g, "<em>$1</em>")
        .replace(/`([^`]+?)`/g, "<code class=\"px-1 py-0.5 bg-gray-100 rounded\">$1</code>")
        .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline">$1<\/a>');

    let html = "";
    if (head) {
      html += `<div class="font-semibold text-gray-900 mb-2 flex items-center gap-2">${boldInline(head)}</div>`;
    }

    const lines = tail.split("\n");
    const bulletRegex = /^(?:[-*•]|–)\s+/;
    const numRegex = /^\d+[\).\s]+/;
    let inUl = false;
    let inOl = false;
    let olCounter = 0; // ổn định đánh số cho danh sách có thứ tự

    const closeLists = () => {
      if (inUl) { html += "</ul>"; inUl = false; }
      if (inOl) { html += "</ol>"; inOl = false; olCounter = 0; }
    };

    // Extended helpers and states for richer formatting
    const escapeHtml = (s: string) =>
      s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    const labelIcon = (label: string) => {
      switch (label.toLowerCase()) {
        case "group": return "👥";
        case "fanpage": return "📄";
        case "website": return "🌐";
        case "facebook": return "📘";
        case "tiktok": return "🎵";
        case "youtube": return "▶️";
        case "zalo": return "💬";
        case "shopee": return "🛍️";
        case "lazada": return "🛒";
        case "hotline": return "☎️";
        case "email": return "✉️";
        default: return "🔗";
      }
    };

    let inCode = false;
    let codeBuffer: string[] = [];
    let inTable = false;
    let tableRows: string[][] = [];

    // Ordered list extras: alpha and roman numerals
    const alphaRegex = /^[A-Za-z][\).\s]+/;
    const romanRegex = /^(?=[IVXLCDM])[IVXLCDM]+[\).\s]+/;

    // Heuristic to decide if a line `Key: Value` is a true KV pair
    const looksLikeKeyValue = (k: string, v: string) => {
      const key = k.trim();
      const wordCount = key.split(/\s+/).filter(Boolean).length;
      if (wordCount > 6) return false; // too long -> likely a sentence
      if (key.length > 40) return false; // overly long key
      if (/[.!?…]$/.test(key)) return false; // sentence-like endings
      return true;
    };

    // Key-Value pairs accumulator
    let inKV = false;
    let kvRows: Array<[string, string]> = [];
    const flushKV = () => {
      if (!inKV || kvRows.length === 0) return;
      if (kvRows.length >= 2) {
        html += `<div class="overflow-x-auto mb-2"><table class="min-w-full text-sm border border-gray-200 rounded">`;
        html += `<tbody>` + kvRows.map(([k, v]) => `<tr><td class="px-3 py-2 border-b font-medium text-gray-900">${escapeHtml(k)}</td><td class="px-3 py-2 border-b">${boldInline(escapeHtml(v))}</td></tr>`).join("") + `</tbody>`;
        html += `</table></div>`;
      } else {
        const [k, v] = kvRows[0];
        html += `<p class="mb-2"><strong>${escapeHtml(k)}:</strong> ${boldInline(escapeHtml(v))}</p>`;
      }
      inKV = false;
      kvRows = [];
    };

    // Callout blocks :::info|warning|success|note ... :::
    let inCallout = false;
    let calloutType: string | null = null;
    let calloutBuffer: string[] = [];
    const flushCallout = () => {
      if (!inCallout) return;
      const type = String(calloutType || 'info').toLowerCase();
      const map = {
        info: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-800', icon: 'ℹ️' },
        warning: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-800', icon: '⚠️' },
        success: { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-800', icon: '✅' },
        note: { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-700', icon: '📝' },
      } as const;
      const style = (map as any)[type] || map.info;
      html += `<div class="rounded-md ${style.bg} ${style.border} ${style.text} border p-3 mb-2"><div class="flex items-start gap-2"><span>${style.icon}</span><div>` + calloutBuffer.map((l) => `<p class="mb-1">${boldInline(escapeHtml(l))}</p>`).join("") + `</div></div></div>`;
      inCallout = false;
      calloutType = null;
      calloutBuffer = [];
    };

    const flushCode = () => {
      if (inCode) {
        html += `<pre class="bg-gray-50 border border-gray-200 rounded p-3 overflow-auto text-xs mb-2"><code>${escapeHtml(codeBuffer.join("\n"))}</code></pre>`;
        inCode = false;
        codeBuffer = [];
      }
    };

    const flushTable = () => {
      if (!inTable || tableRows.length === 0) return;
      const isHeaderSep = tableRows.length > 1 && tableRows[1].every((c) => /^-+$/.test(c));
      const header = isHeaderSep ? tableRows[0] : null;
      const bodyRows = isHeaderSep ? tableRows.slice(2) : tableRows;
      html += `<div class="overflow-x-auto mb-2"><table class="min-w-full text-sm border border-gray-200 rounded">`;
      if (header) {
        html += `<thead class="bg-gray-50"><tr>` + header.map((h) => `<th class="text-left px-3 py-2 border-b">${escapeHtml(h)}</th>`).join("") + `</tr></thead>`;
      }
      html += `<tbody>` + bodyRows.map((row) => `<tr>` + row.map((c) => `<td class="px-3 py-2 border-b">${escapeHtml(c)}</td>`).join("") + `</tr>`).join("") + `</tbody>`;
      html += `</table></div>`;
      inTable = false;
      tableRows = [];
    };

    for (const line of lines) {
      const t = line.trim();
      if (!t) continue;
      // Normalize stray tabs in inline content (outside code blocks)
      const tNorm = t.replace(/\t+/g, " ");
      // Handle full-line bold like `** Tiêu đề \t **`
      const fullBold = tNorm.match(/^\*\*\s*(.*?)\s*\*\*$/);
      if (fullBold) { closeLists(); flushCode(); flushTable(); flushKV(); html += `<div class="font-semibold text-gray-900 mt-2 mb-1">${escapeHtml(fullBold[1])}</div>`; continue; }
      // Callout fences
      const calloutOpen = tNorm.match(/^:::(info|warning|success|note)$/i);
      if (calloutOpen) { closeLists(); flushCode(); flushTable(); flushKV(); inCallout = true; calloutType = calloutOpen[1].toLowerCase(); calloutBuffer = []; continue; }
      if (tNorm === ':::') { closeLists(); flushCode(); flushTable(); flushKV(); flushCallout(); continue; }
      if (inCallout) { calloutBuffer.push(line); continue; }
      // Code fences ```
      if (/^```/.test(tNorm)) {
        closeLists(); flushTable(); flushKV();
        if (!inCode) { inCode = true; codeBuffer = []; } else { flushCode(); }
        continue;
      }
      if (inCode) { codeBuffer.push(line); continue; }
      // Horizontal rule
      if (/^-{3,}$/.test(tNorm) || tNorm === "—") { closeLists(); flushTable(); flushKV(); html += `<hr class="my-3 border-gray-200"/>`; continue; }
      // Blockquote
      if (/^>\s+/.test(tNorm)) { closeLists(); flushTable(); flushKV(); html += `<blockquote class="border-l-4 border-gray-300 pl-3 text-gray-700 italic mb-2">${boldInline(tNorm.replace(/^>\s+/, ""))}</blockquote>`; continue; }
      // Headings #, ##, ###
      const hMatch = tNorm.match(/^(#{1,3})\s+(.*)$/);
      if (hMatch) {
        closeLists(); flushTable(); flushKV();
        const level = Math.min(hMatch[1].length + 2, 6);
        html += `<h${level} class="font-semibold text-gray-900 mt-2 mb-1">${boldInline(hMatch[2])}</h${level}>`;
        continue;
      }
      // Labelled chips
      const labelMatch = tNorm.match(/^(Group|Fanpage|Website|Facebook|TikTok|YouTube|Zalo|Shopee|Lazada|Shop|Hotline|Email):\s*(.+)$/i);
      if (labelMatch) {
        closeLists(); flushTable(); flushKV();
        const label = labelMatch[1];
        const value = labelMatch[2].trim();
        const urlMatch = value.match(/https?:\/\/\S+/);
        const url = urlMatch ? urlMatch[0] : null;
        const chip = (content: string) => `<span class=\"inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-gray-100 text-gray-800 text-xs mr-1\">${labelIcon(label)}<span>${content}</span></span>`;
        if (url) {
          html += `<div class=\"mb-2\"><a href=\"${url}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"no-underline\">${chip(label)}</a></div>`;
        } else if (/^\S+@\S+\.\S+$/.test(value) && label.toLowerCase() === "email") {
          const mail = escapeHtml(value);
          html += `<div class=\"mb-2\"><a href=\"mailto:${mail}\" class=\"no-underline\">${chip(label)}</a></div>`;
        } else {
          html += `<div class=\"mb-2\">${chip(`${label}: ${escapeHtml(value)}`)}</div>`;
        }
        continue;
      }
      // Image line ![alt](url)
      const imgMatch = tNorm.match(/^!\[([^\]]*)\]\((https?:\/\/[^)]+)\)\s*$/);
      if (imgMatch) { closeLists(); flushCode(); flushTable(); flushKV(); const alt = escapeHtml(imgMatch[1] || ""); const url = imgMatch[2]; html += `<figure class="mb-2"><img src="${url}" alt="${alt}" class="max-w-full rounded border border-gray-200"/>` + (alt ? `<figcaption class="text-xs text-gray-500 mt-1">${alt}</figcaption>` : ``) + `</figure>`; continue; }
      // Lists
      if (bulletRegex.test(tNorm)) {
        flushTable();
        if (!inUl) { closeLists(); html += '<ul class=\"list-disc pl-5 space-y-1\">'; inUl = true; }
        const content = tNorm.replace(bulletRegex, "");
        const cbMatch = content.match(/^\[(x|X|\s)\]\s*(.*)$/);
        if (cbMatch) {
          const checked = /x|X/.test(cbMatch[1]);
          html += `<li class=\"flex items-start gap-2\"><input type=\"checkbox\" disabled ${checked ? "checked" : ""} class=\"mt-1\"/>${boldInline(cbMatch[2])}</li>`;
        } else {
          html += `<li>${boldInline(content)}</li>`;
        }
        continue;
      }
      const isOrdered = numRegex.test(tNorm) || alphaRegex.test(tNorm) || romanRegex.test(tNorm);
      if (isOrdered) {
        flushTable();
        if (!inOl) { closeLists(); html += '<ol class=\"pl-5 space-y-1 list-none\">'; inOl = true; olCounter = 0; }
        const stripped = tNorm.replace(numRegex, "").replace(alphaRegex, "").replace(romanRegex, "");
        olCounter += 1;
        html += `<li class=\"flex items-start gap-2\"><span class=\"text-gray-500 select-none\">${olCounter}.<\/span><span>${boldInline(stripped)}<\/span><\/li>`;
        continue;
      }
      // Markdown table row
      if (/^\|.*\|$/.test(tNorm)) {
        closeLists(); flushCode(); flushKV();
        const cols = tNorm.slice(1, -1).split("|").map((c) => c.trim());
        if (!inTable) { inTable = true; tableRows = []; }
        tableRows.push(cols);
        continue;
      } else if (inTable) {
        flushTable();
      }
      // Key-Value row (generic)
      const kvMatch = tNorm.match(/^([^:]{2,}):\s*(.+)$/);
      if (kvMatch) {
        const key = kvMatch[1].trim();
        const val = kvMatch[2].trim();
        if (looksLikeKeyValue(key, val)) {
          closeLists(); flushCode(); flushTable();
          inKV = true;
          kvRows.push([key, val]);
          continue;
        }
        // If not a true KV pair, fall through to normal paragraph rendering
      } else if (inKV) {
        flushKV();
      }
      // Subheading ending with ':'
      if (/^[^:]{2,}:$/.test(tNorm)) { closeLists(); flushTable(); flushKV(); html += `<div class=\"font-semibold text-gray-900 mt-2 mb-1\">${boldInline(tNorm)}</div>`; continue; }
      // Hashtags line -> chips
      const tags = tNorm.match(/#[^\s#]+/g);
      if (tags && tags.length >= 2) {
        closeLists(); flushTable(); flushKV();
        html += `<div class=\"flex flex-wrap gap-1 mb-2\">` + tags.map((tag) => `<span class=\"px-2 py-1 rounded-full bg-gray-100 text-gray-700 text-xs\">${escapeHtml(tag)}</span>`).join("") + `</div>`;
        continue;
      }
      // Default paragraph
      closeLists(); flushTable(); flushKV();
      html += `<p class=\"mb-2\">${boldInline(tNorm)}</p>`;
    }
    closeLists(); flushCode(); flushTable(); flushKV(); flushCallout();

    return fixLinksInHtml(html);
  } catch {
    return fixLinksInHtml(String(raw || "").replace(/\n/g, "<br/>"));
  }
}

function getApiPaths(path: string) {
  const apiUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
  let base = apiUrl;
  if (!base) {
    const host = process.env.NEXT_PUBLIC_SERVER_HOST || "localhost";
    const port = process.env.NEXT_PUBLIC_API_PORT || "1979";
    base = `http://${host}:${port}`;
  }
  return {
    relative: path,
    absolute: base ? `${base}${path}` : null,
  };
}

async function writeChart(userId: string, query: string, context: string): Promise<string | null> {
  try {
    const paths = getApiPaths("/api/v1/chart");
    let res: Response | null = null;
    try {
      res = await fetch(paths.relative, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId || "default", query, context }),
      });
    } catch (e) {
      if (paths.absolute) {
        res = await fetch(paths.absolute, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId || "default", query, context }),
        });
      } else {
        throw e;
      }
    }
    if (!res.ok) return null;
    const data = await res.json();
    return data?.data || null;
  } catch (e) {
    console.error("writeChart error", e);
    return null;
  }
}

type ChatbotType = "reference" | "chart";

async function streamChat(
  chatbotType: ChatbotType,
  payload: any,
  onChunk: (text: string) => void,
  onGenerateChartFlag: () => void,
  onMeta: (metadata: any) => void
) {
  const pathStream = chatbotType === "chart" ? "/api/v1/chatbot-chart-stream" : "/api/v1/chatbot-custom-prompt-stream";
  const pathsStream = getApiPaths(pathStream);
  let res: Response | null = null;
  // Prefer absolute to avoid proxy buffering; fallback to relative
  if (pathsStream.absolute) {
    try {
      res = await fetch(pathsStream.absolute, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream,application/json" },
        body: JSON.stringify(payload),
      });
    } catch (e) {
      // try relative as fallback
      try {
        res = await fetch(pathsStream.relative, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "text/event-stream,application/json" },
          body: JSON.stringify(payload),
        });
      } catch (ee) {
        res = null;
      }
    }
  } else {
    try {
      res = await fetch(pathsStream.relative, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream,application/json" },
        body: JSON.stringify(payload),
      });
    } catch (e) {
      res = null;
    }
  }

  if (!res || !res.ok) {
    // Fallback: try non-stream endpoint to avoid breaking UX
    try {
      const pathNonStream = chatbotType === "chart" ? "/api/v1/chatbot-chart" : "/api/v1/chatbot-custom-prompt";
      const pathsNon = getApiPaths(pathNonStream);
      let nonRes: Response | null = null;
      try {
        nonRes = await fetch(pathsNon.relative, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch (e) {
        if (pathsNon.absolute) {
          nonRes = await fetch(pathsNon.absolute, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
        } else {
          throw e;
        }
      }
      if (!nonRes.ok) {
        const errText = await nonRes.text();
        console.warn("Fallback error:", errText);
        onChunk("Xin lỗi, hệ thống đang gặp sự cố và chưa thể trả lời.");
        return;
      }
      const data = await nonRes.json();
      const answer = data?.data?.answer ?? data?.data ?? "";
      const reference = data?.data?.reference ?? null;
      if (answer) onChunk(String(answer));
      if (reference) onMeta({ reference });
      return;
    } catch (e) {
      console.warn("Stream fallback failed", e);
      onChunk("Xin lỗi, hệ thống đang gặp sự cố và chưa thể trả lời.");
      return;
    }
  }

  const reader = res.body?.getReader();
  if (!reader) {
    const text = await res.text();
    onChunk(text);
    return;
  }

  const decoder = new TextDecoder();
  let sseBuffer = "";
  let sawDone = false;
  const extractNextEvent = () => {
    const idxCRLF = sseBuffer.indexOf("\r\n\r\n");
    const idxLF = sseBuffer.indexOf("\n\n");
    let idx = -1;
    let delimLen = 0;
    if (idxCRLF >= 0 && idxLF >= 0) {
      idx = Math.min(idxCRLF, idxLF);
      delimLen = idx === idxCRLF ? 4 : 2;
    } else if (idxCRLF >= 0) {
      idx = idxCRLF;
      delimLen = 4;
    } else if (idxLF >= 0) {
      idx = idxLF;
      delimLen = 2;
    }
    if (idx < 0) return null;
    const ev = sseBuffer.slice(0, idx);
    sseBuffer = sseBuffer.slice(idx + delimLen);
    return ev;
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    if (!chunk) continue;
    sseBuffer += chunk;
    let evRaw: string | null;
    while ((evRaw = extractNextEvent()) !== null) {
      const lines = evRaw.split(/\r?\n/);
      const dataParts: string[] = [];
      for (const line of lines) {
        const m = line.match(/^\s*data\s*:\s?(.*)$/);
        if (m) dataParts.push(m[1]);
      }
      if (dataParts.length === 0) continue;
      const payloadStr = dataParts.join("\n");
      const trimmed = payloadStr.trim();
      if (trimmed === "[DONE]") {
        sawDone = true;
        break;
      }
      // Chart sentinel support if content is plain text
      if (trimmed.includes(CHART_SENTINEL)) {
        onGenerateChartFlag();
      }
      // Try JSON first, fallback to plain text
      try {
        const obj = JSON.parse(trimmed);
        if (obj && typeof obj === "object") {
          if (obj.metadata) {
            onMeta(obj.metadata);
            continue;
          }
          if (obj.content != null) {
            const text = String(obj.content);
            if (text.includes(CHART_SENTINEL)) onGenerateChartFlag();
            onChunk(text);
            continue;
          }
        }
        // If object but no known keys, emit its string form
        onChunk(String(obj));
      } catch {
        onChunk(trimmed);
      }
    }
    if (sawDone) break;
  }

  // Parse any remaining buffered event(s) after stream ends
  let leftover: string | null;
  while ((leftover = extractNextEvent()) !== null && !sawDone) {
    const lines = leftover.split(/\r?\n/);
    const dataParts: string[] = [];
    for (const line of lines) {
      const m = line.match(/^\s*data\s*:\s?(.*)$/);
      if (m) dataParts.push(m[1]);
    }
    if (dataParts.length === 0) continue;
    const payloadStr = dataParts.join("\n");
    const trimmed = payloadStr.trim();
    if (trimmed === "[DONE]") break;
    try {
      const obj = JSON.parse(trimmed);
      if (obj?.metadata) {
        onMeta(obj.metadata);
        continue;
      }
      if (obj?.content != null) {
        onChunk(String(obj.content));
        continue;
      }
      onChunk(String(obj));
    } catch {
      onChunk(trimmed);
    }
  }
}

export default function ModernChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [systemInstructionUser, setSystemInstructionUser] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [refToggle, setRefToggle] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [userId] = useState<string>("default");
  const [pendingChart, setPendingChart] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string>("");
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [imageFiles, setImageFiles] = useState<File[]>([]);
  const [imageAnalysisText, setImageAnalysisText] = useState<string>("");
  const [showPlusMenu, setShowPlusMenu] = useState<boolean>(false);
  const [showEmojiMenu, setShowEmojiMenu] = useState<boolean>(false);
  const assistantStreamingIdRef = useRef<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!sessionId) setSessionId(generateRandomHistoryId());
  }, [sessionId]);

  useEffect(() => {
    if (uploadSuccess) {
      const t = setTimeout(() => setUploadSuccess(false), 5000);
      return () => clearTimeout(t);
    }
  }, [uploadSuccess]);

  useEffect(() => {
    if (uploadError) {
      const t = setTimeout(() => setUploadError(null), 7000);
      return () => clearTimeout(t);
    }
  }, [uploadError]);

  const handleSendMessage = async () => {
    if (input.trim() === "" && imageFiles.length === 0) return;

    const now = Date.now();
    const defaultSingle = "Phân tích ảnh và cảm nhận hình ảnh này";
    const defaultTwo = "Phân tích ảnh và cảm nhận hai hình ảnh này";
    const imageCount = Math.min(imagePreviews.length, imageFiles.length);
    const autoText = imageCount >= 2 ? defaultTwo : defaultSingle;
    const textToSend = input.trim() !== "" ? input.trim() : autoText;
    const contentToSend: any = imagePreviews.length > 0
      ? { text: textToSend, images: imagePreviews.slice(0, 2) }
      : textToSend;
    const userMessage: ChatMessage = {
      id: now.toString(),
      role: "user",
      content: contentToSend,
      timestamp: now,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);
    setPendingChart(false);

    const queryLower = String(
      typeof userMessage.content === "string" ? userMessage.content : userMessage.content?.text || ""
    ).toLowerCase();
    let chatbotType: ChatbotType = "reference";
    const chartKeywords = [
      "biểu đồ", "đồ thị", "chart", "plot", "graph", "vẽ", "draw", "visualize",
    ];
    // Chỉ bật chế độ chart khi có từ khóa đặc thù của biểu đồ
    if (chartKeywords.some((kw) => queryLower.includes(kw))) {
      chatbotType = "chart";
    }
    // Nếu là tin nhắn mặc định khi có ảnh, không kích hoạt chart
    const defaultSet = [defaultSingle.toLowerCase(), defaultTwo.toLowerCase()];
    if (imageFiles.length > 0 && defaultSet.includes(queryLower)) {
      chatbotType = "reference";
    }

    let imageTextToSend = imageAnalysisText;
    if (!imageTextToSend && imageFiles.length > 0) {
      const texts: string[] = [];
      for (const f of imageFiles.slice(0, 2)) {
        const t = await analyzeImageFile(f);
        if (t) texts.push(t);
      }
      imageTextToSend = texts.join("\n\n---\n");
      setImageAnalysisText(imageTextToSend);
    }

    const payload = {
      user_id: userId,
      query: typeof userMessage.content === "string" ? userMessage.content : userMessage.content?.text || "",
      collections: [DEFAULT_COLLECTION],
      session_id: sessionId,
      history_id: "",
      system_instruction_user: systemInstructionUser,
      include_products: true,
      image_text: imageTextToSend || "",
    };

    // Xóa preview ảnh khỏi khung nhập ngay sau khi chuẩn bị payload
    setImagePreviews([]);
    setImageFiles([]);
    setShowPlusMenu(false);
    setShowEmojiMenu(false);
    if (fileInputRef.current) fileInputRef.current.value = "";

    const assistantId = (Date.now() + 1).toString();
    assistantStreamingIdRef.current = assistantId;

    let fullAnswer = "";
    await streamChat(
      chatbotType,
      payload,
      (chunk) => {
        fullAnswer += chunk;
        setMessages((prev) => {
          const exists = prev.some((m) => m.id === assistantId && m.role === "assistant");
          if (!exists) {
            return [
              ...prev,
              { id: assistantId, role: "assistant", content: fullAnswer, timestamp: Date.now() },
            ];
          }
          return prev.map((m) => (m.id === assistantId && m.role === "assistant") ? { ...m, content: fullAnswer } : m);
        });
      },
      () => {
        setPendingChart(true);
        const updatedContent = `${fullAnswer}\n\nBiểu đồ đang được tạo. Vui lòng đợi trong giây lát...`;
        setMessages((prev) => {
          const exists = prev.some((m) => m.id === assistantId && m.role === "assistant");
          if (!exists) {
            return [
              ...prev,
              { id: assistantId, role: "assistant", content: updatedContent, timestamp: Date.now() },
            ];
          }
          return prev.map((m) => (m.id === assistantId && m.role === "assistant") ? { ...m, content: updatedContent } : m);
        });
      },
      (metadata) => {
        // Append reference or chart metadata entries
        if (metadata?.reference) {
          setMessages((prev) => [
            ...prev,
            { id: `${Date.now()}-ref`, role: "reference", content: metadata.reference, timestamp: Date.now() },
          ]);
        }
        if (metadata?.chart) {
          setMessages((prev) => [
            ...prev,
            { id: `${Date.now()}-chartmeta`, role: "chart", content: metadata.chart, timestamp: Date.now() },
          ]);
        }
      }
    );

    if (chatbotType === "chart") {
      const chartHtml = await writeChart(userId, String(userMessage.content), fullAnswer);
      if (chartHtml) {
        setMessages((prev) => [
          ...prev,
          { id: `${Date.now()}-chart`, role: "chart", content: chartHtml, timestamp: Date.now() },
        ]);
      }
    }

    setIsTyping(false);
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
    setShowPlusMenu(false);
  };

  const analyzeImageFile = async (imageFile: File): Promise<string> => {
    try {
      const form = new FormData();
      form.append("file", imageFile);
      const paths = getApiPaths("/api/v1/analyze-image");
      let res: Response | null = null;
      try {
        res = await fetch(paths.relative, { method: "POST", body: form });
      } catch (err) {
        if (paths.absolute) {
          res = await fetch(paths.absolute, { method: "POST", body: form });
        } else {
          throw err;
        }
      }
      if (res && res.ok) {
        const data = await res.json();
        return String(data?.data?.image_text || "");
      }
      return "";
    } catch {
      return "";
    }
  };

  const handleFileSelected = async (e: any) => {
    const files: File[] = Array.from(e?.target?.files || []);
    if (files.length === 0) return;
    setUploadError(null);

    const imageCandidates = files.filter((f) => f.type?.startsWith("image/"));
    const nonImage = files.find((f) => !f.type?.startsWith("image/"));

    if (imageCandidates.length > 0) {
      try {
        let added = 0;
        for (const file of imageCandidates) {
          if (imageFiles.length + added >= 2) {
            setUploadError("Chỉ cho phép tối đa 2 hình ảnh cho mỗi lần gửi.");
            break;
          }
          const url = URL.createObjectURL(file);
          setImagePreviews((prev) => [...prev, url]);
          setImageFiles((prev) => [...prev, file]);
          const analysis = await analyzeImageFile(file);
          if (analysis) {
            setImageAnalysisText((prev) => prev ? `${prev}\n\n---\n${analysis}` : analysis);
          }
          added += 1;
        }
      } catch (err: any) {
        setUploadError(String(err?.message || err));
      } finally {
        if (fileInputRef.current) fileInputRef.current.value = "";
      }
      return;
    }

    if (nonImage) {
      // File không phải ảnh: quy trình upload bình thường
      setIsUploading(true);
      try {
        const form = new FormData();
        form.append("user_id", userId || "default");
        form.append("collection_name", DEFAULT_COLLECTION);
        form.append("file", nonImage);
        form.append("language", "vie+eng");
        form.append("note", "");

        const paths = getApiPaths("/api/v1/upload-to-collection");
        let res: Response | null = null;
        try {
          res = await fetch(paths.relative, { method: "POST", body: form });
        } catch (err) {
          if (paths.absolute) {
            res = await fetch(paths.absolute, { method: "POST", body: form });
          } else {
            throw err;
          }
        }
        if (!res || !res.ok) {
          const msg = await (res ? res.text() : Promise.resolve("Network error"));
          setUploadError(msg || "Upload failed");
        } else {
          let data: any = null;
          try {
            data = await res.json();
          } catch {
            data = null;
          }
          const fileName = nonImage?.name || "tập tin";
          const points = data?.total_saved_points ?? data?.count ?? null;
          const msgParts: string[] = [];
          msgParts.push(`Đã tải và xử lý xong: ${fileName}`);
          if (typeof points === "number") msgParts.push(`(${points} đoạn)`);
          setUploadMessage(msgParts.join(" "));
          setUploadSuccess(true);
        }
      } catch (err: any) {
        setUploadError(String(err?.message || err));
      } finally {
        setIsUploading(false);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }
    }
  };

  const handlePaste = async (e: any) => {
    try {
      const items = e.clipboardData?.items || [];
      for (let i = 0; i < items.length; i++) {
        const it = items[i];
        if (it && it.type && it.type.startsWith("image/")) {
          if (imageFiles.length >= 2) {
            setUploadError("Chỉ cho phép tối đa 2 hình ảnh cho mỗi lần gửi.");
            break;
          }
          const blob = it.getAsFile();
          if (!blob) continue;
          const file = new File([blob], `pasted-${Date.now()}.png`, { type: blob.type || "image/png" });
          const url = URL.createObjectURL(blob);
          setImagePreviews((prev) => [...prev, url]);
          setImageFiles((prev) => [...prev, file]);
          const analysis = await analyzeImageFile(file);
          if (analysis) {
            setImageAnalysisText((prev) => prev ? `${prev}\n\n---\n${analysis}` : analysis);
          }
          if (imageFiles.length + 1 >= 2) break;
        }
      }
    } catch (err) {
      console.warn("Paste image failed", err);
    }
  };

  const removeImageAt = (index: number) => {
    setImagePreviews((prev) => prev.filter((_, i) => i !== index));
    setImageFiles((prev) => prev.filter((_, i) => i !== index));
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const insertEmoji = (emoji: string) => {
    setInput((prev) => (prev || "") + emoji);
    inputRef.current?.focus();
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen bg-white">
        <AppSidebar />

        {/* Main Content */}
        <div className="flex flex-col flex-1 relative">
          {/* Header */}
          <Header />

          {/* Messages / Empty State */}
          {messages.length === 0 ? (
            <main className="flex-1 bg-gray-50 flex items-center justify-center px-4 md:px-6">
              <div className="max-w-2xl w-full mx-auto flex flex-col items-center">
                <h1 className="text-5xl font-semibold tracking-tight text-gray-900 mb-6 select-none">MEKONGAI</h1>
                <div className="flex items-center gap-2 w-full">
                  <div className="flex-1">
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      className="hidden"
                      onChange={handleFileSelected}
                    />
                    {imagePreviews.length > 0 && (
                      <div className="mb-3 flex flex-wrap gap-2">
                        {imagePreviews.map((preview, idx) => (
                          <div key={idx} className="inline-block relative">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img
                              src={preview}
                              alt="attachment-preview"
                              className="w-28 h-28 rounded-xl border border-gray-200 object-cover bg-white"
                            />
                            <button
                              onClick={() => removeImageAt(idx)}
                              className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-black text-white text-sm flex items-center justify-center"
                              title="Xóa ảnh"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="relative">
                      <input
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onPaste={handlePaste}
                        onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                        placeholder="Bạn muốn biết điều gì?"
                        className="w-full px-5 py-3.5 pl-24 pr-14 rounded-2xl border-2 border-gray-200 focus:border-black focus:outline-none transition-all bg-white shadow-sm text-sm placeholder:text-gray-400"
                      />
                      <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                        <div className="relative">
                          <button
                            onClick={() => setShowPlusMenu((s) => !s)}
                            disabled={isUploading}
                            className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                            title={isUploading ? "Đang tải..." : "Thêm"}
                          >
                            <Plus className="w-5 h-5 text-gray-400" />
                          </button>
                          {showPlusMenu && (
                            <div className="absolute z-10 mt-2 w-56 rounded-xl border border-gray-200 bg-white shadow-md p-2">
                              <button
                                onClick={handleAttachClick}
                                className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 text-sm"
                              >
                                Add photos & files
                              </button>
                            </div>
                          )}
                        </div>
                        <div className="relative">
                          <button
                            onClick={() => setShowEmojiMenu((s) => !s)}
                            className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                            title="Emoji"
                          >
                            <Smile className="w-5 h-5 text-gray-400" />
                          </button>
                          {showEmojiMenu && (
                            <div className="absolute z-10 mt-2 w-36 rounded-xl border border-gray-200 bg-white shadow-md p-2 flex flex-wrap gap-1">
                              {['😀','😊','👍','❤️','🔥','🎉','🙏','🤔','😎','🥳'].map((e) => (
                                <button
                                  key={e}
                                  onClick={() => { insertEmoji(e); setShowEmojiMenu(false); }}
                                  className="px-2 py-1 rounded hover:bg-gray-50 text-lg"
                                  aria-label={`emoji-${e}`}
                                >
                                  {e}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={handleSendMessage}
                        disabled={!input.trim() && imageFiles.length === 0}
                        className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-black text-white hover:bg-gray-800 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                      >
                        <Send className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                  
                </div>
                {isUploading && (
                  <p className="text-xs text-blue-600 text-center mt-2">Đang tải và xử lý tài liệu...</p>
                )}
                {uploadSuccess && uploadMessage && (
                  <p className="text-xs text-green-600 text-center mt-2" aria-live="polite">{uploadMessage}</p>
                )}
                {uploadError && (
                  <p className="text-xs text-red-600 text-center mt-2" aria-live="polite">{uploadError}</p>
                )}
                <p className="text-xs text-gray-400 text-center mt-3">
                  AI có thể mắc lỗi. Hãy kiểm tra thông tin quan trọng.
                </p>
              </div>
            </main>
          ) : (
          <main className="flex-1 overflow-y-auto px-4 md:px-6 py-6 bg-gray-50">
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Reference toggle */}
              {/* <div className="flex items-center justify-end gap-3">
                <label className="text-sm text-gray-600">Hiển thị tham chiếu</label>
                <input
                  type="checkbox"
                  checked={refToggle}
                  onChange={(e) => setRefToggle(e.target.checked)}
                />
              </div> */}

              {messages.filter((m) => !(m.role === "reference" && !refToggle)).map((message, index) => (
                <div
                  key={message.id}
                  className={`flex items-start gap-3 ${
                    message.role === "user" ? "flex-row-reverse" : ""
                  } animate-in fade-in slide-in-from-bottom-4 duration-500`}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div
                    className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-md ${
                      message.role === "user" ? "bg-white border border-gray-200" : "bg-black"
                    }`}
                  >
                    {message.role === "user" ? (
                      <Image src="/OIP.webp" alt="KAT" width={20} height={20} className="rounded-sm object-contain" />
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>
                  <div className={`flex flex-col gap-1 max-w-[70%] ${message.role === "user" ? "items-end" : "items-start"}`}>
                    {message.role === "reference" ? (
                      refToggle ? (
                        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm w-full">
                          {Array.isArray(message.content) ? (
                            message.content.map((md: any, idx: number) => (
                              <details key={idx} className="mb-2">
                                <summary className="cursor-pointer text-sm font-medium">{md.title || `Tham chiếu #${idx+1}`}</summary>
                                <div className="mt-2">
                                  {typeof md.content === "string" ? (
                                    <div className="prose max-w-none text-sm" dangerouslySetInnerHTML={{ __html: fixLinksInHtml(md.content.replace(/\n/g, "\n\n")) }} />
                                  ) : (
                                    <pre className="text-xs bg-gray-50 p-2 rounded border border-gray-200 overflow-auto">{JSON.stringify(md.content, null, 2)}</pre>
                                  )}
                                </div>
                              </details>
                            ))
                          ) : (
                            <pre className="text-xs bg-gray-50 p-2 rounded border border-gray-200 overflow-auto">{JSON.stringify(message.content, null, 2)}</pre>
                          )}
                        </div>
                      ) : null
                    ) : message.role === "chart" ? (
                      <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm w-full">
                        <div dangerouslySetInnerHTML={{ __html: String(message.content) }} />
                      </div>
                    ) : (
                      <div className={`rounded-2xl px-4 py-3 shadow-sm ${message.role === "user" ? "bg-white border border-gray-200 text-gray-800 rounded-tr-md" : "bg-white border border-gray-200 text-gray-800 rounded-tl-md"}`}>
                        {message.role === "assistant" ? (
                          <div className="text-sm leading-relaxed prose max-w-none" dangerouslySetInnerHTML={{ __html: formatAssistantHtml(String(message.content || "")) }} />
                        ) : (
                          typeof message.content === "string" ? (
                            <p className="text-sm leading-relaxed">{String(message.content)}</p>
                          ) : (
                            <div className="flex flex-col gap-2">
                              {Array.isArray(message.content?.images) && message.content.images.length > 0 && (
                                <div className="flex flex-wrap gap-2">
                                  {/* eslint-disable-next-line @next/next/no-img-element */}
                                  {message.content.images.map((src: string, idx: number) => (
                                    <img
                                      key={idx}
                                      src={src}
                                      alt={`attachment-${idx}`}
                                      className="w-36 h-36 rounded-xl object-cover border border-gray-200"
                                    />
                                  ))}
                                </div>
                              )}
                              <p className="text-sm leading-relaxed">{String(message.content?.text || "")}</p>
                            </div>
                          )
                        )}
                      </div>
                    )}
                    <span className="text-xs text-gray-400 px-2">
                      {formatTime(new Date(message.timestamp))}
                    </span>
                  </div>
                </div>
              ))}

              {/* Typing Indicator: only until first assistant chunk appears */}
              {isTyping && !messages.some((m) => m.id === assistantStreamingIdRef.current && m.role === "assistant") && (
                <div className="flex items-start gap-3 animate-in fade-in slide-in-from-bottom-4">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-black flex items-center justify-center shadow-md">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
                    <div className="flex gap-1.5">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </main>

          
          )}
          {messages.length > 0 && (
            <footer className="bg-white border-t border-gray-200 px-4 md:px-6 py-4 shadow-sm">
              <div className="max-w-4xl mx-auto">
                <div className="mb-3">
                  <button
                    className="text-xs text-gray-600 hover:text-gray-900 underline"
                    onClick={() => setShowAdvanced((s) => !s)}
                  >
                    {showAdvanced ? "Ẩn hướng dẫn hệ thống" : "Hiển thị hướng dẫn hệ thống"}  
                  </button>
                  {showAdvanced && (
                    <textarea
                      value={systemInstructionUser}
                      onChange={(e) => setSystemInstructionUser(e.target.value)}
                      placeholder="Nhập hướng dẫn hệ thống dành cho User..."
                      className="mt-2 w-full px-3 py-2 rounded-xl border-2 border-gray-200 focus:border-black focus:outline-none text-sm"
                      rows={3}
                    />
                  )}
                </div>
                {isUploading && (
                  <p className="text-xs text-blue-600 mt-2">Đang tải và xử lý tài liệu...</p>
                )}
                {uploadSuccess && uploadMessage && (
                  <p className="text-xs text-green-600 mt-2" aria-live="polite">{uploadMessage}</p>
                )}
                {uploadError && (
                  <p className="text-xs text-red-600 mt-2" aria-live="polite">{uploadError}</p>
                )}
                <div className="flex items-center gap-2">
                  <div className="flex-1">
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    className="hidden"
                    onChange={handleFileSelected}
                  />
                  {imagePreviews.length > 0 && (
                    <div className="mb-3 flex flex-wrap gap-2">
                      {imagePreviews.map((preview, idx) => (
                        <div key={idx} className="inline-block relative">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={preview}
                            alt="attachment-preview"
                            className="w-28 h-28 rounded-xl border border-gray-200 object-cover bg-white"
                          />
                          <button
                            onClick={() => removeImageAt(idx)}
                            className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-black text-white text-sm flex items-center justify-center"
                            title="Xóa ảnh"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                    <div className="relative">
                      <input
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onPaste={handlePaste}
                        onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                        placeholder="Nhập tin nhắn của bạn..."
                        className="w-full px-5 py-3.5 pl-24 pr-14 rounded-2xl border-2 border-gray-200 focus:border-black focus:outline-none transition-all bg-white shadow-sm text-sm placeholder:text-gray-400"
                      />
                      <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                    <div className="relative">
                      <button
                        onClick={() => setShowPlusMenu((s) => !s)}
                        disabled={isUploading}
                        className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                        title={isUploading ? "Đang tải..." : "Thêm"}
                      >
                        <Plus className="w-5 h-5 text-gray-400" />
                      </button>
                      {showPlusMenu && (
                        <div className="absolute z-10 mt-2 w-56 rounded-xl border border-gray-200 bg-white shadow-md p-2">
                          <button
                            onClick={handleAttachClick}
                            className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 text-sm"
                          >
                            Add photos & files
                          </button>
                        </div>
                      )}
                    </div>
                    <div className="relative">
                      <button
                        onClick={() => setShowEmojiMenu((s) => !s)}
                        className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Emoji"
                      >
                        <Smile className="w-5 h-5 text-gray-400" />
                      </button>
                      {showEmojiMenu && (
                        <div className="absolute z-10 mt-2 w-36 rounded-xl border border-gray-200 bg-white shadow-md p-2 flex flex-wrap gap-1">
                          {['😀','😊','👍','❤️','🔥','🎉','🙏','🤔','😎','🥳'].map((e) => (
                            <button
                              key={e}
                              onClick={() => { insertEmoji(e); setShowEmojiMenu(false); }}
                              className="px-2 py-1 rounded hover:bg-gray-50 text-lg"
                              aria-label={`emoji-${e}`}
                            >
                              {e}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                      </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!input.trim() && imageFiles.length === 0}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-black text-white hover:bg-gray-800 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
                    </div>
                  </div>
                  
                </div>
                <p className="text-xs text-gray-400 text-center mt-3">
                  AI có thể mắc lỗi. Hãy kiểm tra thông tin quan trọng.
                </p>
              </div>
            </footer>
          )}
        </div>
      </div>
    </SidebarProvider>
  );
}
