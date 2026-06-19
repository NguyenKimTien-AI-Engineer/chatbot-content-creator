import { create } from 'zustand';

interface ChatState {
  sessionId: string;
  setSessionId: (id: string) => void;
  historyVersion: number;
  refreshHistory: () => void;
  startNewChat: () => string;
}

function persistSession(id: string) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem('chat_selected_conversation', id);
  } catch {
    /* noop */
  }
}

export function readStoredSessionId(): string {
  if (typeof window === 'undefined') return '';
  try {
    return localStorage.getItem('chat_selected_conversation') || '';
  } catch {
    return '';
  }
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessionId: '',
  setSessionId: (id) => {
    persistSession(id);
    set({ sessionId: id });
  },
  historyVersion: 0,
  refreshHistory: () => set({ historyVersion: get().historyVersion + 1 }),
  startNewChat: () => {
    const id = Math.random().toString(36).slice(2, 12);
    persistSession(id);
    set({ sessionId: id });
    return id;
  },
}));
