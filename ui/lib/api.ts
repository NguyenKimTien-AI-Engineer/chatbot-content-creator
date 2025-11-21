// api.ts
import axios from 'axios';

// ✅ Đơn giản, rõ ràng
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:1979';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
  },
});

function genAuthToken(length = 32): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let out = '';
  for (let i = 0; i < length; i++) out += chars[Math.floor(Math.random() * chars.length)];
  return out;
}

function getOrCreateAuthTokenSafely(): string | null {
  try {
    if (typeof window === 'undefined') return null;
    let token = localStorage.getItem('auth_token');
    if (!token) {
      token = genAuthToken();
      localStorage.setItem('auth_token', token);
    }
    return token;
  } catch {
    return null;
  }
}

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    let token: string | null = null;
    try {
      token = localStorage.getItem('auth_token');
    } catch {}
    if (!token) token = getOrCreateAuthTokenSafely();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Types
export interface ContentGenerationRequest {
  business_name: string;
  business_type: string;
  target_audience: string;
  content_topic: string;
  tone: string;
  content_type?: string;
  // Fanpage specific fields
  post_type?: string;
  product_input_method?: string;
  product_type?: string;
  specific_product?: string;
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
  aggregation_options?: string[];
  num_posts?: string;
  description_product?: string; // Add the description_product field
  // Template overrides
  template_configuration?: Record<string, any>;
  custom_prompt_yaml?: string;
}

export interface ContentGenerationResponse {
  post_content: string;
  caption: string;
  hashtags: string[];
  status: string;
  task_id?: string;
}

export interface HealthResponse {
  status: string;
  message: string;
  timestamp: string;
}

