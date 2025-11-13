# Agent Province Merger Stream API

## Endpoint: `/api/v1/agent-province-merger-stream`

### Description
This endpoint provides a streaming response for the Agent Province Merger functionality. It processes queries related to province merging operations and returns real-time streaming responses using Server-Sent Events (SSE). The agent uses AI tools to search and analyze province merger data with conversational context.

### HTTP Method
`POST`

### URL
```
POST https://api.mekongai.com/api/v1/agent-province-merger-stream
```

### Content Type
- **Request**: `application/json`
- **Response**: `text/event-stream`

### Request Body

The request body must be a JSON object with the following structure:

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `string ` | Yes | Unique identifier for the user making the request. |
| `query` | `string ` | Yes | The query or question related to province merging/address lookup. |
| `session_id` | `string ` | No | Session identifier for maintaining conversation context. Auto-generated if empty. Default: `uuid auto generated` |

#### Request Example

```json
{
  "user_id": "user123",
  "query": "Tìm thông tin sáp nhập xã Hồng Phong thuộc huyện Việt Yên",
  "session_id": "session456"
}
```

### Response

#### Success Response (HTTP 200)
- **Content-Type**: `text/event-stream`
- **Body**: Server-Sent Events (SSE) stream containing real-time data chunks

The response streams content as the AI agent processes the query. Each chunk contains partial text from the agent's response as it's generated.

**Stream Format:**
```
data: X

data: in

data:  ch

data: ào

data: !

data: ...
```

#### Error Response (HTTP 400)
- **Content-Type**: `application/json`

```json
{
  "status": 400,
  "message": "Error: [error description]"
}
```

#### Default Responses

The agent may return these default responses in specific scenarios:

1. **When query is unclear:**
   ```
   Xin lỗi, mình chưa hiểu rõ ý bạn về địa chỉ cần tra cứu. Bạn có thể cung cấp tên địa danh cụ thể hơn được không?
   ```

2. **When system error occurs:**
   ```
   Xin lỗi quý khách, hệ thống tra cứu địa chỉ đang gặp sự cố kỹ thuật nhỏ. Bên mình sẽ sớm khắc phục. Mong bạn thông cảm và thử lại sau ít phút!
   ```

3. **When parsing errors occur:**
   ```
   Xin lỗi, Hệ thống đang gặp chút sự cố nhỏ trong việc xử lý yêu cầu tra cứu địa chỉ của bạn. Bạn vui lòng thử lại hoặc diễn đạt khác đi một chút nhé!
   ```

### Features

- **AI Agent Processing**: Uses OpenAI-based agent with specialized tools for province merger data
- **Conversation History**: Maintains context across multiple requests using session_id
- **Real-time Streaming**: Returns response chunks as they're generated
- **Tool Integration**: Integrates with province merger search tools
- **Error Handling**: Graceful error handling with user-friendly messages
- **Async Processing**: Non-blocking execution with thread pool

### Example Usage

#### cURL
```bash
curl -X POST "https://api.mekongai.com/api/v1/agent-province-merger-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "query": "Xã Tân Hòa thuộc huyện nào sau khi sáp nhập?",
    "session_id": "session456"
  }'
```

#### JavaScript (Server-Sent Events)
```javascript
const eventSource = new EventSource('https://api.mekongai.com/api/v1/agent-province-merger-stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user123',
    query: 'Xã Tân Hòa thuộc huyện nào sau khi sáp nhập?',
    session_id: 'session456'
  })
});

eventSource.onmessage = function(event) {
  console.log('Received:', event.data);
};

eventSource.onerror = function(event) {
  console.error('SSE error:', event);
};
```

#### JavaScript (Fetch API)
```javascript
const response = await fetch('https://api.mekongai.com/api/v1/agent-province-merger-stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user123',
    query: 'Xã Tân Hòa thuộc huyện nào sau khi sáp nhập?',
    session_id: 'session456'
  })
});

if (!response.ok) {
  throw new Error(`HTTP error! status: ${response.status}`);
}

const reader = response.body.getReader();
const decoder = new TextDecoder();

try {
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value, { stream: true });
    console.log('Received chunk:', chunk);
    
    // Process each chunk - it contains the actual text content
    // not in SSE format, just raw text chunks
    if (chunk.trim()) {
      // Update your UI with the chunk
      document.getElementById('response').innerText += chunk;
    }
  }
} catch (error) {
  console.error('Error reading stream:', error);
} finally {
  reader.releaseLock();
}
```

