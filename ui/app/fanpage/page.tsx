"use client";

import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { Header } from "@/components/layout/header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { FileText, Upload, Download, RefreshCw, Sparkles, Package, Users, Target, Globe, MessageSquare, Lightbulb, Eye, Search, Clock, X } from "lucide-react";
import { useContentStore } from "@/store/content-store";
import { api, ContentGenerationRequest, Product, ProductCategoryResponse } from "@/lib/api";
import { toast } from "sonner";
import { ChangeEvent, useState, useEffect } from "react";
import ContentHistory from "@/components/content/content-history";
import { ContentHistoryModal } from "@/components/content/content-history-modal";
import { TemplateListModal } from "@/components/content/template-list-modal";
import { ProductSearchDialog } from "@/components/products/product-search-dialog";

// Mapping mặc định từ value ngắn sang tên đầy đủ cho post_type (fallback khi chưa có dữ liệu từ API)
const POST_TYPE_MAPPING = {
  "product_showcase": "Giới thiệu sản phẩm mới (Product Showcases)",
  "promotions": "Khuyến mãi và ưu đãi (Promotions & Discounts)",
  "customer_stories": "Câu chuyện khách hàng và review (Customer Stories & Reviews)",
  "fashion_tips": "Mẹo thời trang và giáo dục (Fashion Tips & Educational Content)",
  "events": "Sự kiện và thông báo (Events & Announcements)",
  "behind_scenes": "Nội dung hậu trường (Behind-the-Scenes)",
  "single_product": "Bài đăng sản phẩm lẻ (Single Product Post)",
  "product_aggregation": "Bài tổng hợp sản phẩm (Product Aggregation)"
};

// Reverse mapping để tìm value từ tên đầy đủ
const REVERSE_POST_TYPE_MAPPING = Object.fromEntries(
  Object.entries(POST_TYPE_MAPPING).map(([key, value]) => [value, key])
);

