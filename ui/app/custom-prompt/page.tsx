"use client";

import { useState, useEffect } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { Header } from "@/components/layout/header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { 
  Edit3, 
  Save, 
  RefreshCw, 
  FileText, 
  Sparkles, 
  ArrowRight,
  Eye,
  Copy,
  Download,
  Upload,
  Trash2,
  RotateCcw
} from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

interface TemplateInfo {
  name: string;
  file_name: string;
  content_preview: string;
}

interface CustomTemplatesResponse {
  user_id: string;
  templates: Record<string, string>;
}

const TEMPLATE_KEYS = [
  { key: "main_prompt", label: "Content Fanpage Prompt", icon: "" } // New main prompt tab
];

export default function CustomPromptPage() {
  const router = useRouter();
  const [selectedTemplate, setSelectedTemplate] = useState<string>(TEMPLATE_KEYS[0].key);
  const [customTemplates, setCustomTemplates] = useState<Record<string, string>>({});
  const [defaultTemplates, setDefaultTemplates] = useState<Record<string, string>>({});
  const [templateInfo, setTemplateInfo] = useState<Record<string, TemplateInfo>>({});
  const [currentContent, setCurrentContent] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<"edit" | "preview">("edit");
  const [mainPromptContent, setMainPromptContent] = useState<string>("");
  const [editedMainPrompt, setEditedMainPrompt] = useState<string>("");
  const [isTemplateLoaded, setIsTemplateLoaded] = useState<boolean>(false);

  // Load templates on component mount
  useEffect(() => {
    loadTemplates();
    // Clear dữ liệu tạm khi thoát trang
    return () => {
      try {
        sessionStorage.removeItem('temp_main_prompt');
        sessionStorage.removeItem('use_temp_main_prompt');
        console.log('[Templates] Cleared temporary prompt on page unmount');
      } catch (e) {
        console.log('[Templates] Failed to clear temporary prompt', e);
      }
    };
  }, []);

  // Update current content when selected template changes
  useEffect(() => {
    if (selectedTemplate === "main_prompt") {
      setCurrentContent(editedMainPrompt || mainPromptContent);
    } else {
      const customContent = customTemplates[selectedTemplate];
      const defaultContent = defaultTemplates[selectedTemplate];
      setCurrentContent(customContent || defaultContent || "");
    }
  }, [selectedTemplate, customTemplates, defaultTemplates, editedMainPrompt, mainPromptContent]);

  const loadTemplates = async () => {
    setIsLoading(true);
    try {
      // Kiểm tra cache sessionStorage trước khi tải lại từ server
      const cachedLoaded = typeof window !== 'undefined' 
        ? sessionStorage.getItem('isTemplateLoaded') 
        : null;
      if (cachedLoaded === '1') {
        try {
          const cachedCustom = sessionStorage.getItem('custom_templates_cache');
          const cachedDefault = sessionStorage.getItem('default_templates_cache');
          const cachedInfo = sessionStorage.getItem('template_info_cache');
          const cachedMainPrompt = sessionStorage.getItem('main_prompt_full_cache');
          if (cachedCustom) {
            setCustomTemplates(JSON.parse(cachedCustom));
          }
          if (cachedDefault) {
            setDefaultTemplates(JSON.parse(cachedDefault));
          }
          if (cachedInfo) {
            setTemplateInfo(JSON.parse(cachedInfo));
          }
          if (cachedMainPrompt) {
            setMainPromptContent(cachedMainPrompt);
          }
          const storedEdit = typeof window !== 'undefined' 
            ? localStorage.getItem('edited_main_prompt') 
            : null;
          if (storedEdit) {
            setEditedMainPrompt(storedEdit);
          }
          setIsTemplateLoaded(true);
          console.log('[Templates] Loaded from session cache');
          setIsLoading(false);
          toast.success("Đã tải templates từ cache phiên!");
          return;
        } catch (e) {
          console.log('[Templates] Cache parse failed', e);
        }
      }

      // Load custom templates for default user
      const customResponse = await fetch('http://localhost:8001/api/v1/prompt-templates/custom/default');
      if (customResponse.ok) {
        const customData: CustomTemplatesResponse = await customResponse.json();
        setCustomTemplates(customData.templates);
        try {
          sessionStorage.setItem('custom_templates_cache', JSON.stringify(customData.templates || {}));
        } catch (e) {
          console.log('[Templates] Failed to cache custom templates', e);
        }
      }

      // Load default variables from YAML
      const defaultsResponse = await fetch('http://localhost:8001/api/v1/prompt-templates/variables');
        if (defaultsResponse.ok) {
          const defaultsData = await defaultsResponse.json();
          const vars = defaultsData.variables || {};
          setDefaultTemplates(vars);
          try {
            sessionStorage.setItem('default_templates_cache', JSON.stringify(vars || {}));
          } catch (e) {
            console.log('[Templates] Failed to cache default templates', e);
          }

          // Optional: load template info for labels/placeholders
          const infoResponse = await fetch('http://localhost:8001/api/v1/prompt-templates/info');
          if (infoResponse.ok) {
            const infoData = await infoResponse.json();
            const infoTemplates = infoData.templates || {};
            const mappedInfo: Record<string, TemplateInfo> = {};
            Object.keys(infoTemplates).forEach((key) => {
              mappedInfo[key] = {
                name: infoTemplates[key].name,
                file_name: 'content_fanpage_prompts.yaml',
                content_preview: String(vars[key] || '').slice(0, 160)
              };
            });
            setTemplateInfo(mappedInfo);
            try {
              sessionStorage.setItem('template_info_cache', JSON.stringify(mappedInfo || {}));
            } catch (e) {
              console.log('[Templates] Failed to cache template info', e);
            }
          }
      }

      // Load full main prompt (cache per-tab using sessionStorage)
      const cachedMainPrompt = typeof window !== 'undefined' 
        ? sessionStorage.getItem('main_prompt_full_cache') 
        : null;

      if (cachedMainPrompt) {
        setMainPromptContent(cachedMainPrompt);
      } else {
        const fullResponse = await fetch('http://localhost:8001/api/v1/prompt-templates/full');
        if (fullResponse.ok) {
          const fullData = await fullResponse.json();
          setMainPromptContent(fullData.content);
          try {
            sessionStorage.setItem('main_prompt_full_cache', fullData.content || '');
          } catch (e) {
            // Ignore storage errors silently
          }
        }
      }

      // Check local storage for edited version
      const storedEdit = typeof window !== 'undefined' 
        ? localStorage.getItem('edited_main_prompt') 
        : null;
      if (storedEdit) {
        setEditedMainPrompt(storedEdit);
      }

      toast.success("Đã tải templates thành công!");
      try {
        sessionStorage.setItem('isTemplateLoaded', '1');
        setIsTemplateLoaded(true);
      } catch (e) {
        console.log('[Templates] Failed to set isTemplateLoaded', e);
      }
    } catch (error) {
      console.error("Error loading templates:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveCustomTemplate = async () => {
    if (!selectedTemplate || !currentContent.trim()) {
      toast.error("Vui lòng chọn template và nhập nội dung");
      return;
    }

    if (selectedTemplate === "main_prompt") {
      // Gọi API lưu custom prompt với versioning
      setIsSaving(true);
      try {
        console.log('[Templates] Saving custom main prompt via API', { contentLength: currentContent.length });
        
        const response = await fetch('http://localhost:8001/api/v1/content/save-custom-prompt', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            prompt_content: currentContent,
            prompt_type: 'fanpage_content'
          })
        });

        if (response.ok) {
          const result = await response.json();
          console.log('[Templates] Custom prompt saved successfully', { 
            version: result.version, 
            file_path: result.file_path 
          });
          
          // Lưu vào sessionStorage để sử dụng tạm thời
          try {
            sessionStorage.setItem('temp_main_prompt', currentContent);
            sessionStorage.setItem('use_temp_main_prompt', '1');
          } catch (e) {
            console.log('[Templates] Failed to set temp_main_prompt flag', e);
          }
          
          setEditedMainPrompt(currentContent);
          toast.success(`Đã lưu custom prompt thành công! (Version: ${result.version})`);
        } else {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to save custom prompt');
        }
      } catch (error) {
        console.error("Error saving custom prompt:", error);
      } finally {
        setIsSaving(false);
      }
      return;
    }

    // Các template khác vẫn dùng API cũ
    setIsSaving(true);
    try {
      console.log('[Templates] Saving template to server', { key: selectedTemplate, length: currentContent.length });
      const updatedTemplates = {
        ...customTemplates,
        [selectedTemplate]: currentContent
      };

      const response = await fetch('http://localhost:8001/api/v1/prompt-templates/custom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'default',
          templates: updatedTemplates
        })
      });

      if (response.ok) {
        setCustomTemplates(updatedTemplates);
        toast.success("Đã lưu template thành công!");
      } else {
        throw new Error('Failed to save template');
      }
    } catch (error) {
      console.error("Error saving template:", error);
      toast.error("Lỗi khi lưu template");
    } finally {
      setIsSaving(false);
    }
  };

  const resetToDefault = async () => {
    if (selectedTemplate === "main_prompt") {
      localStorage.removeItem('edited_main_prompt');
      setEditedMainPrompt("");
      setCurrentContent(mainPromptContent);
      toast.success("Đã reset prompt chính về mặc định!");
      return;
    }

    const defaultContent = defaultTemplates[selectedTemplate];
    if (!defaultContent) {
      toast.error("Không có nội dung mặc định để reset");
      return;
    }

    try {
      const response = await fetch('http://localhost:8001/api/v1/prompt-templates/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default',
          key: selectedTemplate,
          default_value: defaultContent
        })
      });

      if (!response.ok) {
        throw new Error('Reset request failed');
      }

      // Cập nhật UI state sau khi reset thành công
      const updatedCustom = { ...customTemplates };
      delete updatedCustom[selectedTemplate];
      setCustomTemplates(updatedCustom);
      setCurrentContent(defaultContent);
      toast.success("Đã reset về template mặc định và đồng bộ server");
    } catch (error) {
      console.error("Error resetting template:", error);
      toast.error("Lỗi khi reset template về mặc định");
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(currentContent);
      toast.success("Đã copy nội dung");
    } catch (error) {
      toast.error("Lỗi khi copy nội dung");
    }
  };

  const exportTemplate = () => {
    const dataStr = JSON.stringify({ [selectedTemplate]: currentContent }, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${selectedTemplate}_template.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    toast.success("Đã export template");
  };

  const navigateToFanpage = () => {
    const willUseTemp = selectedTemplate === 'main_prompt';
    if (willUseTemp) {
      const toUse = editedMainPrompt || currentContent;
      try {
        sessionStorage.setItem('temp_main_prompt', toUse || '');
        sessionStorage.setItem('use_temp_main_prompt', '1');
        console.log('[Navigate] Set temp main prompt for fanpage', { length: (toUse || '').length });
      } catch (e) {
        console.log('[Navigate] Failed to set temp prompt', e);
      }
    }
    console.log('[Navigate] Using customized prompt?', { selectedTemplate, isUsingTemp: willUseTemp, editedLen: editedMainPrompt.length, currentLen: currentContent.length });
    router.push('/fanpage');
    toast.success("Chuyển đến trang tạo nội dung Fanpage");
  };

  const getTemplateIcon = (key: string) => {
    return TEMPLATE_KEYS.find(t => t.key === key)?.icon || "";
  };

  const getTemplateLabel = (key: string) => {
    return TEMPLATE_KEYS.find(t => t.key === key)?.label || key;
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen w-full">
        <AppSidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto p-6 bg-white/95 via-indigo-50 to-purple-50">
            <div className="w-full">
              {/* Header Section */}
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-gray-900">
                    Custom Prompt Editor
                  </h1>
                  <p className="text-gray-600 mt-2">
                    Tùy chỉnh và chỉnh sửa các template prompt theo ý muốn của bạn
                  </p>
                </div>
                <Button 
                  onClick={navigateToFanpage}
                  className="from-gray-500 to-emerald-600 hover:from-gray-600 hover:to-emerald-700"
                >
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Tạo nội dung Fanpage
                </Button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-4">
                {/* Template Selection Sidebar */}
                <Card className="lg:col-span-1 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Edit3 className="w-5 h-5 text-blue-600" />
                      Templates
                    </CardTitle>
                    <CardDescription>
                      Chọn template để chỉnh sửa
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {TEMPLATE_KEYS.map((template) => (
                      <Button
                        key={template.key}
                        variant={selectedTemplate === template.key ? "default" : "ghost"}
                        className={`w-full justify-start text-left h-auto p-3 ${
                          selectedTemplate === template.key 
                            ? "from-gray-500 to-purple-600 text-white shadow-md" 
                            : "hover:bg-gray-50"
                        }`}
                        onClick={() => setSelectedTemplate(template.key)}
                      >
                        <div className="flex items-center gap-3 w-full">
                          <span className="text-lg">{template.icon}</span>
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-sm truncate">
                              {template.label}
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                              {customTemplates[template.key] && (
                                <Badge variant="secondary" className="text-xs">
                                  Custom
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </Button>
                    ))}
                  </CardContent>
                </Card>

                {/* Main Editor Area */}
                <div className="lg:col-span-3 space-y-6 max-h-[calc(100vh-220px)] overflow-y-auto">
                  {/* Editor Tabs */}
                  <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                    <CardHeader className="pb-4">
                      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as "edit" | "preview")}>
                        <div className="flex items-center justify-between">
                          <TabsList className="grid w-fit grid-cols-2">
                            <TabsTrigger value="edit" className="flex items-center gap-2">
                              <Edit3 className="w-4 h-4" />
                              Chỉnh sửa
                            </TabsTrigger>
                            <TabsTrigger value="preview" className="flex items-center gap-2">
                              <Eye className="w-4 h-4" />
                              Xem trước
                            </TabsTrigger>
                          </TabsList>
                          
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={resetToDefault}
                              disabled={!defaultTemplates[selectedTemplate]}
                            >
                              <RotateCcw className="w-4 h-4 mr-2" />
                              Reset
                            </Button>
                            <Button
                              onClick={saveCustomTemplate}
                              disabled={isSaving || !String(currentContent || "").trim()}
                              className="to-purple-600 hover:from-blue-600 hover:to-purple-700"
                            >
                              {isSaving ? (
                                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                              ) : (
                                <Save className="w-4 h-4 mr-2" />
                              )}
                              Lưu Template
                            </Button>
                          </div>
                        </div>

                        <TabsContent value="edit" className="mt-4">
                          <Textarea
                            value={currentContent}
                            onChange={(e) => setCurrentContent(e.target.value)}
                            placeholder="Nhập nội dung template của bạn..."
                            className="min-h-[500px] max-h-[700px] overflow-y-auto font-mono text-sm resize-none border-2 border-dashed border-gray-200 focus:border-blue-400 transition-colors"
                          />
                        </TabsContent>

                        <TabsContent value="preview" className="mt-4">
                          <div className="min-h-[500px] p-6 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200 overflow-y-auto max-h-[700px]">
                            <div className="prose max-w-none">
                              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-gray-800">
                                {currentContent || "Chưa có nội dung để xem trước..."}
                              </pre>
                            </div>
                          </div>
                        </TabsContent>
                      </Tabs>
                    </CardHeader>
                  </Card>

                  {/* Action Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="shadow-lg border-0 to-emerald-50 hover:shadow-xl transition-shadow cursor-pointer" onClick={navigateToFanpage}>
                      <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                          <div className="p-3 rounded-full">
                            <FileText className="w-6 h-6 text-green-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-green-800">Tạo nội dung</h3>
                            <p className="text-sm text-green-600">Sử dụng prompt đã tùy chỉnh</p>
                          </div>
                          <ArrowRight className="w-5 h-5 text-green-600 ml-auto" />
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="shadow-lg border-0 to-pink-50 hover:shadow-xl transition-shadow cursor-pointer" onClick={loadTemplates}>
                      <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                          <div className="p-3 bg-purple-100 rounded-full">
                            <RefreshCw className="w-6 h-6 text-purple-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-purple-800">Tải lại Templates</h3>
                            <p className="text-sm text-purple-600">Cập nhật từ server</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}