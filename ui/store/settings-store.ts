import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export type ThemeMode = 'light' | 'dark' | 'system';
export type Language = 'vi' | 'en';

export interface AppSettings {
  displayName: string;
  email: string;
  userId: string;

  chatModel: string;
  miniModel: string;
  temperature: number;
  streamingEnabled: boolean;

  defaultCollection: string;
  includeProducts: boolean;
  systemInstructionUser: string;
  customMainPrompt: string;
  autoSaveChat: boolean;
  showReferences: boolean;

  businessName: string;
  brandTone: string;
  defaultLanguage: Language;

  apiHost: string;
  apiPort: string;

  theme: ThemeMode;
  compactMode: boolean;
  showTimestamps: boolean;

  desktopNotifications: boolean;
  soundEnabled: boolean;
  emailDigest: boolean;

  saveChatHistory: boolean;
  analyticsEnabled: boolean;
}

export const DEFAULT_SETTINGS: AppSettings = {
  displayName: 'User',
  email: '',
  userId: 'default',

  chatModel: 'gemini-2.5-flash',
  miniModel: 'gemini-2.5-flash-lite',
  temperature: 0,
  streamingEnabled: true,

  defaultCollection: 'CHATBOT_MekongAI_d41b1532-bf75-481d-ad6d-b7dac8cbae4d',
  includeProducts: true,
  systemInstructionUser: '',
  customMainPrompt: '',
  autoSaveChat: true,
  showReferences: true,

  businessName: 'KAT Leather',
  brandTone: 'Refined, premium, friendly',
  defaultLanguage: 'en',

  apiHost: 'localhost',
  apiPort: '1979',

  theme: 'light',
  compactMode: false,
  showTimestamps: true,

  desktopNotifications: false,
  soundEnabled: true,
  emailDigest: false,

  saveChatHistory: true,
  analyticsEnabled: false,
};

interface SettingsState {
  settings: AppSettings;
  isDirty: boolean;
  setSetting: <K extends keyof AppSettings>(key: K, value: AppSettings[K]) => void;
  patchSettings: (patch: Partial<AppSettings>) => void;
  resetSettings: () => void;
  markClean: () => void;
  exportSettings: () => string;
  importSettings: (json: string) => boolean;
}

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set, get) => ({
        settings: DEFAULT_SETTINGS,
        isDirty: false,

        setSetting: (key, value) =>
          set((state) => ({
            settings: { ...state.settings, [key]: value },
            isDirty: true,
          })),

        patchSettings: (patch) =>
          set((state) => ({
            settings: { ...state.settings, ...patch },
            isDirty: true,
          })),

        resetSettings: () =>
          set({ settings: DEFAULT_SETTINGS, isDirty: true }),

        markClean: () => set({ isDirty: false }),

        exportSettings: () => JSON.stringify(get().settings, null, 2),

        importSettings: (json) => {
          try {
            const parsed = JSON.parse(json) as Partial<AppSettings>;
            set({
              settings: { ...DEFAULT_SETTINGS, ...parsed },
              isDirty: true,
            });
            return true;
          } catch {
            return false;
          }
        },
      }),
      {
        name: 'mekongai-settings',
        partialize: (state) => ({ settings: state.settings }),
        onRehydrateStorage: () => (state) => {
          if (state) state.isDirty = false;
        },
      }
    ),
    { name: 'settings-store' }
  )
);

export function applyTheme(theme: ThemeMode) {
  if (typeof document === 'undefined') return;

  const root = document.documentElement;
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isDark = theme === 'dark' || (theme === 'system' && prefersDark);

  root.classList.toggle('dark', isDark);
}

export function syncLegacyStorage(settings: AppSettings) {
  if (typeof window === 'undefined') return;

  localStorage.setItem('user_id', settings.userId);
  localStorage.setItem(
    'user',
    JSON.stringify({ name: settings.displayName, email: settings.email })
  );

  if (settings.customMainPrompt) {
    localStorage.setItem('edited_main_prompt', settings.customMainPrompt);
  }

  localStorage.setItem('mekongai_api_host', settings.apiHost);
  localStorage.setItem('mekongai_api_port', settings.apiPort);
}
