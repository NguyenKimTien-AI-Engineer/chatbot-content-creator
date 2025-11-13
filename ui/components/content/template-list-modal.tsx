"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Calendar, FileText, Globe, MessageSquare, Package, Trash2, Download } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface TemplateItem {
  template_id: string;
  template_name?: string;
  template_description?: string;
  created_at: string;
  platforms: string[];
  main_message: string;
  product_name?: string;
  // Full template configuration fields
  product_info?: any;
  post_info?: any;
  target_audience?: any;
  objectives?: any;
  content?: any;
  content_settings?: any;
}

interface TemplateListModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTemplate?: (templateId: string) => void;
  onLoadTemplate?: (templateData: any) => void;
}

export function TemplateListModal({ isOpen, onClose, onSelectTemplate, onLoadTemplate }: TemplateListModalProps) {
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateItem | null>(null);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await api.getTemplateList(20); // Lấy 20 templates
      if (response.success) {
        setTemplates(response.templates || []);
      } else {
        toast.error(response.message || "Không thể tải danh sách template");
      }
    } catch (error: any) {
      console.error("Error fetching templates:", error);
      toast.error("Có lỗi xảy ra khi tải danh sách template");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchTemplates();
    }
  }, [isOpen]);

  const handleSelectTemplate = (template: TemplateItem) => {
    setSelectedTemplate(template);
  };

  const handleLoadTemplate = async (templateId: string) => {
    try {
      // Fetch full template data
      const response = await api.getLatestTemplate();
      if (response.success && response.template && onLoadTemplate) {
        onLoadTemplate(response.template);
        toast.success("Template đã được tải thành công!");
        onClose();
      } else if (onSelectTemplate) {
        onSelectTemplate(templateId);
        toast.success("Đã chọn template để tải");
        onClose();
      }
    } catch (error: any) {
      console.error("Error loading template:", error);
      toast.error("Có lỗi xảy ra khi tải template");
    }
  };

  const handleDeleteTemplate = async (templateId: string) => {
    try {
      const response = await api.deleteTemplate(templateId);
      if (response.success) {
        toast.success("Đã xóa template thành công");
        fetchTemplates(); // Refresh list
      } else {
        toast.error(response.message || "Không thể xóa template");
      }
    } catch (error: any) {
      console.error("Error deleting template:", error);
      toast.error("Có lỗi xảy ra khi xóa template");
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('vi-VN');
    } catch {
      return dateString;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'facebook':
        return 'bg-blue-100 text-blue-800';
      case 'instagram':
        return 'bg-pink-100 text-pink-800';
      case 'tiktok':
        return 'bg-gray-100 text-gray-800';
      case 'web branding':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <FileText className="mr-2 h-5 w-5 text-blue-600" />
            Danh sách Template ({templates.length})
          </DialogTitle>
        </DialogHeader>

        <div className="flex gap-4 h-[70vh]">
          {/* Template List */}
          <div className="flex-1">
            <ScrollArea className="h-full">
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : templates.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>Chưa có template nào được lưu</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {templates.map((template) => (
                    <Card 
                      key={template.template_id}
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        selectedTemplate?.template_id === template.template_id 
                          ? 'ring-2 ring-blue-500 bg-blue-50' 
                          : ''
                      }`}
                      onClick={() => handleSelectTemplate(template)}
                    >
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="text-sm font-medium">
                              {template.template_name || `Template ${template.template_id.slice(-8)}`}
                            </CardTitle>
                            <CardDescription className="text-xs mt-1">
                              {template.template_description || "Không có mô tả"}
                            </CardDescription>
                          </div>
                          <div className="flex gap-1">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation();
                                if (onLoadTemplate) {
                                  handleLoadTemplate(template.template_id);
                                }
                              }}
                            >
                              <Download className="h-3 w-3 mr-1" />
                              Áp dụng
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleLoadTemplate(template.template_id);
                              }}
                            >
                              <Download className="h-3 w-3 mr-1" />
                              Tải
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteTemplate(template.template_id);
                              }}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                          <Calendar className="h-3 w-3" />
                          {formatDate(template.created_at)}
                        </div>
                        
                        <div className="flex flex-wrap gap-1 mb-2">
                          {template.platforms.map((platform) => (
                            <Badge 
                              key={platform} 
                              variant="secondary" 
                              className={`text-xs ${getPlatformColor(platform)}`}
                            >
                              <Globe className="h-3 w-3 mr-1" />
                              {platform}
                            </Badge>
                          ))}
                        </div>

                        {template.main_message && (
                          <div className="flex items-start gap-2 text-xs">
                            <MessageSquare className="h-3 w-3 mt-0.5 text-gray-400" />
                            <span className="text-gray-600 line-clamp-2">
                              {template.main_message}
                            </span>
                          </div>
                        )}

                        {template.product_name && (
                          <div className="flex items-center gap-2 text-xs mt-1">
                            <Package className="h-3 w-3 text-gray-400" />
                            <span className="text-gray-600">{template.product_name}</span>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>

          {/* Template Detail */}
          {selectedTemplate && (
            <>
              <Separator orientation="vertical" />
              <div className="w-80">
                <ScrollArea className="h-full">
                  <div className="p-4">
                    <h3 className="font-semibold mb-4">Chi tiết Template</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Tên Template</label>
                        <p className="text-sm text-gray-900 mt-1">
                          {selectedTemplate.template_name || `Template ${selectedTemplate.template_id.slice(-8)}`}
                        </p>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Mô tả</label>
                        <p className="text-sm text-gray-900 mt-1">
                          {selectedTemplate.template_description || "Không có mô tả"}
                        </p>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Ngày tạo</label>
                        <p className="text-sm text-gray-900 mt-1">
                          {formatDate(selectedTemplate.created_at)}
                        </p>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Platforms</label>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {selectedTemplate.platforms.map((platform) => (
                            <Badge 
                              key={platform} 
                              variant="secondary" 
                              className={`text-xs ${getPlatformColor(platform)}`}
                            >
                              {platform}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Thông điệp chính</label>
                        <p className="text-sm text-gray-900 mt-1">
                          {selectedTemplate.main_message || "Không có thông điệp"}
                        </p>
                      </div>

                      {selectedTemplate.product_name && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">Sản phẩm</label>
                          <p className="text-sm text-gray-900 mt-1">
                            {selectedTemplate.product_name}
                          </p>
                        </div>
                      )}

                      {selectedTemplate.target_audience && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">Đối tượng mục tiêu</label>
                          <div className="mt-1 space-y-1">
                            {selectedTemplate.target_audience.segments && (
                              <div>
                                <span className="text-xs font-medium text-gray-600">Phân khúc:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {selectedTemplate.target_audience.segments.map((segment: string, index: number) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {segment}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                            {selectedTemplate.target_audience.specific_targets && (
                              <div>
                                <span className="text-xs font-medium text-gray-600">Mục tiêu cụ thể:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {selectedTemplate.target_audience.specific_targets.map((target: string, index: number) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {target}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {selectedTemplate.objectives && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">Mục tiêu</label>
                          <div className="mt-1 space-y-1">
                            {selectedTemplate.objectives.main && (
                              <div>
                                <span className="text-xs font-medium text-gray-600">Mục tiêu chính:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {selectedTemplate.objectives.main.map((obj: string, index: number) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {obj}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                            {selectedTemplate.objectives.funnel && (
                              <div>
                                <span className="text-xs font-medium text-gray-600">Funnel:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {selectedTemplate.objectives.funnel.map((funnel: string, index: number) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {funnel}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {selectedTemplate.content && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">Nội dung</label>
                          <div className="mt-1 space-y-1">
                            {selectedTemplate.content.pillars && (
                              <div>
                                <span className="text-xs font-medium text-gray-600">Trụ cột nội dung:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {selectedTemplate.content.pillars.map((pillar: string, index: number) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {pillar}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                            {selectedTemplate.content.use_cases && (
                              <div>
                                <span className="text-xs font-medium text-gray-600">Use cases:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {selectedTemplate.content.use_cases.map((useCase: string, index: number) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {useCase}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {selectedTemplate.content_settings && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">Cài đặt nội dung</label>
                          <div className="mt-1 space-y-1">
                            {selectedTemplate.content_settings.content_length && (
                              <p className="text-xs text-gray-600">
                                Độ dài nội dung: {selectedTemplate.content_settings.content_length}
                              </p>
                            )}
                            {selectedTemplate.content_settings.hook_length && (
                              <p className="text-xs text-gray-600">
                                Độ dài hook: {selectedTemplate.content_settings.hook_length}
                              </p>
                            )}
                          </div>
                        </div>
                      )}

                      {selectedTemplate.post_info && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">Thông tin bài post</label>
                          <div className="mt-1">
                            {selectedTemplate.post_info.post_type && (
                              <p className="text-xs text-gray-600">
                                Loại bài post: {selectedTemplate.post_info.post_type}
                              </p>
                            )}
                          </div>
                        </div>
                      )}

                      <div className="pt-4 border-t">
                        <div className="flex gap-2">
                          <Button 
                            className="flex-1"
                            variant="outline"
                            onClick={() => {
                              if (onLoadTemplate && selectedTemplate) {
                                // Fetch full template data and apply to form
                                handleLoadTemplate(selectedTemplate.template_id);
                              }
                            }}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Áp dụng
                          </Button>
                          <Button 
                            className="flex-1"
                            onClick={() => handleLoadTemplate(selectedTemplate.template_id)}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Tải Template
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </ScrollArea>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}