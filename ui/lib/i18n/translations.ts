export type Locale = "en" | "vi";

export const translations = {
  en: {
    nav: {
      home: "Home",
      chat: "Chat",
      settings: "Settings",
    },
    header: {
      search: "Search...",
      notificationsSoon: "Notifications (coming soon)",
      personalInfo: "Personal info",
      logout: "Log out",
      comingSoon: "Coming soon",
      noEmail: "No email",
    },
    home: {
      badge: "KAT Content Studio",
      greeting: "Hello, {name}",
      subtitle:
        "AI content platform for KAT Leather. Start chatting or configure the system in settings.",
      openChat: "Open Chat",
      settings: "Settings",
      quickAccess: "Quick access",
      writeMarketing: "Write marketing copy",
      fanpageCaption: "Fanpage caption",
      productAdvice: "Product advice",
      features: "Features",
      open: "Open",
      ready: "Ready",
      access: "Open",
      quickStart: "Quick start",
      quickStartChat: "Open Chat and pick a suggested prompt",
      quickStartSettings: "Customize Gemini models and prompts in Settings",
      quickStartDev: "Fanpage, Branding, and Planning modules are in development",
      stats: "Usage stats",
      statsSoon: "Coming soon",
      contentCreated: "Content created",
      templatesUsed: "Templates used",
      timeSaved: "Time saved",
      dash: "—",
      featuresList: {
        chat: {
          title: "AI Chat",
          description: "Chat, marketing content, and captions powered by Gemini",
        },
        settings: {
          title: "Settings",
          description: "Configure AI, chatbot, brand, and API connection",
        },
        fanpage: {
          title: "Fanpage content",
          description: "Posts, captions, and hashtags for Facebook",
        },
        plan: {
          title: "Content plan",
          description: "Scheduling and posting strategy",
        },
        branding: {
          title: "Branding",
          description: "Tone of voice and brand style",
        },
        prompt: {
          title: "Custom prompt",
          description: "Create and manage prompt templates",
        },
      },
    },
    chat: {
      badge: "AI Content Assistant · KAT Leather",
      emptyHeadline: "Where should we begin?",
      newChat: "New chat",
      greeting: "Hello, {name}",
      subtitle:
        "Create marketing content, fanpage captions, and leather bag product advice.",
      inputPlaceholder: "Ask anything",
      add: "Add",
      uploading: "Uploading...",
      addFiles: "Add photos & files",
      addEmoji: "Insert emoji",
      removeImage: "Remove image",
      disclaimer: "AI can make mistakes. Check important information.",
      showSystem: "Show system instructions",
      hideSystem: "Hide system instructions",
      systemPlaceholder: "Enter user system instructions...",
      processing: "Uploading and processing document...",
      prompts: {
        marketing: {
          title: "Marketing",
          prompt:
            "I want to write a marketing post for KAT Leather. Ask me about goals, audience, and tone before writing.",
        },
        product: {
          title: "Product intro",
          prompt:
            "Help me write product content for a KAT Leather bag. Ask for product name, color, and key selling points.",
        },
        caption: {
          title: "Fanpage caption",
          prompt:
            "I need a fanpage caption for KAT Leather. Ask about post type, product, and desired length before writing.",
        },
        hashtag: {
          title: "Hashtag & CTA",
          prompt:
            "Suggest hashtags and a call-to-action for a premium KAT Leather fashion post.",
        },
        customer: {
          title: "Customer reply",
          prompt:
            "A customer asks about leather quality and bag care for KAT Leather. Draft a friendly, professional reply.",
        },
        trend: {
          title: "Content trends",
          prompt:
            "Suggest 5 marketing content ideas for KAT Leather this week, each with a strong hook.",
        },
        story: {
          title: "Storytelling",
          prompt:
            "Write a short brand story about KAT Leather's craftsmanship and genuine leather quality since 2009.",
        },
        consult: {
          title: "Content strategy",
          prompt:
            "I need content marketing strategy advice for a premium leather bag brand. Start by asking about my business goals.",
        },
      },
      imageDefaultOne: "Analyze this image and describe how it feels",
      imageDefaultTwo: "Analyze these two images and describe how they feel",
      historyTitle: "Chat history",
      historyLoading: "Loading...",
      historyEmpty: "No conversations yet",
      historyDelete: "Delete",
      historyDeleteTitle: "Delete conversation?",
      historyDeleteDesc: "This action cannot be undone.",
      openChatLink: "Open chat",
    },
    settings: {
      hub: "Configuration hub",
      title: "Settings",
      subtitle:
        "Customize AI, chatbot, brand, and API connection for KAT Content Studio.",
      synced: "Synced",
      unsaved: "Unsaved changes",
      geminiApi: "Gemini API",
      categories: "Categories",
      pickCategory: "Choose a section to configure",
      saveHintSaved: "All changes saved.",
      saveHintDirty: "You have unsaved changes.",
      reset: "Reset to defaults",
      save: "Save settings",
      language: "Interface language",
      languageDesc: "Display language across the app",
      english: "English",
      vietnamese: "Vietnamese",
    },
    common: {
      popular: "Popular",
      cancel: "Cancel",
    },
  },
  vi: {
    nav: {
      home: "Trang chủ",
      chat: "Chat",
      settings: "Cài đặt",
    },
    header: {
      search: "Tìm kiếm...",
      notificationsSoon: "Thông báo (sắp ra mắt)",
      personalInfo: "Thông tin cá nhân",
      logout: "Đăng xuất",
      comingSoon: "Sắp ra mắt",
      noEmail: "Chưa có email",
    },
    home: {
      badge: "KAT Content Studio",
      greeting: "Xin chào, {name}",
      subtitle:
        "Nền tảng tạo nội dung AI cho KAT Leather. Bắt đầu chat ngay hoặc cấu hình hệ thống trong phần cài đặt.",
      openChat: "Mở Chat",
      settings: "Cài đặt",
      quickAccess: "Truy cập nhanh",
      writeMarketing: "Viết bài marketing",
      fanpageCaption: "Caption fanpage",
      productAdvice: "Tư vấn sản phẩm",
      features: "Tính năng",
      open: "Mở",
      ready: "Sẵn sàng",
      access: "Truy cập",
      quickStart: "Bắt đầu nhanh",
      quickStartChat: "Mở Chat và chọn gợi ý prompt có sẵn",
      quickStartSettings: "Tùy chỉnh model Gemini và prompt trong Cài đặt",
      quickStartDev: "Các module Fanpage, Branding, Kế hoạch đang được phát triển",
      stats: "Thống kê sử dụng",
      statsSoon: "Sắp ra mắt",
      contentCreated: "Nội dung đã tạo",
      templatesUsed: "Templates đã dùng",
      timeSaved: "Thời gian tiết kiệm",
      dash: "—",
      featuresList: {
        chat: {
          title: "Chat AI",
          description: "Trò chuyện, tạo content marketing và caption với Gemini",
        },
        settings: {
          title: "Cài đặt",
          description: "Cấu hình AI, chatbot, thương hiệu và kết nối API",
        },
        fanpage: {
          title: "Tạo nội dung Fanpage",
          description: "Bài viết, caption và hashtag cho Facebook",
        },
        plan: {
          title: "Kế hoạch nội dung",
          description: "Lập lịch và chiến lược đăng bài",
        },
        branding: {
          title: "Branding",
          description: "Quản lý tone of voice và phong cách thương hiệu",
        },
        prompt: {
          title: "Custom Prompt",
          description: "Soạn và quản lý prompt templates",
        },
      },
    },
    chat: {
      badge: "AI Content Assistant · KAT Leather",
      emptyHeadline: "Chúng ta bắt đầu từ đâu?",
      newChat: "Chat mới",
      greeting: "Xin chào, {name}",
      subtitle:
        "Tạo content marketing, caption fanpage và tư vấn sản phẩm túi da.",
      inputPlaceholder: "Hỏi bất cứ điều gì",
      add: "Thêm",
      uploading: "Đang tải...",
      addFiles: "Thêm ảnh & tài liệu",
      addEmoji: "Chèn biểu tượng cảm xúc",
      removeImage: "Xóa ảnh",
      disclaimer: "AI có thể mắc lỗi. Hãy kiểm tra thông tin quan trọng.",
      showSystem: "Hiển thị hướng dẫn hệ thống",
      hideSystem: "Ẩn hướng dẫn hệ thống",
      systemPlaceholder: "Nhập hướng dẫn hệ thống dành cho User...",
      processing: "Đang tải và xử lý tài liệu...",
      prompts: {
        marketing: {
          title: "Marketing",
          prompt:
            "Tôi muốn viết một bài marketing cho thương hiệu KAT Leather. Hãy hỏi tôi mục tiêu, đối tượng và tone giọng trước khi viết bài.",
        },
        product: {
          title: "Giới thiệu SP",
          prompt:
            "Giúp tôi viết nội dung giới thiệu một sản phẩm túi da KAT Leather. Hãy hỏi tên sản phẩm, màu sắc và điểm bán hàng chính.",
        },
        caption: {
          title: "Caption Fanpage",
          prompt:
            "Tôi cần caption cho bài đăng fanpage KAT Leather. Hãy hỏi loại bài, sản phẩm và độ dài mong muốn trước khi viết.",
        },
        hashtag: {
          title: "Hashtag & CTA",
          prompt:
            "Gợi ý hashtag và câu kêu gọi hành động (CTA) phù hợp cho bài viết thời trang túi da cao cấp KAT Leather.",
        },
        customer: {
          title: "Trả lời khách",
          prompt:
            "Khách hàng hỏi về chất liệu da và bảo quản túi KAT Leather. Hãy soạn câu trả lời thân thiện, chuyên nghiệp.",
        },
        trend: {
          title: "Xu hướng",
          prompt:
            "Gợi ý 5 ý tưởng nội dung marketing cho KAT Leather trong tuần này, kèm hook hấp dẫn cho từng ý tưởng.",
        },
        story: {
          title: "Storytelling",
          prompt:
            "Viết một bài storytelling ngắn về tinh thần thủ công và chất lượng da thật của thương hiệu KAT Leather since 2009.",
        },
        consult: {
          title: "Tư vấn content",
          prompt:
            "Tôi cần tư vấn chiến lược content marketing cho thương hiệu túi da cao cấp. Hãy bắt đầu bằng cách hỏi mục tiêu kinh doanh của tôi.",
        },
      },
      imageDefaultOne: "Phân tích ảnh và cảm nhận hình ảnh này",
      imageDefaultTwo: "Phân tích ảnh và cảm nhận hai hình ảnh này",
      historyTitle: "Lịch sử chat",
      historyLoading: "Đang tải...",
      historyEmpty: "Chưa có cuộc trò chuyện",
      historyDelete: "Xóa",
      historyDeleteTitle: "Xóa cuộc trò chuyện?",
      historyDeleteDesc: "Hành động này không thể hoàn tác.",
      openChatLink: "Mở chat",
    },
    settings: {
      hub: "Trung tâm cấu hình",
      title: "Cài đặt",
      subtitle:
        "Tùy chỉnh AI, chatbot, thương hiệu và kết nối API cho KAT Content Studio.",
      synced: "Đã đồng bộ",
      unsaved: "Chưa lưu thay đổi",
      geminiApi: "Gemini API",
      categories: "Danh mục",
      pickCategory: "Chọn mục cần cấu hình",
      saveHintSaved: "Mọi thay đổi đã được lưu.",
      saveHintDirty: "Bạn có thay đổi chưa lưu.",
      reset: "Khôi phục mặc định",
      save: "Lưu cài đặt",
      language: "Ngôn ngữ giao diện",
      languageDesc: "Ngôn ngữ hiển thị trên toàn bộ ứng dụng",
      english: "English",
      vietnamese: "Tiếng Việt",
    },
    common: {
      popular: "Phổ biến",
      cancel: "Hủy",
    },
  },
} as const;

export type TranslationKey = typeof translations.en;
