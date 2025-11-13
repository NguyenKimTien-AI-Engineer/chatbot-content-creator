"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, Package, X } from "lucide-react";
import { api, Product, ProductSearchRequest } from "@/lib/api";
import { toast } from "sonner";

interface ProductSearchDialogProps {
  isOpen: boolean;
  onClose: () => void;
  category: string;
  onSelectProduct: (product: Product) => void;
  cachedProducts?: Product[];
  multipleMode?: boolean;
  selectedProducts?: Product[];
}

export function ProductSearchDialog({
  isOpen,
  onClose,
  category,
  onSelectProduct,
  cachedProducts = [],
  multipleMode = false,
  selectedProducts = [],
}: ProductSearchDialogProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Load initial products when dialog opens
  useEffect(() => {
    if (isOpen && category) {
      // Use cached products if available, otherwise load from API
      if (cachedProducts.length > 0) {
        setProducts(cachedProducts);
        setHasSearched(true);
      } else {
        loadInitialProducts();
      }
    }
  }, [isOpen, category, cachedProducts]);

  // Search products when query changes
  useEffect(() => {
    if (searchQuery.trim()) {
      const timeoutId = setTimeout(() => {
        searchProducts();
      }, 500); // Debounce search
      return () => clearTimeout(timeoutId);
    } else if (hasSearched) {
      // Use cached products if available, otherwise load from API
      if (cachedProducts.length > 0) {
        setProducts(cachedProducts);
      } else {
        loadInitialProducts();
      }
    }
  }, [searchQuery, cachedProducts]);

  const loadInitialProducts = async () => {
    setIsLoading(true);
    try {
      const response = await api.getProductsByCategory(category, 50);
      setProducts(response.data);
      setHasSearched(true);
    } catch (error) {
      console.error("Error loading products:", error);
      toast.error("Không thể tải danh sách sản phẩm");
    } finally {
      setIsLoading(false);
    }
  };

  const searchProducts = async () => {
    setIsLoading(true);
    try {
      const searchRequest: ProductSearchRequest = {
        category,
        query: searchQuery.trim(),
        limit: 50,
      };
      const response = await api.searchProducts(searchRequest);
      setProducts(response.data);
    } catch (error) {
      console.error("Error searching products:", error);
      toast.error("Không thể tìm kiếm sản phẩm");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectProduct = (product: Product) => {
    onSelectProduct(product);
  };

  const handleClose = () => {
    setSearchQuery("");
    setProducts([]);
    setHasSearched(false);
    onClose();
  };

  const getCategoryDisplayName = (category: string) => {
    switch (category) {
      case "bag":
        return "Túi";
      case "shoes":
        return "Giày";
      case "wallet":
        return "Ví";
      default:
        return category;
    }
  };

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: currency === "VND" ? "VND" : "USD",
    }).format(price);
  };

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent 
        className="max-w-4xl max-h-[80vh] flex flex-col"
        onEscapeKeyDown={(e) => e.preventDefault()}
        onInteractOutside={(e) => e.preventDefault()}
      >
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center gap-2">
              <Package className="w-5 h-5" />
              {multipleMode 
                ? `Chọn nhiều sản phẩm - ${getCategoryDisplayName(category)}`
                : `Tìm kiếm sản phẩm - ${getCategoryDisplayName(category)}`
              }
            </DialogTitle>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Đóng"
              onClick={handleClose}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder={`Tìm kiếm ${getCategoryDisplayName(category).toLowerCase()}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-10"
          />
          {searchQuery && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
              onClick={() => setSearchQuery("")}
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Products List */}
        <ScrollArea className="flex-1 mt-4 max-h-[50vh] overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">Đang tải...</span>
            </div>
          ) : products.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {products.map((product) => {
                const isSelected = multipleMode && selectedProducts.some(p => p.sku === product.sku);
                return (
                  <div
                    key={product.sku}
                    className={`border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer ${
                      isSelected ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                    onClick={() => handleSelectProduct(product)}
                  >
                    <div className="flex gap-4">
                      {/* Product Image */}
                      {product.media && product.media.length > 0 && (
                        <div className="w-20 h-20 flex-shrink-0">
                          <img
                            src={product.media[0].url}
                            alt={product.name}
                            className="w-full h-full object-cover rounded-md"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.src = "/placeholder-product.png";
                            }}
                          />
                        </div>
                      )}

                      {/* Product Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <h3 className="font-medium text-sm line-clamp-2 mb-1">
                            {product.name}
                          </h3>
                          {isSelected && (
                            <div className="ml-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                              Đã chọn
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mb-1">SKU: {product.sku}</p>
                        <p className="text-sm font-semibold text-blue-600">
                          {formatPrice(product.pricing.price, product.pricing.currency)}
                        </p>
                        {product.data.category && product.data.category.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {product.data.category.slice(0, 2).map((cat, index) => (
                              <span
                                key={index}
                                className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                              >
                                {cat}
                              </span>
                            ))}
                            {product.data.category.length > 2 && (
                              <span className="text-xs text-gray-400">
                                +{product.data.category.length - 2}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : hasSearched ? (
            <div className="text-center py-8 text-gray-500">
              <Package className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Không tìm thấy sản phẩm nào</p>
              {searchQuery && (
                <p className="text-sm mt-1">
                  Thử tìm kiếm với từ khóa khác
                </p>
              )}
            </div>
          ) : null}
        </ScrollArea>

        {/* Footer */}
        <div className="flex justify-between items-center pt-4 border-t">
          {multipleMode && (
            <div className="text-sm text-gray-600">
              Đã chọn: {selectedProducts.length} sản phẩm
            </div>
          )}
          <div className="flex gap-2 ml-auto">
            <Button variant="outline" onClick={handleClose}>
              {multipleMode ? "Hoàn thành" : "Đóng"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}