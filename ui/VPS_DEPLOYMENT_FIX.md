# Hướng Dẫn Fix Lỗi Deployment Trên VPS

## Phân Tích Lỗi

### 1. Lỗi ERR_CONNECTION_REFUSED
- **Nguyên nhân**: API endpoint vẫn đang gọi `localhost:8001` thay vì IP VPS
- **Triệu chứng**: `GET http://localhost:8001/api/v1/content/history/?user_id=default_user&limit=5 net::ERR_CONNECTION_REFUSED`

### 2. Lỗi 307 Redirect
- **Nguyên nhân**: Trailing slash trong API endpoint gây redirect
- **Triệu chứng**: `Response: 307 - 0.001s` trong backend logs

### 3. Lỗi WebSocket HMR
- **Nguyên nhân**: Development mode WebSocket không hoạt động trên production
- **Triệu chứng**: `WebSocket connection to 'ws://144.91.113.233:3000/_next/webpack-hmr' failed`

## Các Fix Đã Thực Hiện

### 1. Fix API Endpoints (✅ Hoàn thành)
```typescript
// Trước (có trailing slash - gây 307 redirect)
const response = await apiClient.get(`/api/v1/content/history/?user_id=${userId}&limit=${limit}`);

// Sau (không có trailing slash)
const response = await apiClient.get(`/api/v1/content/history?user_id=${userId}&limit=${limit}`);
```

### 2. Fix Environment Variables (✅ Hoàn thành)
- Cập nhật `.env.local` với port đúng (8001 thay vì 8000)
- Tạo `.env.production` với cấu hình production
- Tạo `.env.example` làm template

### 3. Fix WebSocket HMR (✅ Hoàn thành)
- Disable WebSocket HMR trong production
- Cấu hình webpack để tắt HMR khi NODE_ENV=production

## Hướng Dẫn Deploy Trên VPS

### Bước 1: Cấu Hình Environment Variables
Tạo file `.env.production` trên VPS:
```bash
# Production environment variables
NODE_ENV=production

# API Configuration - THAY ĐỔI IP_VPS_CỦA_BẠN
NEXT_PUBLIC_API_URL=http://144.91.113.233:8001
NEXT_PUBLIC_SERVER_HOST=144.91.113.233
NEXT_PUBLIC_API_PORT=8001

# Disable development features
NEXT_TELEMETRY_DISABLED=1
FAST_REFRESH=false
```

### Bước 2: Build và Deploy
```bash
# 1. Copy code lên VPS
scp -r ./ui user@144.91.113.233:/path/to/project/

# 2. SSH vào VPS
ssh user@144.91.113.233

# 3. Navigate to project directory
cd /path/to/project/ui

# 4. Install dependencies
npm install

# 5. Build production
npm run build

# 6. Start production server
npm start
```

### Bước 3: Kiểm Tra Backend
Đảm bảo backend đang chạy trên VPS:
```bash
# Kiểm tra backend có đang chạy không
curl http://144.91.113.233:8001/health

# Kiểm tra API history
curl "http://144.91.113.233:8001/api/v1/content/history?user_id=default_user&limit=5"
```

### Bước 4: Kiểm Tra Firewall
```bash
# Mở port 3000 và 8001
sudo ufw allow 3000
sudo ufw allow 8001
sudo ufw reload
```

## Troubleshooting

### Nếu vẫn gặp lỗi ERR_CONNECTION_REFUSED:
1. Kiểm tra backend có đang chạy: `ps aux | grep uvicorn`
2. Kiểm tra port có mở: `netstat -tlnp | grep :8001`
3. Kiểm tra firewall: `sudo ufw status`

### Nếu vẫn gặp lỗi 307 Redirect:
1. Kiểm tra backend routes có trailing slash không
2. Xem logs backend để debug: `tail -f /path/to/backend/logs`

### Nếu vẫn có lỗi WebSocket:
1. Kiểm tra NODE_ENV=production
2. Clear browser cache
3. Hard refresh (Ctrl+Shift+R)

## Kết Quả Mong Đợi

Sau khi fix:
- ✅ Content history load thành công
- ✅ Không còn lỗi ERR_CONNECTION_REFUSED  
- ✅ Không còn 307 redirect
- ✅ Không còn WebSocket errors
- ✅ API calls đến đúng IP VPS

## Lưu Ý Quan Trọng

1. **Thay đổi IP**: Nhớ thay `144.91.113.233` bằng IP thực của VPS
2. **Port Backend**: Đảm bảo backend chạy trên port 8001
3. **CORS**: Backend cần allow origin từ frontend domain
4. **SSL**: Nên setup SSL certificate cho production

## SSE Streaming (Chat) trên VPS

Để trả lời từng ký tự (character-by-character) khi deploy lên VPS, cần vô hiệu hóa buffer/caching ở proxy (Nginx/CDN) và đảm bảo backend gửi đúng headers SSE.

- Backend đã được cập nhật để trả về các headers SSE: `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no`.
- Cấu hình Nginx khuyến nghị (áp dụng cho các route stream):

```nginx
# File mẫu: resources/docs/nginx-sse.conf
location ~* ^/api/v1/(chatbot-custom-prompt-stream|chatbot-chart-stream|chatbot-basic-stream|chatbot-reference-stream|agent-kat-stream|agent-province-merger-stream)$ {
    proxy_pass http://127.0.0.1:1979;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_request_buffering off;
    proxy_cache off;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    send_timeout 600s;
    proxy_set_header X-Accel-Buffering no;
    add_header Cache-Control "no-cache";
    add_header X-Accel-Buffering "no";
    gzip off;
}
```

Kiểm tra nhanh bằng `curl` (nên thấy dữ liệu đổ về từng dòng):

```bash
curl -N -H "Accept: text/event-stream" -H "Content-Type: application/json" \
    -d '{"user_id":"default_user","query":"Xin chào","collections":[],"session_id":"demo","history_id":"demo","system_instruction_user":"","include_products":true}' \
    http://YOUR_DOMAIN_OR_IP/api/v1/chatbot-custom-prompt-stream
```

Gợi ý cấu hình UI để tránh proxy buffer:

- Đặt `NEXT_PUBLIC_API_URL` trỏ thẳng về API (ví dụ `http://YOUR_DOMAIN_OR_IP:8001`), UI sẽ ưu tiên dùng đường dẫn tuyệt đối cho các call streaming.
- Đảm bảo Node.js trên VPS `>= 18` để `ReadableStream` hoạt động ổn định.