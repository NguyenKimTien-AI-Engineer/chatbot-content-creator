import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { ContentHistoryItem, ContentHistoryDetail, SessionInfo } from '@/lib/api';

export interface ContentFormData {
  business_name: string;
  business_type: string;
  target_audience: string;
  content_topic: string;
  tone: string;
  // Fanpage specific fields
  post_type?: string;
  product_input_method?: string;
  product_type?: string;
  specific_product?: string;
  color?: string;
  custom_product_name?: string;
  custom_product_price?: string;
  custom_product_description?: string;
  customer_segments?: string[];
  specific_targets?: string[];
  main_objectives?: string[];
  funnel_objectives?: string[];
  platforms?: string[];
  content_pillars?: string[];
  content_funnel?: string[];
  main_message?: string;
  content_length?: string;
  hook_length?: string;
  num_posts?: string;
  aggregation_options?: string[];
}

export interface GeneratedContent {
  post_content: string;
  caption: string;
  hashtags: string[];
  created_at: string;
  id?: string;
}

interface ContentState {
  // Form data
  formData: ContentFormData;
  setFormData: (data: Partial<ContentFormData>) => void;
  resetFormData: () => void;

  // Generated content
  generatedContent: GeneratedContent | null;
  setGeneratedContent: (content: GeneratedContent) => void;
  clearGeneratedContent: () => void;

  // Loading states
  isGenerating: boolean;
  setIsGenerating: (loading: boolean) => void;

  // Content history
  contentHistory: GeneratedContent[];
  setContentHistory: (history: GeneratedContent[]) => void;
  addToHistory: (content: GeneratedContent) => void;

  // Content history from database
  savedContentHistory: ContentHistoryItem[];
  setSavedContentHistory: (history: ContentHistoryItem[]) => void;
  addToSavedHistory: (content: ContentHistoryItem) => void;
  
  // Content history detail
  selectedHistoryDetail: ContentHistoryDetail | null;
  setSelectedHistoryDetail: (detail: ContentHistoryDetail | null) => void;

  // Loading states for history
  isLoadingHistory: boolean;
  setIsLoadingHistory: (loading: boolean) => void;

  // History cache management
  isHistoryLoaded: boolean;
  setIsHistoryLoaded: (loaded: boolean) => void;
  lastHistoryFetch: number | null;
  setLastHistoryFetch: (timestamp: number) => void;

  // Templates
  templates: any[];
  setTemplates: (templates: any[]) => void;

  historySessions: SessionInfo[];
  setHistorySessions: (sessions: SessionInfo[]) => void;
  historyPreviews: Record<string, string>;
  setHistoryPreviews: (previews: Record<string, string>) => void;
  mergeHistoryPreviews: (previews: Record<string, string>) => void;
  historyHasLoaded: boolean;
  setHistoryHasLoaded: (loaded: boolean) => void;
  historyHasMore: boolean;
  setHistoryHasMore: (hasMore: boolean) => void;
  historySkip: number;
  setHistorySkip: (skip: number) => void;
  historyLimit: number;
  setHistoryLimit: (limit: number) => void;
  historyLoading: boolean;
  setHistoryLoading: (loading: boolean) => void;

  // UI states
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const initialFormData: ContentFormData = {
  business_name: '',
  business_type: '',
  target_audience: '',
  content_topic: '',
  tone: '',
  // Fanpage specific defaults
  product_input_method: 'predefined',
  num_posts: '3',
};

export const useContentStore = create<ContentState>()(
  devtools(
    persist(
      (set, get) => ({
        // Form data
        formData: initialFormData,
        setFormData: (data) =>
          set((state) => ({
            formData: { ...state.formData, ...data },
          })),
        resetFormData: () => set({ formData: initialFormData }),

        // Generated content
        generatedContent: null,
        setGeneratedContent: (content) => set({ generatedContent: content }),
        clearGeneratedContent: () => set({ generatedContent: null }),

        // Loading states
        isGenerating: false,
        setIsGenerating: (loading) => set({ isGenerating: loading }),

        // Content history
        contentHistory: [],
        setContentHistory: (history) => set({ contentHistory: history }),
        addToHistory: (content) =>
          set((state) => ({
            contentHistory: [content, ...state.contentHistory],
          })),

        // Content history from database
        savedContentHistory: [],
        setSavedContentHistory: (history) => set({ savedContentHistory: history }),
        addToSavedHistory: (content) =>
          set((state) => ({
            savedContentHistory: [content, ...state.savedContentHistory.slice(0, 9)], // Keep only 10 items
          })),

        // Content history detail
        selectedHistoryDetail: null,
        setSelectedHistoryDetail: (detail) => set({ selectedHistoryDetail: detail }),

        // Loading states for history
        isLoadingHistory: false,
        setIsLoadingHistory: (loading) => set({ isLoadingHistory: loading }),

        // History cache management
        isHistoryLoaded: false,
        setIsHistoryLoaded: (loaded) => set({ isHistoryLoaded: loaded }),
        lastHistoryFetch: null,
        setLastHistoryFetch: (timestamp) => set({ lastHistoryFetch: timestamp }),

        // Templates
        templates: [],
        setTemplates: (templates) => set({ templates }),

        historySessions: [],
        setHistorySessions: (sessions) => set({ historySessions: sessions }),
        historyPreviews: {},
        setHistoryPreviews: (previews) => set({ historyPreviews: previews }),
        mergeHistoryPreviews: (previews) =>
          set((state) => ({ historyPreviews: { ...state.historyPreviews, ...previews } })),
        historyHasLoaded: false,
        setHistoryHasLoaded: (loaded) => set({ historyHasLoaded: loaded }),
        historyHasMore: true,
        setHistoryHasMore: (hasMore) => set({ historyHasMore: hasMore }),
        historySkip: 0,
        setHistorySkip: (skip) => set({ historySkip: skip }),
        historyLimit: 20,
        setHistoryLimit: (limit) => set({ historyLimit: limit }),
        historyLoading: false,
        setHistoryLoading: (loading) => set({ historyLoading: loading }),

        // UI states
        activeTab: 'post',
        setActiveTab: (tab) => set({ activeTab: tab }),
      }),
      {
        name: 'content-store',
        partialize: (state) => ({
          savedContentHistory: state.savedContentHistory,
          isHistoryLoaded: state.isHistoryLoaded,
          lastHistoryFetch: state.lastHistoryFetch,
          historySessions: state.historySessions,
          historyPreviews: state.historyPreviews,
          historyHasLoaded: state.historyHasLoaded,
          historyHasMore: state.historyHasMore,
          historySkip: state.historySkip,
          historyLimit: state.historyLimit,
        }),
      }
    ),
    {
      name: 'content-store',
    }
  )
);