// Products API Types
export interface Product {
  id?: string;
  name: string;
  sku: string;
  pricing: {
    price: number;
    currency: string;
    cost?: number;
  };
  media: Array<{
    type: string;
    url: string;
    alt_text?: string;
  }>;
  data: {
    description: string;
    category: string[];
    quantity: number;
  };
  user_id?: string;
  company_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProductSearchRequest {
  query?: string;
  category?: string;
  limit?: number;
}

export interface ProductListResponse {
  success: boolean;
  message: string;
  data: Product[];
  total: number;
}

export interface ProductCategoryResponse {
  success: boolean;
  message: string;
  category: string;
  product_names: string[];
}

// Post Types API Types
export interface PostType {
  key: string;
  full_name: string;
  description?: string;
  active: boolean;
}

export interface PostTypeListResponse {
  success: boolean;
  message: string;
  items: PostType[];
}

export interface PostTypeCreateRequest {
  key: string;
  full_name: string;
  description?: string;
}

// Product create request
export interface ProductCreateRequest {
  name: string;
  sku?: string;
  pricing: {
    price: number;
    currency: string;
    cost?: number;
  };
  media: Array<{
    type: string;
    url: string;
    alt_text?: string;
  }>;
  data: {
    description: string;
    category: string[];
    quantity: number;
  };
}

export interface ConversationItem {
  conversation_id: string;
  user_id: string;
  created_at?: string;
  updated_at?: string;
  preview?: string;
  metadata?: Record<string, any> | null;
}

export interface ConversationListData {
  items: ConversationItem[];
  page: number;
  limit: number;
  total: number;
}

// History API Types
export interface HistoryItem {
  history_id: string;
  user_id: string;
  session_id: string;
  query: string;
  answer: string;
  feedback?: string;
  feedback_status?: string;
  reference?: any[];
  chart?: any;
  image_url?: string;
  timestamp?: string;
  created_at?: string;
}

export interface HistoryCreateRequest {
  user_id: string;
  session_id: string;
  query: string;
  answer: string;
  feedback?: string;
  feedback_status?: string;
  reference?: any[];
  chart?: any;
  image_url?: string;
}

export interface HistoryListResponse {
  success: boolean;
  message: string;
  data: HistoryItem[];
  total: number;
  page: number;
  limit: number;
}

export interface HistoryCreateResponse {
  success: boolean;
  message: string;
  data: {
    history_id: string;
    inserted_id: string;
  };
}

export interface HistoryDeleteResponse {
  success: boolean;
  message: string;
}

export interface SessionInfo {
  session_id: string;
  user_id: string;
  last_activity?: string;
  created_at?: string;
  updated_at?: string;
  preview?: string;
}

export interface SessionsResponse {
  success: boolean;
  message: string;
  data: SessionInfo[];
  total: number;
}

export interface DeleteSessionResponse {
  success: boolean;
  message: string;
}

// API Functions
export const api = {
  // Health check
  health: async (): Promise<HealthResponse> => {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  },

  // Generate fanpage content
  generateFanpageContent: async (data: ContentGenerationRequest): Promise<ContentGenerationResponse> => {
    const response = await apiClient.post('/api/v1/content/generate-fanpage', data);
    return response.data;
  },

  // Generate content using the main content endpoint
  generateContent: async (data: any): Promise<any> => {
    const response = await apiClient.post('/api/v1/content/generate', data);
    return response.data;
  },

  // Get generation status (for async operations)
  getGenerationStatus: async (taskId: string) => {
    const response = await apiClient.get(`/api/v1/content/status/${taskId}`);
    return response.data;
  },

  // Upload template
  uploadTemplate: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/api/v1/content/upload-template', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get templates
  getTemplates: async () => {
    const response = await apiClient.get('/api/v1/content/templates');
    return response.data;
  },

  // Get latest saved template
  getLatestTemplate: async () => {
    const response = await apiClient.get('/api/v1/templates/latest');
    return response.data;
  },

  // Save template configuration
  saveTemplate: async (templateData: {
    template_name?: string;
    template_description?: string;
    configuration: any;
  }) => {
    const response = await apiClient.post('/api/v1/templates/save', templateData);
    return response.data;
  },

  // Get list of templates
  getTemplateList: async (limit: number = 5) => {
    const response = await apiClient.get(`/api/v1/templates/list?limit=${limit}`);
    return response.data;
  },

  // Get template statistics
  getTemplateStats: async () => {
    const response = await apiClient.get('/api/v1/templates/stats');
    return response.data;
  },

  deleteTemplate: async (templateId: string) => {
    const response = await apiClient.delete(`/api/v1/templates/delete`, {
      data: { template_id: templateId }
    });
    return response.data;
  },

  // Save generated content
  saveContent: async (content: any) => {
    const response = await apiClient.post('/api/v1/content/save', content);
    return response.data;
  },

  // Products API
  getProductsByCategory: async (category: string, limit: number = 20): Promise<ProductListResponse> => {
    const response = await apiClient.get(`/api/v1/products/category/${category}?limit=${limit}`);
    return response.data;
  },

  getProductNamesByCategory: async (category: string): Promise<ProductCategoryResponse> => {
    const response = await apiClient.get(`/api/v1/products/category/${category}/names`);
    return response.data;
  },

  searchProducts: async (searchRequest: ProductSearchRequest): Promise<ProductListResponse> => {
    const response = await apiClient.post('/api/v1/products/search', searchRequest);
    return response.data;
  },

  getProductById: async (productId: string): Promise<Product> => {
    const response = await apiClient.get(`/api/v1/products/${productId}`);
    return response.data;
  },

  // Create product
  createProduct: async (payload: ProductCreateRequest): Promise<any> => {
    const response = await apiClient.post('/api/v1/products', payload);
    return response.data;
  },

  // Post Types API
  getPostTypes: async (): Promise<PostTypeListResponse> => {
    const response = await apiClient.get('/api/v1/post-types');
    return response.data;
  },

  createPostType: async (payload: PostTypeCreateRequest): Promise<any> => {
    const response = await apiClient.post('/api/v1/post-types', payload);
    return response.data;
  },

  // History API
  saveHistory: async (data: HistoryCreateRequest): Promise<HistoryCreateResponse> => {
    const response = await apiClient.post('/api/v1/history', data);
    historyCache.clear();
    sessionsCache.clear();
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem('history_updated_at', String(Date.now()));
      }
    } catch {}
    return response.data;
  },

  uploadChatImage: async (file: File, user_id: string, session_id: string): Promise<{ status: number; message: string; data: { image_url: string } }> => {
    const form = new FormData();
    form.append('user_id', user_id);
    form.append('session_id', session_id);
    form.append('image', file);
    const response = await apiClient.post('/api/v1/images/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getHistory: async (params?: {
    user_id?: string;
    session_id?: string;
    page?: number;
    limit?: number;
  }): Promise<HistoryListResponse> => {
    const response = await apiClient.get('/api/v1/history', { params });
    return response.data;
  },

  deleteHistory: async (historyId: string): Promise<HistoryDeleteResponse> => {
    const response = await apiClient.delete(`/api/v1/history/${historyId}`);
    return response.data;
  },

  getSessions: async (params?: { limit?: number; skip?: number }): Promise<SessionsResponse> => {
    const response = await apiClient.get('/api/v1/history/sessions', { params });
    return response.data;
  },

  deleteSession: async (sessionId: string): Promise<DeleteSessionResponse> => {
    try {
      const response = await apiClient.delete(`/api/v1/history/sessions/${sessionId}`);
      historyCache.clear();
      sessionsCache.clear();
      try { if (typeof window !== 'undefined') localStorage.setItem('history_updated_at', String(Date.now())); } catch {}
      return response.data;
    } catch (err) {
      const status = err?.response?.status;
      if (status === 404 || status === 405) {
        try {
          const resp2 = await apiClient.delete(`/api/v1/history/sessions/${sessionId}/`);
          historyCache.clear();
          sessionsCache.clear();
          try { if (typeof window !== 'undefined') localStorage.setItem('history_updated_at', String(Date.now())); } catch {}
          return resp2.data;
        } catch {
          const resp3 = await apiClient.post(`/api/v1/history/sessions/delete`, { session_id: sessionId });
          historyCache.clear();
          sessionsCache.clear();
          try { if (typeof window !== 'undefined') localStorage.setItem('history_updated_at', String(Date.now())); } catch {}
          return resp3.data;
        }
      }
      throw err;
    }
  },

  getHistoryCached: async (params?: {
    user_id?: string;
    session_id?: string;
    page?: number;
    limit?: number;
  }): Promise<HistoryListResponse> => {
    const key = JSON.stringify({
      user_id: params?.user_id || 'current',
      session_id: params?.session_id || 'all',
      page: params?.page || 1,
      limit: params?.limit || 20,
    });
    const cached = historyCache.get(key);
    const ttl = 5 * 60 * 1000;
    if (cached && Date.now() - cached.ts < ttl) {
      return {
        success: true,
        message: 'cached',
        data: cached.data,
        total: cached.data.length,
        page: params?.page || 1,
        limit: params?.limit || 20,
      };
    }
    const response = await apiClient.get('/api/v1/history', { params });
    const data = response.data as HistoryListResponse;
    historyCache.set(key, { ts: Date.now(), data: data.data });
    return data;
  },

  getSessionsCached: async (params?: { limit?: number; skip?: number }): Promise<SessionsResponse> => {
    const key = JSON.stringify({ limit: params?.limit ?? 30, skip: params?.skip ?? 0 });
    const cached = sessionsCache.get(key);
    const ttl = 2 * 60 * 1000;
    if (cached && Date.now() - cached.ts < ttl) {
      return {
        success: true,
        message: 'cached',
        data: cached.data,
        total: cached.data.length,
      } as SessionsResponse;
    }
    const response = await apiClient.get('/api/v1/history/sessions', { params });
    const data = response.data as SessionsResponse;
    sessionsCache.set(key, { ts: Date.now(), data: data.data });
    return data;
  },
  connectHistoryWS: (): WebSocket | null => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
      const host = process.env.NEXT_PUBLIC_SERVER_HOST || 'localhost';
      const port = process.env.NEXT_PUBLIC_API_PORT || '1979';
      const base = apiUrl ? apiUrl.replace(/\/$/, '') : `http://${host}:${port}`;
      const proto = base.startsWith('https') ? 'wss' : 'ws';
      let token: string | null = null;
      try { token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null; } catch {}
      const wsUrl = `${proto}://${base.replace(/^https?:\/\//, '')}/ws/history?token=${encodeURIComponent(token || '')}`;
      return new WebSocket(wsUrl);
    } catch {
      return null;
    }
  },
};

export default apiClient;

type HistoryCacheEntry = { ts: number; data: HistoryItem[] };
const historyCache: Map<string, HistoryCacheEntry> = new Map();
type SessionsCacheEntry = { ts: number; data: SessionInfo[] };
const sessionsCache: Map<string, SessionsCacheEntry> = new Map();
