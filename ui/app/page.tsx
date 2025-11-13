"use client";

import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { Header } from "@/components/layout/header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, BarChart3, Sparkles, TrendingUp, Edit3 } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
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
                  Chào mừng đến với AI Content Generator
                </h1>
                <p className="text-gray-600">
                  Tạo nội dung chất lượng cao với sức mạnh của AI
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <Card className="bg-white hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center text-blue-700">
                      <FileText className="mr-2 h-5 w-5" />
                      Tạo nội dung Fanpage
                    </CardTitle>
                    <CardDescription>
                      Tạo bài viết, caption và hashtag cho fanpage Facebook
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button asChild className="w-full">
                      <Link href="/fanpage">Bắt đầu tạo</Link>
                    </Button>
                  </CardContent>
                </Card>

                <Card className="bg-white hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center text-green-700">
                      <BarChart3 className="mr-2 h-5 w-5" />
                      Kế hoạch nội dung
                    </CardTitle>
                    <CardDescription>
                      Lập kế hoạch và lịch đăng nội dung hiệu quả
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button asChild variant="outline" className="w-full">
                      <Link href="/plan">Xem kế hoạch</Link>
                    </Button>
                  </CardContent>
                </Card>

                <Card className="bg-white hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center text-purple-700">
                      <Sparkles className="mr-2 h-5 w-5" />
                      Branding
                    </CardTitle>
                    <CardDescription>
                      Quản lý thương hiệu và phong cách nội dung
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button asChild variant="outline" className="w-full">
                      <Link href="/branding">Quản lý brand</Link>
                    </Button>
                  </CardContent>
                </Card>

                <Card className="bg-white hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center text-orange-700">
                      <Edit3 className="mr-2 h-5 w-5" />
                      Custom Prompt
                    </CardTitle>
                    <CardDescription>
                      Tùy chỉnh và quản lý prompt templates theo ý muốn
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button asChild variant="outline" className="w-full">
                      <Link href="/custom-prompt">Chỉnh sửa prompt</Link>
                    </Button>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <TrendingUp className="mr-2 h-5 w-5 text-green-600" />
                      Thống kê sử dụng
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Nội dung đã tạo</span>
                        <span className="font-semibold">0</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Templates đã sử dụng</span>
                        <span className="font-semibold">0</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Thời gian tiết kiệm</span>
                        <span className="font-semibold">0 giờ</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-white">
                  <CardHeader>
                    <CardTitle>Bắt đầu nhanh</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <p className="text-gray-600 text-sm">
                        Khám phá các tính năng mạnh mẽ của AI Content Generator:
                      </p>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-center text-gray-700">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                          Tạo nội dung fanpage tự động
                        </li>
                        <li className="flex items-center text-gray-700">
                          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                          Lập kế hoạch nội dung thông minh
                        </li>
                        <li className="flex items-center text-gray-700">
                          <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                          Quản lý thương hiệu chuyên nghiệp
                        </li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