export default function FanpagePage() {
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null);
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  
  // Generation time tracking state
  const [generationStartTime, setGenerationStartTime] = useState<number | null>(null);
  const [generationEndTime, setGenerationEndTime] = useState<number | null>(null);
  const [generationDuration, setGenerationDuration] = useState<number | null>(null);
  
  // Products state
  const [productNames, setProductNames] = useState<string[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);
  const [isProductSearchOpen, setIsProductSearchOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [cachedProducts, setCachedProducts] = useState<Product[]>([]);
  
  // Multi-product selection state
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
  const [selectedProductNames, setSelectedProductNames] = useState<string[]>([]);
  // Post types state
  const [postTypes, setPostTypes] = useState<{ key: string; full_name: string; description?: string; active: boolean }[]>([]);
  const [isLoadingPostTypes, setIsLoadingPostTypes] = useState(false);
  const [isPostTypeDialogOpen, setIsPostTypeDialogOpen] = useState(false);
  const [newPostType, setNewPostType] = useState<{ key: string; full_name: string; description?: string }>({ key: "", full_name: "", description: "" });
  
  // Custom prompt state
  const [customMainPrompt, setCustomMainPrompt] = useState<string | null>(null);
  const [isCustomPromptLoaded, setIsCustomPromptLoaded] = useState(false);
  // Load post types from API on mount
  useEffect(() => {
    const loadPostTypes = async () => {
      setIsLoadingPostTypes(true);
      try {
        const res = await api.getPostTypes();
        setPostTypes(res.items || []);
      } catch (error) {
        console.error("Error loading post types:", error);
      } finally {
        setIsLoadingPostTypes(false);
      }
    };
    loadPostTypes();
  }, []);

  // Load custom prompt from localStorage on mount
  useEffect(() => {
    const loadCustomPrompt = () => {
      try {
        const storedPrompt = localStorage.getItem('edited_main_prompt');
        if (storedPrompt) {
          setCustomMainPrompt(storedPrompt);
          setIsCustomPromptLoaded(true);
        } else {
          setCustomMainPrompt(null);
          setIsCustomPromptLoaded(false);
        }
      } catch (error) {
        console.error("Error loading custom prompt:", error);
        setCustomMainPrompt(null);
        setIsCustomPromptLoaded(false);
      }
    };
    
    loadCustomPrompt();
  }, []);
  
  // Cache for each product category to avoid redundant API calls
  const [productCache, setProductCache] = useState<{
    [category: string]: {
      names: string[];
      products: Product[];
    }
  }>({});

  const {
    formData,
    setFormData,
    generatedContent,
    setGeneratedContent,
    isGenerating,
    setIsGenerating,
    activeTab,
    setActiveTab,
    addToHistory,
    addToSavedHistory,
  } = useContentStore();

  // LoadingSpinner component
  const LoadingSpinner = () => (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <Sparkles className="w-6 h-6 text-blue-600" />
        </div>
      </div>
      <p className="mt-4 text-gray-600 font-medium">Đang tạo nội dung...</p>
      <p className="text-sm text-gray-500">Vui lòng đợi trong giây lát</p>
    </div>
  );

  const getFullNameByKey = (key: string): string | undefined => {
    const found = postTypes.find((pt) => pt.key === key);
    if (found) return found.full_name;
    return POST_TYPE_MAPPING[key as keyof typeof POST_TYPE_MAPPING];
  };

  const getKeyByFullName = (fullName: string): string | undefined => {
    const found = postTypes.find((pt) => pt.full_name === fullName);
    if (found) return found.key;
    return (REVERSE_POST_TYPE_MAPPING as Record<string, string>)[fullName];
  };

  const handleInputChange = (field: string, value: string | string[]) => {
    // Lưu trực tiếp giá trị vào formData (đối với post_type: lưu key)
    setFormData({ [field]: value });
  };

  const handleViewHistoryDetail = (historyId: string) => {
    setSelectedHistoryId(historyId);
    setIsHistoryModalOpen(true);
  };

  const handleCloseHistoryModal = () => {
    setIsHistoryModalOpen(false);
    setSelectedHistoryId(null);
  };

  // Load product names when product type changes
  useEffect(() => {
    if (formData.product_type) {
      loadProductNames(formData.product_type);
    } else {
      setProductNames([]);
      setSelectedProduct(null);
      setCachedProducts([]);
    }
  }, [formData.product_type]);

  const loadProductNames = async (category: string) => {
    // Check if data for this category is already cached
    if (productCache[category]) {
      console.log(`Using cached data for category: ${category}`);
      setProductNames(productCache[category].names);
      setCachedProducts(productCache[category].products);
      return;
    }

    setIsLoadingProducts(true);
    try {
      console.log(`Loading fresh data for category: ${category}`);
      // Load both product names and full product data
      const [namesResponse, productsResponse] = await Promise.all([
        api.getProductNamesByCategory(category),
        api.getProductsByCategory(category, 50)
      ]);
      
      const names = namesResponse.product_names;
      const products = productsResponse.data;
      
      // Update current state
      setProductNames(names);
      setCachedProducts(products);
      
      // Cache the data for this category
      setProductCache(prev => ({
        ...prev,
        [category]: {
          names: names,
          products: products
        }
      }));
      
    } catch (error) {
      console.error("Error loading product names:", error);
      toast.error("Không thể tải danh sách sản phẩm");
      setProductNames([]);
      setCachedProducts([]);
    } finally {
      setIsLoadingProducts(false);
    }
  };

  const handleProductSelect = (product: Product) => {
    setSelectedProduct(product);
    handleInputChange('specific_product', product.name);
  };

  // Handle multiple product selection
  const handleMultipleProductSelect = (product: Product) => {
    // Check if product is already selected
    const isAlreadySelected = selectedProducts.some(p => p.name === product.name);
    
    if (isAlreadySelected) {
      toast.info("Sản phẩm này đã được chọn");
      return;
    }
    
    // Add to selected products
    const updatedProducts = [...selectedProducts, product];
    const updatedProductNames = [...selectedProductNames, product.name];
    
    setSelectedProducts(updatedProducts);
    setSelectedProductNames(updatedProductNames);
    
    // Update form data with multiple product names
    handleInputChange('specific_product', updatedProductNames.join(', '));
    toast.success(`Đã thêm sản phẩm: ${product.name}`);
  };

  // Remove a product from selection
  const removeSelectedProduct = (productName: string) => {
    const updatedProducts = selectedProducts.filter(p => p.name !== productName);
    const updatedProductNames = selectedProductNames.filter(name => name !== productName);
    
    setSelectedProducts(updatedProducts);
    setSelectedProductNames(updatedProductNames);
    
    // Update form data
    handleInputChange('specific_product', updatedProductNames.join(', '));
    
    toast.success(`Đã xóa sản phẩm: ${productName}`);
  };

  // Clear all selected products
  const clearAllSelectedProducts = () => {
    setSelectedProducts([]);
    setSelectedProductNames([]);
    handleInputChange('specific_product', '');
    toast.success("Đã xóa tất cả sản phẩm đã chọn");
  };

  // Get product description from selected product or cached products
  const getSelectedProductDescription = (): string => {
    // Handle multiple products
    if (selectedProducts.length > 0) {
      return selectedProducts
        .map((product, index) => `Sản phẩm ${index + 1}: ${product.data.description || ""}`)
        .join("\n\n");
    }
    
    // Handle multiple product names from form
    if (selectedProductNames.length > 0 && cachedProducts.length > 0) {
      const descriptions = selectedProductNames
        .map((productName, index) => {
          const foundProduct = cachedProducts.find(p => p.name === productName);
          return foundProduct ? `Sản phẩm ${index + 1}: ${foundProduct.data.description || ""}` : "";
        })
        .filter(desc => desc !== "");
      
      if (descriptions.length > 0) {
        return descriptions.join("\n\n");
      }
    }
    
    // Fallback to single product logic for backward compatibility
    if (selectedProduct) {
      return selectedProduct.data.description || "";
    }
    
    // If no selectedProduct but we have a specific_product name, find it in cached products
    if (formData.specific_product && cachedProducts.length > 0) {
      const foundProduct = cachedProducts.find(p => p.name === formData.specific_product);
      return foundProduct?.data.description || "";
    }
    
    return "";
  };

  const openProductSearch = () => {
    if (!formData.product_type) {
      toast.error("Vui lòng chọn loại sản phẩm trước");
      return;
    }
    setIsProductSearchOpen(true);
  };

  const handleGenerateContent = async () => {
    // Validate form data
    if (!formData.post_type) {
      toast.error("Vui lòng chọn loại bài viết");
      return;
    }

    // Start time tracking
    const startTime = Date.now();
    setGenerationStartTime(startTime);
    setGenerationEndTime(null);
    setGenerationDuration(null);

    setIsGenerating(true);
    
    try {
      const postTypeName = getFullNameByKey(formData.post_type as string) || (formData.post_type as string);
      // Build template configuration for backend prompt rendering
      const templateConfiguration = {
        timestamp: new Date().toISOString(),
        product_info: {
          input_method: formData.product_input_method || "Chọn từ danh sách có sẵn",
          product_type: formData.product_type || "",
          selected_product: formData.specific_product || formData.custom_product_name || "",
          product_name: formData.custom_product_name || "",
          product_price: parseFloat(formData.custom_product_price || "0") || 0,
          product_description: formData.custom_product_description || getSelectedProductDescription()
        },
        post_info: {
          post_type: postTypeName,
          summary_options: formData.aggregation_options || []
        },
        target_audience: {
          segments: formData.customer_segments || [],
          specific_targets: formData.specific_targets || []
        },
        objectives: {
          main: formData.main_objectives || [],
          funnel: formData.funnel_objectives || []
        },
        platforms: formData.platforms || ["Facebook"],
        content: {
          pillars: formData.content_pillars || [],
          use_cases: formData.content_funnel || []
        },
        main_message: formData.main_message || "",
        content_settings: {
          content_length: parseInt(formData.content_length || "200"),
          hook_length: parseInt(formData.hook_length || "25"),
          num_posts: parseInt(formData.num_posts || "3")
        }
      };

      // Use custom main prompt from state (already loaded from localStorage)
      const customPrompt = customMainPrompt;

      // Map UI form data to API schema format based on ContentGenerationRequest
      const requestData = {
        timestamp: new Date().toISOString(),
        product_info: {
          input_method: formData.product_input_method || "Chọn từ danh sách có sẵn",
          selected_product: formData.specific_product || formData.custom_product_name || "",
          product_name: formData.custom_product_name || "",
          product_price: parseFloat(formData.custom_product_price || "0") || 0,
        },
        post_info: {
          post_type: postTypeName,
          summary_options: formData.aggregation_options || []
        },
        target_audience: {
          segments: formData.customer_segments || [],
          specific_targets: formData.specific_targets || []
        },
        objectives: {
          main: formData.main_objectives || [],
          funnel: formData.funnel_objectives || []
        },
        platforms: formData.platforms || ["Facebook"],
        content: {
          pillars: formData.content_pillars || [],
          use_cases: formData.content_funnel || []
        },
        main_message: formData.main_message || "",
        content_settings: {
          content_length: parseInt(formData.content_length || "200"),
          hook_length: parseInt(formData.hook_length || "25"),
          num_posts: parseInt(formData.num_posts || "3")
        },
        description_product: getSelectedProductDescription(), // Add the description_product variable
        template_configuration: templateConfiguration,
        custom_prompt_yaml: customPrompt || undefined
      };

      const response = await api.generateContent(requestData);
      
      const newContent = {
        post_content: response.final_output || response.content || "",
        caption: response.final_output || response.content || "",
        hashtags: response.hashtags || [],
        created_at: new Date().toISOString(),
        id: response.crew_id || Date.now().toString(),
      };

      setGeneratedContent(newContent);
      addToHistory(newContent);
      
      // Lưu lịch sử vào database
      try {
        const historyData = {
          content_type: 'fanpage',
          title: `${postTypeName || 'Bài viết'} - ${new Date().toLocaleDateString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
          })}`,
          content: JSON.stringify({
            post_content: newContent.post_content,
            caption: newContent.caption,
            hashtags: newContent.hashtags,
            form_data: formData
          }),
          metadata: {
            post_type: postTypeName,
            post_type_key: formData.post_type,
            business_name: formData.business_name,
            num_posts: formData.num_posts
          }
        };
        
        const savedHistory = await api.createContentHistory(historyData);
        
        // Thêm vào state với format phù hợp
        const historyItem = {
          id: savedHistory.id,
          user_id: savedHistory.user_id,
          content_type: savedHistory.content_type,
          title: savedHistory.title,
          created_at: savedHistory.created_at,
          preview: savedHistory.preview
        };
        
        addToSavedHistory(historyItem);
        
      } catch (error) {
        console.error("Lỗi khi lưu lịch sử:", error);
        // Không hiển thị lỗi để không làm phiền user
      }
      
      // End time tracking
      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000; // Convert to seconds
      setGenerationEndTime(endTime);
      setGenerationDuration(duration);
      
      toast.success("Tạo nội dung thành công!");
      
      // Tự động lưu template sau khi tạo nội dung thành công
      try {
        await handleSaveTemplate();
      } catch (error) {
        console.error("Auto-save template failed:", error);
        // Không hiển thị lỗi auto-save để không làm phiền user
      }
      
    } catch (error: unknown) {
      console.error("Error generating content:", error);
      
      let errorMessage = "Có lỗi xảy ra khi tạo nội dung";
      
      // Handle different types of errors
      if (error instanceof Error) {
        if ('response' in error && error.response && typeof error.response === 'object') {
          const response = error.response as any;
          
          // Handle API error responses
          if (response.data) {
            if (response.data.error) {
              errorMessage = response.data.error;
            } else if (response.data.message) {
              errorMessage = response.data.message;
            } else if (response.data.detail) {
              errorMessage = response.data.detail;
            }
          }
          
          // Handle HTTP status codes
          if (response.status === 400) {
            errorMessage = "Dữ liệu đầu vào không hợp lệ. Vui lòng kiểm tra lại thông tin.";
          } else if (response.status === 500) {
            errorMessage = "Lỗi máy chủ. Vui lòng thử lại sau.";
          } else if (response.status === 422) {
            errorMessage = "Dữ liệu không đúng định dạng. Vui lòng kiểm tra lại.";
          }
        } else if ('code' in error && error.code === 'NETWORK_ERROR') {
          errorMessage = "Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.";
        } else {
          errorMessage = error.message || errorMessage;
        }
      }
      
      toast.error(errorMessage);
    } finally {
      // End time tracking for failed generations
      if (generationStartTime && !generationEndTime) {
        const endTime = Date.now();
        const duration = (endTime - generationStartTime) / 1000;
        setGenerationEndTime(endTime);
        setGenerationDuration(duration);
      }
      setIsGenerating(false);
    }
  };

  const handleGenerate = async () => {
    await handleGenerateContent();
  };

  const handleLoadTemplate = async () => {
    try {
      const response = await api.getLatestTemplate();
      if (response.success && response.template) {
        const template = response.template;
        const loadedPostTypeKey = getKeyByFullName(template?.post_info?.post_type || "") || "";
        
        const mappedFormData: any = {
          post_type: loadedPostTypeKey,
          aggregation_options: template?.post_info?.summary_options || [],
          product_input_method: template?.product_info?.input_method || "predefined",
          product_type: template?.product_info?.product_type || "",
          specific_product: template?.product_info?.selected_product || "",
          custom_product_name: template?.product_info?.product_name || "",
          custom_product_price: (template?.product_info?.product_price ?? "").toString(),
          custom_product_description: template?.product_info?.product_description || "",
          customer_segments: template?.target_audience?.segments || [],
          specific_targets: template?.target_audience?.specific_targets || [],
          main_objectives: template?.objectives?.main || [],
          funnel_objectives: template?.objectives?.funnel || [],
          platforms: template?.platforms || [],
          content_pillars: template?.content?.pillars || [],
          content_funnel: template?.content?.use_cases || [],
          main_message: template?.main_message || "",
          content_length: (template?.content_settings?.content_length ?? "").toString(),
          hook_length: (template?.content_settings?.hook_length ?? "").toString(),
        };

        setFormData(mappedFormData);
        toast.success(`Đã tải template thành công! (Tổng cộng: ${response.template_count} templates)`);
      } else {
        toast.error(response.message || "Không tìm thấy template nào.");
      }
    } catch (error: any) {
      console.error("Error loading template:", error);
      if (error?.response?.status === 404) {
        toast.error("Không tìm thấy template nào. Hãy tạo nội dung trước để lưu template.");
      } else {
        toast.error("Không thể tải template. Vui lòng thử lại.");
      }
    }
  };

  const handleSaveTemplate = async () => {
    try {
      // Validate form data trước khi lưu
      if (!formData.post_type) {
        toast.error("Vui lòng chọn loại bài viết trước khi lưu template");
        return;
      }

      // Tạo template configuration từ form data
      const postTypeName = getFullNameByKey(formData.post_type as string) || (formData.post_type as string);
      const templateConfiguration = {
        timestamp: new Date().toISOString(),
        product_info: {
          input_method: formData.product_input_method || "Chọn từ danh sách có sẵn",
          product_type: formData.product_type || "",
          selected_product: formData.specific_product || formData.custom_product_name || "",
          product_name: formData.custom_product_name || "",
          product_price: parseFloat(formData.custom_product_price || "0") || 0,
          product_description: formData.custom_product_description || getSelectedProductDescription()
        },
        post_info: {
          post_type: postTypeName,
          summary_options: formData.aggregation_options || []
        },
        target_audience: {
          segments: formData.customer_segments || [],
          specific_targets: formData.specific_targets || []
        },
        objectives: {
          main: formData.main_objectives || [],
          funnel: formData.funnel_objectives || []
        },
        platforms: formData.platforms || ["Facebook"],
        content: {
          pillars: formData.content_pillars || [],
          use_cases: formData.content_funnel || []
        },
        main_message: formData.main_message || "",
        content_settings: {
          content_length: parseInt(formData.content_length || "200"),
          hook_length: parseInt(formData.hook_length || "25")
        }
      };

      // Kiểm tra xem có template nào tương tự không
      try {
        const templateResponse = await api.getTemplateList();
        const existingTemplates = templateResponse.templates || [];
        
        // So sánh configuration hiện tại với các template đã có
        const isDuplicate = existingTemplates.some((template: any) => {
          const existingConfig = template.configuration;
          
          // So sánh các trường chính
          return (
            existingConfig?.post_info?.post_type === templateConfiguration.post_info.post_type &&
            JSON.stringify(existingConfig?.target_audience?.segments?.sort()) === JSON.stringify(templateConfiguration.target_audience.segments.sort()) &&
            JSON.stringify(existingConfig?.objectives?.main?.sort()) === JSON.stringify(templateConfiguration.objectives.main.sort()) &&
            JSON.stringify(existingConfig?.platforms?.sort()) === JSON.stringify(templateConfiguration.platforms.sort()) &&
            existingConfig?.main_message === templateConfiguration.main_message &&
            existingConfig?.product_info?.selected_product === templateConfiguration.product_info.selected_product
          );
        });

        if (isDuplicate) {
          toast.info("Template tương tự đã tồn tại. Không cần lưu template mới.");
          return;
        }
      } catch (error) {
        console.warn("Không thể kiểm tra template trùng lặp:", error);
        // Tiếp tục lưu nếu không thể kiểm tra
      }

      const templateData = {
        template_name: `Template ${new Date().toLocaleDateString('vi-VN')} - ${postTypeName}`,
        template_description: `Template tự động cho ${postTypeName} - ${formData.main_message?.substring(0, 50) || 'Không có mô tả'}`,
        configuration: templateConfiguration
      };

      const response = await api.saveTemplate(templateData);
      
      if (response.success) {
        toast.success(`Template đã được lưu thành công! ID: ${response.template_id}`);
      } else {
        toast.error(response.message || "Không thể lưu template");
      }
    } catch (error: any) {
      console.error("Error saving template:", error);
      toast.error("Có lỗi xảy ra khi lưu template. Vui lòng thử lại.");
    }
  };

  return (
    <SidebarProvider>
      <div className="flex min-h-screen bg-gray-50">
        <AppSidebar />
        <div className="flex-1">
          <Header />
          <main className="p-6">
            <div className="w-full">
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  Tạo nội dung Fanpage
                </h1>
                <p className="text-gray-600">
                  Tạo bài viết, caption và hashtag chuyên nghiệp cho fanpage Facebook
                </p>
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 w-full">
                {/* Form Input */}
                <Card className="bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FileText className="mr-2 h-5 w-5 text-blue-600" />
                      Thông tin đầu vào
                    </CardTitle>
                    <CardDescription>
                      Nhập thông tin để tạo nội dung phù hợp
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Loại Bài Viết */}
                    <div className="space-y-3">
                      <Label className="text-base font-semibold flex items-center">
                        <MessageSquare className="mr-2 h-4 w-4" />
                        Loại Bài Viết *
                      </Label>
                      <Select 
                        value={formData.post_type || ""}
                        onValueChange={(value) => handleInputChange('post_type', value)}
                      >
                        <SelectTrigger className="bg-gray-50 border-gray-200 focus:bg-white">
                          <SelectValue placeholder="Chọn loại bài viết" />
                        </SelectTrigger>
                        <SelectContent>
                          {(postTypes.length > 0 ? postTypes : Object.entries(POST_TYPE_MAPPING).map(([key, full]) => ({ key, full_name: full, active: true } as any))).map((pt: any) => (
                            <SelectItem key={pt.key} value={pt.key}>{pt.full_name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                      <div className="flex items-center gap-2">
                        <Dialog open={isPostTypeDialogOpen} onOpenChange={setIsPostTypeDialogOpen}>
                          <DialogTrigger asChild>
                            <Button type="button" variant="outline" size="sm">Thêm loại bài viết</Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Thêm loại bài viết mới</DialogTitle>
                              <DialogDescription>Nhập thông tin để tạo loại bài viết mới.</DialogDescription>
                            </DialogHeader>
                            <div className="space-y-3">
                              <div>
                                <Label className="text-sm">Key (khóa nội bộ):</Label>
                                <Input value={newPostType.key} onChange={(e) => setNewPostType((p) => ({ ...p, key: e.target.value }))} placeholder="vd: product_showcases" />
                              </div>
                              <div>
                                <Label className="text-sm">Tên đầy đủ:</Label>
                                <Input value={newPostType.full_name} onChange={(e) => setNewPostType((p) => ({ ...p, full_name: e.target.value }))} placeholder="vd: Giới thiệu sản phẩm mới (Product Showcases)" />
                              </div>
                              <div>
                                <Label className="text-sm">Mô tả (tùy chọn):</Label>
                                <Textarea value={newPostType.description || ""} onChange={(e) => setNewPostType((p) => ({ ...p, description: e.target.value }))} placeholder="Mô tả ngắn" />
                              </div>
                            </div>
                            <DialogFooter>
                              <Button type="button" variant="secondary" onClick={() => setIsPostTypeDialogOpen(false)}>Hủy</Button>
                              <Button
                                type="button"
                                onClick={async () => {
                                  try {
                                    if (!newPostType.key || !newPostType.full_name) {
                                      toast.error("Vui lòng nhập đầy đủ key và tên");
                                      return;
                                    }
                                    const res = await api.createPostType(newPostType);
                                    if (res?.success) {
                                      toast.success("Đã thêm/cập nhật loại bài viết");
                                      setIsPostTypeDialogOpen(false);
                                      setNewPostType({ key: "", full_name: "", description: "" });
                                      const updated = await api.getPostTypes();
                                      setPostTypes(updated.items || []);
                                    } else {
                                      toast.error("Không thể tạo loại bài viết");
                                    }
                                  } catch (err) {
                                    toast.error("Lỗi khi tạo loại bài viết");
                                  }
                                }}
                              >Lưu</Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      </div>
                      
                      {/* Tùy chọn tổng hợp sản phẩm */}
                      {formData.post_type === "product_aggregation" && (
                        <div className="ml-4 space-y-2">
                          <Label className="text-sm font-medium">Tùy chọn tổng hợp:</Label>
                          <div className="space-y-2">
                            {[
                              "Tổng hợp theo màu sắc",
                              "Tổng hợp theo thiết kế/bộ sưu tập",
                              "Tổng hợp theo tính năng/dịp sử dụng (đi làm, đi tiệc, du lịch)",
                              "Tổng hợp theo phong cách (năng động, công sở, tối giản)"
                            ].map((option) => (
                              <div key={option} className="flex items-center space-x-2">
                                <Checkbox 
                                  id={option}
                                  checked={(formData.aggregation_options as string[] || []).includes(option)}
                                  onCheckedChange={(checked: boolean) => {
                                    const current = formData.aggregation_options as string[] || [];
                                    if (checked) {
                                      handleInputChange('aggregation_options', [...current, option]);
                                    } else {
                                      handleInputChange('aggregation_options', current.filter(item => item !== option));
                                    }
                                  }}
                                />
                                <Label htmlFor={option} className="text-sm">{option}</Label>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Thông Tin Sản Phẩm */}
                    <div className="space-y-3">
                      <Label className="text-base font-semibold flex items-center">
                        <Package className="mr-2 h-4 w-4" />
                        Thông Tin Sản Phẩm
                      </Label>
                      
                      <RadioGroup 
                        value={formData.product_input_method || "predefined"} 
                        onValueChange={(value) => handleInputChange('product_input_method', value)}
                        className="flex flex-row space-x-4"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="predefined" id="predefined" />
                          <Label htmlFor="predefined" className="text-sm">Chọn 1 sản phẩm từ danh sách</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="multiple" id="multiple" />
                          <Label htmlFor="multiple" className="text-sm">Chọn nhiều sản phẩm (2+ sản phẩm)</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="custom" id="custom" />
                          <Label htmlFor="custom" className="text-sm">Nhập sản phẩm mới</Label>
                        </div>
                      </RadioGroup>

                      {formData.product_input_method === "predefined" ? (
                        <div className="space-y-3">
                          <div className="flex items-center gap-3">
                            <Label className="text-sm w-28 shrink-0">Loại sản phẩm:</Label>
                            <Select
                              value={formData.product_type || ""}
                              onValueChange={(value) => handleInputChange('product_type', value)}
                            >
                              <SelectTrigger className="bg-gray-50 border-gray-200 w-48">
                                <SelectValue placeholder="Chọn loại" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="bag">Túi</SelectItem>
                                <SelectItem value="shoes">Giày</SelectItem> 
                                <SelectItem value="wallet">Ví</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="flex items-center gap-3">
                            <Label className="text-sm w-28 shrink-0">Sản phẩm cụ thể:</Label>
                            <div className="flex gap-2 flex-1">
                              <Select
                                value={formData.specific_product || ""}
                                onValueChange={(value) => handleInputChange('specific_product', value)}
                                disabled={!formData.product_type || isLoadingProducts}
                              >
                                <SelectTrigger className="bg-gray-50 border-gray-200 flex-1 truncate text-ellipsis overflow-hidden whitespace-nowrap max-w-[300px]">
                                <SelectValue 
                                  placeholder={
                                    isLoadingProducts 
                                      ? "Đang tải..." 
                                      : !formData.product_type 
                                        ? "Chọn loại sản phẩm trước" 
                                        : "Chọn sản phẩm"
                                  } 
                                />
                              </SelectTrigger>
                                <SelectContent className="max-h-[300px] overflow-y-auto">
                                  {productNames.map((productName) => (
                                    <SelectItem key={productName} value={productName}>
                                      {productName}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={openProductSearch}
                                disabled={!formData.product_type}
                                className="px-5"
                              >
                                <Search className="w-6 h-6" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ) : formData.product_input_method === "multiple" ? (
                        <div className="space-y-4">
                          <div className="flex items-center gap-3">
                            <Label className="text-sm w-28 shrink-0">Loại sản phẩm:</Label>
                            <Select
                              value={formData.product_type || ""}
                              onValueChange={(value) => handleInputChange('product_type', value)}
                            >
                              <SelectTrigger className="bg-gray-50 border-gray-200 w-48">
                                <SelectValue placeholder="Chọn loại" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="bag">Túi</SelectItem>
                                <SelectItem value="shoes">Giày</SelectItem> 
                                <SelectItem value="wallet">Ví</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          
                          <div className="flex items-center gap-3">
                            <Label className="text-sm w-28 shrink-0">Thêm sản phẩm:</Label>
                            <div className="flex gap-2 flex-1">
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={openProductSearch}
                                disabled={!formData.product_type}
                                className="px-4"
                              >
                                <Search className="w-4 h-4 mr-2" />
                                Tìm và thêm sản phẩm
                              </Button>
                              {selectedProducts.length > 0 && (
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  onClick={clearAllSelectedProducts}
                                  className="px-4 text-red-600 hover:text-red-700"
                                >
                                  Xóa tất cả
                                </Button>
                              )}
                            </div>
                          </div>

                          {/* Display selected products */}
                          {selectedProducts.length > 0 && (
                            <div className="space-y-2">
                              <Label className="text-sm font-medium">Sản phẩm đã chọn ({selectedProducts.length}):</Label>
                              <div className="space-y-2 max-h-40 overflow-y-auto">
                                {selectedProducts.map((product, index) => (
                                  <div key={product.name} className="flex items-center justify-between bg-blue-50 p-3 rounded-lg border">
                                    <div className="flex-1">
                                      <div className="font-medium text-sm">{index + 1}. {product.name}</div>
                                      <div className="text-xs text-gray-600 truncate max-w-[300px]">
                                        {product.data.description || "Không có mô tả"}
                                      </div>
                                    </div>
                                    <Button
                                      type="button"
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => removeSelectedProduct(product.name)}
                                      className="ml-2 h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                                    >
                                      <X className="w-4 h-4" />
                                    </Button>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {selectedProducts.length === 0 && (
                            <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg border-2 border-dashed">
                              <Package className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                              <p className="text-sm">Chưa có sản phẩm nào được chọn</p>
                              <p className="text-xs">Nhấn "Tìm và thêm sản phẩm" để bắt đầu</p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <Label className="text-sm">Tên sản phẩm:</Label>
                              <Input
                                placeholder="Nhập tên sản phẩm"
                                className="bg-gray-50 border-gray-200"
                                value={formData.custom_product_name || ""}
                                onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange('custom_product_name', e.target.value)}
                              />
                            </div>
                            <div>
                              <Label className="text-sm">Giá sản phẩm (VNĐ):</Label>
                              <Input
                                type="number"
                                placeholder="0"
                                className="bg-gray-50 border-gray-200"
                                value={formData.custom_product_price || ""}
                                onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange('custom_product_price', e.target.value)}
                              />
                            </div>
                          </div>
                          <div>
                            <Label className="text-sm">Mô tả sản phẩm:</Label>
                            <Textarea
                              placeholder="Mô tả chi tiết về sản phẩm"
                              className="bg-gray-50 border-gray-200"
                              value={formData.custom_product_description || ""}
                              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => handleInputChange('custom_product_description', e.target.value)}
                            />
                          </div>
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              type="button"
                              variant="outline"
                              onClick={async () => {
                                try {
                                  const name = formData.custom_product_name || "";
                                  if (!name.trim()) {
                                    toast.error("Vui lòng nhập tên sản phẩm");
                                    return;
                                  }
                                  const price = parseFloat(formData.custom_product_price || "0");
                                  const description = formData.custom_product_description || "";
                                  const category = formData.product_type ? [formData.product_type] : [];
                                  const payload = {
                                    name,
                                    pricing: { price, currency: "VND" },
                                    media: [],
                                    data: { description, category, quantity: 0 },
                                  };
                                  const res = await api.createProduct(payload);
                                  if (res?.success) {
                                    toast.success("Đã lưu sản phẩm mới");
                                  } else {
                                    toast.error("Không thể lưu sản phẩm");
                                  }
                                } catch (err) {
                                  toast.error("Lỗi khi lưu sản phẩm");
                                }
                              }}
                            >Lưu sản phẩm</Button>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Khách Hàng Mục Tiêu */}
                    <div className="space-y-3">
                      <Label className="text-base font-semibold flex items-center">
                        <Users className="mr-2 h-4 w-4" />
                        Khách Hàng Mục Tiêu
                      </Label>
                      
                      <div className="space-y-3">
                        <div>
                          <Label className="text-sm font-medium">Phân khúc khách hàng:</Label>
                          <div className="grid grid-cols-1 gap-2 mt-2">
                            {[
                              "New Visitors - Khách mới (Awareness)",
                              "Prospects - Khách tiềm năng (Consideration)",
                              "New Buyers/Engaged - Khách mua mới/đã tương tác",
                              "Recent Customers (30d) - Khách đã mua (30 ngày)",
                              "Community / Public - Cộng đồng chung",
                              "Loyal/VIP (90/180d) - Trung thành/VIP",
                              "Dormant 180d+ - Ngủ quên"
                            ].map((segment) => (
                              <div key={segment} className="flex items-center space-x-2">
                                <Checkbox 
                                  id={segment}
                                  checked={(formData.customer_segments as string[] || []).includes(segment)}
                                  onCheckedChange={(checked: boolean) => {
                                    const current = formData.customer_segments as string[] || [];
                                    if (checked) {
                                      handleInputChange('customer_segments', [...current, segment]);
                                    } else {
                                      handleInputChange('customer_segments', current.filter(item => item !== segment));
                                    }
                                  }}
                                />
                                <Label htmlFor={segment} className="text-sm">{segment}</Label>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <Label className="text-sm font-medium">Đối tượng cụ thể:</Label>
                          <div className="grid grid-cols-2 gap-2 mt-2">
                            {["Đối tượng cho túi", "Đối tượng cho giày"].map((target) => (
                              <div key={target} className="flex items-center space-x-2">
                                <Checkbox 
                                  id={target}
                                  checked={(formData.specific_targets as string[] || []).includes(target)}
                                  onCheckedChange={(checked: boolean) => {
                                    const current = formData.specific_targets as string[] || [];
                                    if (checked) {
                                      handleInputChange('specific_targets', [...current, target]);
                                    } else {
                                      handleInputChange('specific_targets', current.filter(item => item !== target));
                                    }
                                  }}
                                />
                                <Label htmlFor={target} className="text-sm">{target}</Label>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Mục Tiêu */}
                    <div className="space-y-3">
                      <Label className="text-base font-semibold flex items-center">
                        <Target className="mr-2 h-4 w-4" />
                        Mục Tiêu
                      </Label>
                      
                      <div className="space-y-3">
                        <div>
                          <Label className="text-sm font-medium">Mục tiêu chính:</Label>
                          <div className="grid grid-cols-1 gap-2 mt-2">
                            {[
                              "Branding (Xây dựng nhận diện thương hiệu)",
                              "Performance / Direct Sales (Bán hàng trực tiếp)",
                              "Retention & After-sales (Chăm sóc hậu mãi)",
                              "Onboarding / New CX (Trải nghiệm KH mới)",
                              "Community & PR (Cộng đồng & lan tỏa)",
                              "Educate (Giáo dục khách hàng)"
                            ].map((objective) => (
                              <div key={objective} className="flex items-center space-x-2">
                                <Checkbox 
                                  id={objective}
                                  checked={(formData.main_objectives as string[] || []).includes(objective)}
                                  onCheckedChange={(checked: boolean) => {
                                    const current = formData.main_objectives as string[] || [];
                                    if (checked) {
                                      handleInputChange('main_objectives', [...current, objective]);
                                    } else {
                                      handleInputChange('main_objectives', current.filter(item => item !== objective));
                                    }
                                  }}
                                />
                                <Label htmlFor={objective} className="text-sm">{objective}</Label>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <Label className="text-sm font-medium">Mục tiêu theo phễu:</Label>
                          <div className="grid grid-cols-1 gap-2 mt-2">
                            {[
                              "Awareness (Nhận biết) - Dừng lướt & nhớ keyword",
                              "Consideration (Cân nhắc) - Hiểu lợi ích, so sánh",
                              "Conversion (Chuyển đổi) ATC - mua/đặt lịch thử",
                              "Loyalty (Trung thành/Mua lại) - Mua lần 2, LTV",
                              "Engagement (Tương tác/Cộng đồng) - UGC/Workshop/Referral"
                            ].map((funnel) => (
                              <div key={funnel} className="flex items-center space-x-2">
                                <Checkbox 
                                  id={funnel}
                                  checked={(formData.funnel_objectives as string[] || []).includes(funnel)}
                                  onCheckedChange={(checked: boolean) => {
                                    const current = formData.funnel_objectives as string[] || [];
                                    if (checked) {
                                      handleInputChange('funnel_objectives', [...current, funnel]);
                                    } else {
                                      handleInputChange('funnel_objectives', current.filter(item => item !== funnel));
                                    }
                                  }}
                                />
                                <Label htmlFor={funnel} className="text-sm">{funnel}</Label>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Nền Tảng Đăng Tải */}
                    <div className="space-y-3">
                      <Label className="text-base font-semibold flex items-center">
                        <Globe className="mr-2 h-4 w-4" />
                        Nền Tảng Đăng Tải
                      </Label>
                      <div className="grid grid-cols-3 gap-2">
                        {["Facebook", "Instagram", "TikTok", "Website", "YouTube"].map((platform) => (
                          <div key={platform} className="flex items-center space-x-2">
                            <Checkbox 
                              id={platform}
                              checked={(formData.platforms as string[] || ["Facebook"]).includes(platform)}
                              onCheckedChange={(checked: boolean) => {
                                const current = formData.platforms as string[] || ["Facebook"];
                                if (checked) {
                                  handleInputChange('platforms', [...current, platform]);
                                } else {
                                  handleInputChange('platforms', current.filter(item => item !== platform));
                                }
                              }}
                            />
                            <Label htmlFor={platform} className="text-sm">{platform}</Label>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Trụ Cột Nội Dung */}
                    <div className="space-y-3">
                      <Label className="text-base font-semibold flex items-center">
                        <Lightbulb className="mr-2 h-4 w-4" />
                        Trụ Cột Nội Dung
                      </Label>
                      <div className="space-y-3">
                        <div>
                          <Label className="text-sm font-medium">Mục tiêu chính:</Label>
                          <div className="grid grid-cols-1 gap-2 mt-2">
                            {[
                              "Branding (Xây dựng thương hiệu)",
                              "Performance / Direct Sales (Bán hàng trực tiếp)",
                              "Retention & After-sales (Chăm sóc hậu mãi)",
                              "Onboarding / New CX (Trải nghiệm khách hàng mới)",
                              "Community & PR (Cộng đồng & quan hệ công chúng)",
                              "Educate (Giáo dục khách hàng)"
                            ].map((pillar) => (
                              <div key={pillar} className="flex items-center space-x-2">
                                <Checkbox 
                                  id={pillar}
                                  checked={(formData.content_pillars as string[] || []).includes(pillar)}
                                  onCheckedChange={(checked: boolean) => {
                                    const current = formData.content_pillars as string[] || [];
                                    if (checked) {
                                      handleInputChange('content_pillars', [...current, pillar]);
                                    } else {
                                      handleInputChange('content_pillars', current.filter(item => item !== pillar));
                                    }
                                  }}
                                />
                                <Label htmlFor={pillar} className="text-sm">{pillar}</Label>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <Label className="text-sm font-medium">Mục tiêu theo phễu:</Label>
                          <div className="grid grid-cols-1 gap-2 mt-2">
                            {[
                              "Awareness (Nhận biết)",
                              "Consideration (Cân nhắc)",
                              "Conversion (Chuyển đổi)",
                              "Loyalty (Trung thành)"
                            ].map((funnel) => (
                              <div key={funnel} className="flex items-center space-x-2">
                                <Checkbox 
                                  id={funnel}
                                  checked={(formData.content_funnel as string[] || []).includes(funnel)}
                                  onCheckedChange={(checked: boolean) => {
                                    const current = formData.content_funnel as string[] || [];
                                    if (checked) {
                                      handleInputChange('content_funnel', [...current, funnel]);
                                    } else {
                                      handleInputChange('content_funnel', current.filter(item => item !== funnel));
                                    }
                                  }}
                                />
                                <Label htmlFor={funnel} className="text-sm">{funnel}</Label>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Thông điệp và chú đề chính */}
                    <div className="space-y-3">
                      <Label className="text-base font-semibold">Thông điệp và chú đề chính</Label>
                      <Textarea
                        placeholder="Nhập thông điệp chính mà bạn muốn truyền tải..."
                        className="bg-gray-50 border-gray-200 focus:bg-white min-h-[100px]"
                        value={formData.main_message || ""}
                        onChange={(e) => handleInputChange('main_message', e.target.value)}
                      />
                    </div>

                    {/* Cấu hình đại bài viết */}
                    <div className="space-y-3">
                      <Label className="text-base font-semibold">Cấu hình đại bài viết</Label>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-sm">Độ dài nội dung chính (từ):</Label>
                          <Input
                            type="number"
                            placeholder="200"
                            className="bg-gray-50 border-gray-200"
                            value={formData.content_length || ""}
                            onChange={(e) => handleInputChange('content_length', e.target.value)}
                          />
                        </div>  
                        <div>
                          <Label className="text-sm">Độ dài hook (từ):</Label>
                          <Input
                            type="number"
                            placeholder="25"
                            className="bg-gray-50 border-gray-200"
                            value={formData.hook_length || ""}
                            onChange={(e) => handleInputChange('hook_length', e.target.value)}
                          />
                        </div>
                        <div>
                          <Label className="text-sm">Số bài viết:</Label>
                          <Input
                            type="number"
                            placeholder="3"
                            className="bg-gray-50 border-gray-200"
                            value={formData.num_posts || ""}
                            onChange={(e) => handleInputChange('num_posts', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Custom prompt status indicator */}
                    {isCustomPromptLoaded && customMainPrompt && (
                      <div className="mb-4 p-2 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center text-sm text-blue-700">
                            <Lightbulb className="mr-2 h-4 w-4" />
                            <span>Đang sử dụng custom prompt đã chỉnh sửa</span>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              localStorage.removeItem('edited_main_prompt');
                              setCustomMainPrompt(null);
                              setIsCustomPromptLoaded(false);
                              toast.success("Đã xóa custom prompt");
                            }}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    )}

                    <div className="flex space-x-3">
                      <Button 
                        onClick={handleGenerate}
                        disabled={isGenerating || !formData.post_type}
                        className="flex-1"
                      >
                        {isGenerating ? (
                          <>
                            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                            Đang tạo...
                          </>
                        ) : (
                          <>
                            <Sparkles className="mr-2 h-4 w-4" />
                            Tạo nội dung
                          </>
                        )}
                      </Button>
                      <Button variant="outline" onClick={handleLoadTemplate}>
                    <Upload className="mr-2 h-4 w-4" />
                    Tải template
                  </Button>
                  <Button variant="outline" onClick={() => setIsTemplateModalOpen(true)}>
                    <Eye className="mr-2 h-4 w-4" />
                    Xem template
                  </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Generated Content */}
                <Card className="bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="flex items-center">
                        <FileText className="mr-2 h-5 w-5 text-green-600" />
                        Nội dung đã tạo
                      </span>
                      {generatedContent && (
                        <Button variant="outline" size="sm">
                          <Download className="mr-2 h-4 w-4" />
                          Xuất file
                        </Button>
                      )}
                    </CardTitle>
                    <CardDescription className="flex items-center justify-between">
                      <span>Kết quả tạo nội dung cho fanpage</span>
                      {generationDuration && (
                        <div className="flex items-center text-sm text-gray-500">
                          <Clock className="mr-1 h-4 w-4" />
                          <span>Thời gian tạo: {generationDuration.toFixed(2)}s</span>
                        </div>
                      )}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="max-h-465 overflow-y-auto">
                    {isGenerating ? (
                      <LoadingSpinner />
                    ) : generatedContent ? (
                      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                        <TabsList className="grid w-full grid-cols-3">
                          <TabsTrigger value="post">Bài viết</TabsTrigger>
                          <TabsTrigger value="caption">Caption</TabsTrigger>
                          <TabsTrigger value="hashtags">Hashtags</TabsTrigger>
                        </TabsList>

                        <CardDescription className="flex items-center justify-between">
                        {generationDuration && (
                          <div className="flex items-center text-sm text-red-600">
                            <Clock className="mr-1 h-4 w-4" />
                            <span>Thời gian tạo: {generationDuration.toFixed(2)}s</span>
                          </div>
                        )}
                      </CardDescription>
                        
                        <TabsContent value="post" className="mt-0">
                          <div className="bg-gray-50 p-4 rounded-lg overflow-y-auto">
                            <h4 className="font-medium mb-2">Nội dung bài viết:</h4>
                            <div className="whitespace-pre-wrap text-sm text-gray-700">
                              {generatedContent.post_content}
                            </div>
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="caption" className="mt-4">
                          <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
                            <h4 className="font-medium mb-2">Caption:</h4>
                            <div className="whitespace-pre-wrap text-sm text-gray-700">
                              {generatedContent.caption}
                            </div>
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="hashtags" className="mt-4">
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <h4 className="font-medium mb-2">Hashtags:</h4>
                            <div className="flex flex-wrap gap-2">
                              {generatedContent.hashtags?.map((tag: string, index: number) => (
                                <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                                  {tag}
                                </span>
                              )) || []}
                            </div>
                          </div>
                        </TabsContent>
                      </Tabs>
                    ) : (
                      <div className="text-center py-12 text-gray-500">
                        <FileText className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                        <p>Chưa có nội dung nào được tạo</p>
                        <p className="text-sm">Điền thông tin và nhấn "Tạo nội dung" để bắt đầu</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Content History */}
                <ContentHistory onViewDetail={handleViewHistoryDetail} />
              </div>

              {/* Content History Modal */}
              <ContentHistoryModal
                isOpen={isHistoryModalOpen}
                onClose={handleCloseHistoryModal}
                historyId={selectedHistoryId}
              />

              {/* Template List Modal */}
              <TemplateListModal
                isOpen={isTemplateModalOpen}
                onClose={() => setIsTemplateModalOpen(false)}
                onLoadTemplate={(templateData) => {
                  // Load template data into form
                  setFormData(templateData);
                  setIsTemplateModalOpen(false);
                  toast.success("Template đã được tải thành công!");
                }}
              />

              {/* Product Search Dialog */}
              <ProductSearchDialog
                isOpen={isProductSearchOpen}
                onClose={() => setIsProductSearchOpen(false)}
                category={formData.product_type || ""}
                onSelectProduct={formData.product_input_method === "multiple" ? handleMultipleProductSelect : handleProductSelect}
                cachedProducts={cachedProducts}
                multipleMode={formData.product_input_method === "multiple"}
                selectedProducts={selectedProducts}
              />
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}