#### JavaScript (with async generator)
```javascript
async function* streamResponse(url, data) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      if (chunk.trim()) {
        yield chunk;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// Usage
const data = {
  user_id: 'user123',
  query: 'Xã Tân Hòa thuộc huyện nào sau khi sáp nhập?',
  session_id: 'session456'
};

for await (const chunk of streamResponse('https://api.mekongai.com/api/v1/agent-province-merger-stream', data)) {
  console.log('Received:', chunk);
  // Update your UI with each chunk
  document.getElementById('response').innerText += chunk;
}
```

#### JavaScript (React/Next.js example)
```javascript
import { useState } from 'react';

function ProvinceChat() {
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (query) => {
    setIsLoading(true);
    setResponse('');
    
    try {
      const res = await fetch('https://api.mekongai.com/api/v1/agent-province-merger-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'user123',
          query: query,
          session_id: 'session456'
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        if (chunk.trim()) {
          setResponse(prev => prev + chunk);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setResponse('Có lỗi xảy ra khi gọi API');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div>{response}</div>
      {isLoading && <div>Đang xử lý...</div>}
    </div>
  );
}
```

#### Python (requests with streaming)
```python
import requests
import json

url = "https://api.mekongai.com/api/v1/agent-province-merger-stream"
data = {
    "user_id": "user123",
    "query": "Xã Tân Hòa thuộc huyện nào sau khi sáp nhập?",
    "session_id": "session456"
}

try:
    response = requests.post(url, json=data, stream=True, timeout=30)
    response.raise_for_status()
    
    for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
        if chunk:
            print(chunk, end='', flush=True)
            
except requests.RequestException as e:
    print(f"Error: {e}")
```

#### Python (with httpx async - similar to webui)
```python
import httpx
import asyncio

async def stream_province_merger():
    url = "https://api.mekongai.com/api/v1/agent-province-merger-stream"
    payload = {
        "user_id": "user123",
        "query": "Xã Tân Hòa thuộc huyện nào sau khi sáp nhập?",
        "session_id": "session456"
    }
    
    timeout = 30.0
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    print(f"Error: {response.text}")
                    return
                
                async for chunk in response.aiter_text():
                    if chunk:
                        print(chunk, end='', flush=True)
                        
    except Exception as e:
        print(f"Error: {str(e)}")

# Run the async function
asyncio.run(stream_province_merger())
```

### Response Format Details

The streaming response follows the Server-Sent Events format:
```
data: [content chunk]

data: [content chunk]

data: [content chunk]
```

Each data chunk contains partial text from the AI agent's response as it's being generated, providing real-time feedback to
the user.

---
---
---

## History API

### Endpoint: `/api/v1/history`

#### Description
This endpoint retrieves chat history for a specific user, with optional filtering by session ID or history ID.

#### HTTP Method
`POST`

#### URL
```
POST https://api.mekongai.com/api/v1/history
```

#### Content Type
- **Request**: `application/json`
- **Response**: `application/json`

#### Request Body

The request body must be a JSON object with the following structure:

##### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `string` | Yes | Unique identifier for the user whose history to retrieve. |
| `session_id` | `string` | No | Session identifier to filter history for a specific session. |
| `history_id` | `string` | No | History identifier to filter for a specific history entry. |

##### Request Examples

**Get all history for a user:**
```json
{
  "user_id": "user123"
}
```

**Get history for a specific session:**
```json
{
  "user_id": "user123",
  "session_id": "session456"
}
```

**Get a specific history entry:**
```json
{
  "user_id": "user123",
  "history_id": "history789"
}
```

#### Response

##### Success Response (HTTP 200)
- **Content-Type**: `application/json`

```json
{
  "status": 200,
  "message": "success",
  "data": [
    {
      "history_id": "history789",
      "query": "Tìm thông tin sáp nhập xã Hồng Phong thuộc huyện Việt Yên",
      "answer": "Xã Hồng Phong, huyện Việt Yên, tỉnh Bắc Giang đã được sáp nhập...",
      "feedback": "",
      "feedback_status": "",
      "reference": [...],
      "chart": null
    }
  ]
}
```

##### Error Response (HTTP 400)
- **Content-Type**: `application/json`

```json
{
  "status": 400,
  "message": "Error: [error description]"
}
```

#### Example Usage

##### cURL
```bash
curl -X POST "https://api.mekongai.com/api/v1/history" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session456"
  }'
```

##### JavaScript
```javascript
const response = await fetch('https://api.mekongai.com/api/v1/history', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user123',
    session_id: 'session456'
  })
});

const data = await response.json();
console.log('History:', data);
```

##### Python
```python
import requests

url = "https://api.mekongai.com/api/v1/history"
data = {
    "user_id": "user123",
    "session_id": "session456"
}

response = requests.post(url, json=data)
history_data = response.json()
```