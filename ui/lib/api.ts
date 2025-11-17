// api.ts
import axios from 'axios';

// ✅ Đơn giản, rõ ràng
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
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

export interface ContentHistoryItem {
  id: string;
  user_id: string;
  content_type: string;
  title: string;
  created_at: string;
  preview: string;
}

export interface ContentHistoryDetail {
  id: string;
  user_id: string;
  content_type: string;
  title: string;
  content: string;
  metadata: any;
  created_at: string;
  updated_at: string;
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

export interface ContentHistoryCreateRequest {
  user_id?: string;
  content_type: string;
  title: string;
  content: string;
  metadata?: any;
}

// Chat Histories (MongoDB) Types
export interface ChatHistoryMessage {
  role: string;
  content: any;
  metadata?: Record<string, any> | null;
}

export interface CreateConversationPayload {
  conversation_id: string;
  user_id: string;
  first_message?: ChatHistoryMessage | null;
  metadata?: Record<string, any> | null;
}

export interface AppendMessagePayload {
  conversation_id: string;
  message: ChatHistoryMessage;
}

export interface ConversationItem {
  conversation_id: string;
  user_id: string;
  created_at?: string;
  updated_at?: string;
  preview?: string;
  messages?: ChatHistoryMessage[];
  metadata?: Record<string, any> | null;
}

export interface ConversationListData {
  items: ConversationItem[];
  page: number;
  limit: number;
  total: number;
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

  // Get saved content history
  getContentHistory: async (page: number = 1, limit: number = 10) => {
    const response = await apiClient.get(`/api/v1/content/history?limit=${limit}`);
    return response.data;
  },

  // Content History API functions
  createContentHistory: async (data: ContentHistoryCreateRequest): Promise<any> => {
    const response = await apiClient.post('/api/v1/content/history', data);
    return response.data;
  },

  getContentHistoryList: async (userId: string = 'default_user', limit: number = 10): Promise<ContentHistoryItem[]> => {
    const response = await apiClient.get(`/api/v1/content/history?user_id=${userId}&limit=${limit}`);
    return response.data;
  },

  getContentHistoryDetail: async (historyId: string): Promise<ContentHistoryDetail> => {
    const response = await apiClient.get(`/api/v1/content/history/${historyId}`);
    return response.data;
  },

  deleteContentHistory: async (historyId: string): Promise<any> => {
    const response = await apiClient.delete(`/api/v1/content-history/${historyId}`);
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

  // =========================
  // MongoDB Chat Histories API
  // =========================
  historiesCreate: async (payload: CreateConversationPayload): Promise<any> => {
    const response = await apiClient.post('/api/v1/histories/create', payload);
    return response.data;
  },

  historiesAppend: async (payload: AppendMessagePayload): Promise<any> => {
    const response = await apiClient.post('/api/v1/histories/append', payload);
    return response.data;
  },

  historiesGet: async (conversationId: string): Promise<{ status: number; message: string; data: ConversationItem | null; }> => {
    const response = await apiClient.post('/api/v1/histories/get', { conversation_id: conversationId });
    return response.data;
  },

  historiesList: async (userId: string, page: number = 1, limit: number = 20): Promise<{ status: number; message: string; data: ConversationListData; }> => {
    const response = await apiClient.post('/api/v1/histories/list', { user_id: userId, page, limit });
    return response.data;
  },

  historiesDelete: async (conversationId: string): Promise<any> => {
    const response = await apiClient.post('/api/v1/histories/delete', { conversation_id: conversationId });
    return response.data;
  },
};

export default apiClient;
