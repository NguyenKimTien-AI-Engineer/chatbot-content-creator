# Cấu trúc thư mục

```
mekongai-template/
├── api/                         # REST API endpoints
├── bot/v1/                      # Chứa code để chạy bot
├── configs/                     # Cấu hình hệ thống
│   ├── prompts/                 # System prompts cho AI
│   ├── constant.py              # Hằng số hệ thống
│   └── environment.py           # Biến môi trường (LLM, Embedding,...)
├── controllers/                 # Logic xử lý chính
│   ├── agent/tool/              # AI agents và tools
│   ├── aws/                     # AWS services integration
│   ├── data/                    # Xử lý dữ liệu
│   ├── databases/               # Database operations
│   ├── documents/               # Xử lý tài liệu
│   ├── llm/                     # Large Language Model
│   ├── modules/                 # Modules tiện ích
│   ├── rag/                     # RAG implementation
│   ├── services/                # Business services
│   ├── socials/facebook/        # Social media integration
│   └── utils/                   # Utility functions
├── resources/                   # Tài nguyên hệ thống
│   ├── backups/db/              # Database backups
│   ├── data/                    # Dữ liệu static
│   ├── dev/                     # Development resources
│   ├── docs/                    # Documentation
│   ├── icon/                    # Icons và images
│   ├── logs/                    # Log files
│   ├── tests/                   # Test data
│   └── tmp/                     # Temporary files
├── tests/                       # Unit tests
├── ui/                          # User Interface
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── app.py                       # Main application
├── Dockerfile                   # Docker configuration
├── README.md                    # Project documentation
├── requirements_basic.txt       # Basic dependencies
├── requirements.txt             # Full dependencies
└── webui.py                     # Web UI launcher
```