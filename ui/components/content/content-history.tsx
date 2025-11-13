'use client';

import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Trash2, Eye, Clock, Globe, RefreshCw } from 'lucide-react';
import { useContentStore } from '@/store/content-store';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface ContentHistoryProps {
  onViewDetail?: (id: string) => void;
}

const ContentHistory: React.FC<ContentHistoryProps> = ({ onViewDetail }) => {
  const {
    savedContentHistory,
    setSavedContentHistory,
    isLoadingHistory,
    setIsLoadingHistory,
    isHistoryLoaded,
    setIsHistoryLoaded,
    lastHistoryFetch,
    setLastHistoryFetch,
  } = useContentStore();

  // Luôn fetch data mới khi nhấn nút làm mới
  const shouldFetchFromDB = () => {
    if (!isHistoryLoaded) return true; // Lần đầu load
    return true; // Luôn fetch khi nhấn nút làm mới
  };

  const fetchContentHistory = async (forceRefresh = false) => {
    if (!forceRefresh && !shouldFetchFromDB()) {
      console.log('Sử dụng cache lịch sử từ localStorage');
      return;
    }

    try {
      setIsLoadingHistory(true);
      const history = await api.getContentHistoryList('default_user', 5);
      setSavedContentHistory(history);
      setIsHistoryLoaded(true);
      setLastHistoryFetch(Date.now());
      console.log('Đã tải lịch sử từ DB:', history.length, 'items');
    } catch (error) {
      console.error('Lỗi khi tải lịch sử:', error);
      toast.error('Không thể tải lịch sử nội dung');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteContentHistory(id);
      const updatedHistory = savedContentHistory.filter(item => item.id !== id);
      setSavedContentHistory(updatedHistory);
      toast.success('Đã xóa lịch sử thành công');
    } catch (error) {
      console.error('Lỗi khi xóa lịch sử:', error);
      toast.error('Không thể xóa lịch sử');
    }
  };

  const handleViewDetail = (id: string) => {
    if (onViewDetail) {
      onViewDetail(id);
    }
  };

  const getContentTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'fanpage_post':
        return 'bg-blue-100 text-blue-800';
      case 'blog_post':
        return 'bg-green-100 text-green-800';
      case 'social_media':
        return 'bg-purple-100 text-purple-800';
      case 'email':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getContentTypeLabel = (type: string) => {
    switch (type.toLowerCase()) {
      case 'fanpage_post':
        return 'Facebook';
      case 'blog_post':
        return 'Blog Post';
      case 'social_media':
        return 'Social Media';
      case 'email':
        return 'Email';
      default:
        return type;
    }
  };

  const getContentPreview = (content: string, maxLength: number = 100): string => {
    if (!content) return 'Không có nội dung';
    
    // Loại bỏ markdown và HTML tags
    let cleanContent = content
      .replace(/#{1,6}\s+/g, '') // Remove markdown headers
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
      .replace(/\*(.*?)\*/g, '$1') // Remove italic markdown
      .replace(/<[^>]*>/g, '') // Remove HTML tags
      .replace(/\n+/g, ' ') // Replace newlines with spaces
      .trim();

    if (cleanContent.length <= maxLength) {
      return cleanContent;
    }

    return cleanContent.substring(0, maxLength) + '...';
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch (error) {
      return 'Không xác định';
    }
  };

  // Chỉ load lịch sử lần đầu khi component mount
  useEffect(() => {
    fetchContentHistory();
  }, []);

  const handleManualRefresh = () => {
    fetchContentHistory(true);
  };

  return (
    <Card className="bg-white xl:col-span-2">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Lịch sử nội dung
        </CardTitle>
        <div className="flex items-center gap-2">
          {isHistoryLoaded && (
            <Badge variant="outline" className="text-xs">
              Cache: {savedContentHistory.length} items
            </Badge>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={handleManualRefresh}
            disabled={isLoadingHistory}
            className="flex items-center gap-1"
          >
            <RefreshCw className={`h-4 w-4 ${isLoadingHistory ? 'animate-spin' : ''}`} />
            Làm mới
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoadingHistory && savedContentHistory.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <div className="flex items-center gap-2 text-muted-foreground">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Đang tải lịch sử...
            </div>
          </div>
        ) : savedContentHistory.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            Chưa có lịch sử nội dung nào
          </div>
        ) : (
          <div className="space-y-3">
            {savedContentHistory.map((item) => (
              <div
                key={item.id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      
                      <Globe className="h-3 flex-wrap w-3 mr-0" />
                      <Badge key={item.content_type} className={`text-xs ${getContentTypeColor(item.content_type)}`} variant="secondary">
                        {getContentTypeLabel(item.content_type)}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {formatDate(item.created_at)}
                      </span>
                    </div>
                    <h4 className="font-medium text-sm mb-1 truncate">
                      {item.title || 'Không có tiêu đề'}
                    </h4>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {getContentPreview(item.preview)}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewDetail(item.id)}
                      className="h-8 w-8 p-0"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(item.id)}
                      className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ContentHistory;