"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, FileText, Copy, Download } from "lucide-react";
import { useContentStore } from "@/store/content-store";
import { api, ContentHistoryDetail } from "@/lib/api";
import { toast } from "sonner";

interface ContentHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  historyId: string | null;
}

export function ContentHistoryModal({ isOpen, onClose, historyId }: ContentHistoryModalProps) {
  const [historyDetail, setHistoryDetail] = useState<ContentHistoryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parsedContent, setParsedContent] = useState<any>(null);

  useEffect(() => {
    if (isOpen && historyId) {
      loadHistoryDetail();
    }
  }, [isOpen, historyId]);

  const loadHistoryDetail = async () => {
    if (!historyId) return;
    
    try {
      setIsLoading(true);
      const detail = await api.getContentHistoryDetail(historyId);
      setHistoryDetail(detail);
      
      // Parse content JSON
      try {
        const content = JSON.parse(detail.content);
        setParsedContent(content);
      } catch (error) {
        console.error("Lỗi parse content:", error);
        setParsedContent({ raw_content: detail.content });
      }
    } catch (error) {
      console.error("Lỗi khi tải chi tiết:", error);
      toast.error("Không thể tải chi tiết lịch sử");
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getContentTypeLabel = (type: string) => {
    switch (type) {
      case 'fanpage':
        return 'Fanpage';
      case 'blog':
        return 'Blog';
      case 'social':
        return 'Social Media';
      default:
        return 'Nội dung';
    }
  };

  const getContentTypeColor = (type: string) => {
    switch (type) {
      case 'fanpage':
        return 'bg-blue-100 text-blue-800';
      case 'blog':
        return 'bg-green-100 text-green-800';
      case 'social':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Đã sao chép vào clipboard");
  };

  const exportContent = () => {
    if (!historyDetail || !parsedContent) return;
    
    const exportData = {
      title: historyDetail.title,
      content_type: historyDetail.content_type,
      created_at: historyDetail.created_at,
      content: parsedContent,
      metadata: historyDetail.metadata
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `content-${historyDetail.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success("Đã xuất nội dung thành công");
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[95vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center mt-4 justify-between">
            <span className="flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Chi tiết lịch sử nội dung
            </span>
            {historyDetail && (
              <div className="flex space-x-8">
                <Button variant="outline" size="sm" onClick={exportContent}>
                  <Download className="mr-2 h-6 w-4" />
                  Xuất
                </Button>
              </div>
            )}
          </DialogTitle>
          <DialogDescription>
            Xem chi tiết nội dung đã tạo và thông tin liên quan
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : historyDetail ? (
          <ScrollArea className="max-h-[70vh]">
            <div className="space-y-6">
              {/* Header Info */}
              <Card>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{historyDetail.title}</CardTitle>
                      <CardDescription className="mt-1">
                        <div className="flex items-center space-x-4">
                          <Badge 
                            variant="secondary" 
                            className={getContentTypeColor(historyDetail.content_type)}
                          >
                            {getContentTypeLabel(historyDetail.content_type)}
                          </Badge>
                          <span className="flex items-center text-sm text-gray-500">
                            <Clock className="mr-1 h-3 w-3" />
                            {formatDate(historyDetail.created_at)}
                          </span>
                        </div>
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* Content Tabs */}
              {parsedContent && (
                <Tabs defaultValue="content" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="content">Nội dung</TabsTrigger>
                    <TabsTrigger value="metadata">Thông tin</TabsTrigger>
                    <TabsTrigger value="settings">Cài đặt</TabsTrigger>
                  </TabsList>

                  <TabsContent value="content" className="space-y-4">
                    {parsedContent.post_content && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center justify-between">
                            Bài viết
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(parsedContent.post_content)}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <pre className="whitespace-pre-wrap text-sm">
                              {parsedContent.post_content}
                            </pre>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {parsedContent.caption && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center justify-between">
                            Caption
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(parsedContent.caption)}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <pre className="whitespace-pre-wrap text-sm">
                              {parsedContent.caption}
                            </pre>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {parsedContent.hashtags && parsedContent.hashtags.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center justify-between">
                            Hashtags
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(parsedContent.hashtags.join(' '))}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="flex flex-wrap gap-2">
                            {parsedContent.hashtags.map((tag: string, index: number) => (
                              <Badge key={index} variant="outline">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </TabsContent>

                  <TabsContent value="metadata" className="space-y-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Thông tin metadata</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {historyDetail.metadata && Object.entries(historyDetail.metadata).map(([key, value]) => (
                            <div key={key} className="flex justify-between py-2 border-b border-gray-100">
                              <span className="font-medium text-gray-700 capitalize">
                                {key.replace(/_/g, ' ')}:
                              </span>
                              <span className="text-gray-600">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="settings" className="space-y-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Cài đặt form</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {parsedContent.form_data && (
                          <div className="space-y-3">
                            {Object.entries(parsedContent.form_data).map(([key, value]) => (
                              <div key={key} className="flex justify-between py-2 border-b border-gray-100">
                                <span className="font-medium text-gray-700 capitalize">
                                  {key.replace(/_/g, ' ')}:
                                </span>
                                <span className="text-gray-600">
                                  {Array.isArray(value) ? value.join(', ') : String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              )}
            </div>
          </ScrollArea>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <FileText className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <p>Không thể tải chi tiết lịch sử</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}