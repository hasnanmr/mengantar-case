# Backend to Frontend API Documentation

This document describes the API endpoints used by the frontend to communicate with the backend.

---

## Base URL

```
http://localhost:8000
```

Or for production:
```
https://api.hasnan.cloud
```

The frontend reads this from `NEXT_PUBLIC_API_URL` environment variable.

---

## 1. Chat API

### POST `/api/chat`

Streaming chat endpoint using **SSE (Server-Sent Events)**. Returns a stream of events for real-time response generation.

**Request:**
```json
{
  "message": "Hello, saya punya masalah jerawat",
  "thread_id": "optional-thread-id-if-continuing"
}
```

**Response:** `text/event-stream` (SSE)

Each line is a data event in the format: `data: {"type": "...", ...}\n\n`

**Event Types:**

| Event Type | Description | Fields |
|------------|-------------|--------|
| `token` | LLM token response | `content`: string |
| `usage` | Token usage info | `input_tokens`, `output_tokens`, `total_tokens` |
| `done` | Stream completed | `thread_id`, `stage` |
| `error` | Error occurred | `content`: error message |

**Event Examples:**

```event-stream
data: {"type": "token", "content": "Halo"}
data: {"type": "token", "content": "! Saya"}
data: {"type": "token", "content": " siap"}
data: {"type": "usage", "input_tokens": 25, "output_tokens": 10, "total_tokens": 35}
data: {"type": "done", "thread_id": "abc-123", "stage": "greeting"}
```

**Frontend Usage:**
```typescript
import { streamChat } from "@/lib/api";

streamChat(
  "Hello",
  null, // thread_id (null for new thread)
  (token) => { console.log(token); }, // onToken - each LLM token
  (usage) => { console.log(usage); }, // onUsage - token count
  (done) => { console.log(done); },   // onDone - stream complete
  (error) => { console.error(error); } // onError - stream error
);
```

**Headers (Response):**
```
Cache-Control: no-cache
Connection: keep-alive
X-Thread-Id: abc-123-def-456
```

---

## 2. Thread API

### GET `/api/threads/`

List all chat threads with their last checkpoint ID.

**Response:**
```json
{
  "threads": [
    {
      "thread_id": "abc-123-def",
      "last_checkpoint": 42
    },
    {
      "thread_id": "xyz-789-ghi",
      "last_checkpoint": 15
    }
  ]
}
```

**Frontend Usage:**
```typescript
import { fetchThreads } from "@/lib/api";

const data = await fetchThreads();
console.log(data.threads); // [{ thread_id, last_checkpoint }, ...]
```

---

### GET `/api/threads/{thread_id}`

Get message history for a specific thread.

**Response:**
```json
{
  "thread_id": "abc-123-def",
  "messages": [
    {
      "id": "1700000000",
      "role": "user",
      "content": "Halo, saya punya masalah jerawat",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "id": "1700000000-ai",
      "role": "assistant",
      "content": "Halo! Saya siap membantu kamu menangani jerawat...",
      "timestamp": "2024-01-15T10:30:05Z",
      "tokenUsage": {
        "input_tokens": 25,
        "output_tokens": 45,
        "total_tokens": 70
      }
    }
  ],
  "stage": "greeting"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `thread_id` | string | Thread identifier |
| `messages` | array | Array of message objects |
| `stage` | string | Current conversation stage |

**Message Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message ID |
| `role` | string | `"user"` or `"assistant"` |
| `content` | string | Message content |
| `timestamp` | string | ISO 8601 timestamp |
| `tokenUsage` | object | Optional, only for assistant messages |

**Frontend Usage:**
```typescript
import { fetchThreadHistory } from "@/lib/api";

const data = await fetchThreadHistory("abc-123-def");
console.log(data.messages); // Array of messages
console.log(data.stage);    // "greeting", "consultation", etc.
```

---

### DELETE `/api/threads/{thread_id}`

Delete a thread and all its checkpoints.

**Response:**
```json
{
  "message": "Thread abc-123 deleted successfully"
}
```

**Error Response (404):**
```json
{
  "detail": "Thread not found"
}
```

**Frontend Usage:**
```typescript
import { deleteThread } from "@/lib/api";

await deleteThread("abc-123-def");
```

---

## Conversation Stages

The `stage` field in responses indicates the current conversation phase:

| Stage | Description |
|-------|-------------|
| `greeting` | Initial greeting, product introduction |
| `needs_assessment` | Understanding user's skin issues |
| `consultation` | Product recommendations, RAG lookup |
| `social_proof` | Testimonials displayed (multimodal) |
| `promotion` | Special offers, bundling deals |
| `closing` | Conversation wrap-up |
| `end` | Conversation completed |

---

## SSE Parsing Example

Frontend receives the stream and parses events:

```typescript
const reader = res.body.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split("\n\n");
  buffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.startsWith("data: ")) continue;
    const event = JSON.parse(line.slice(6)); // Remove "data: " prefix

    switch (event.type) {
      case "token":
        onToken(event.content);
        break;
      case "usage":
        onUsage(event);
        break;
      case "done":
        onDone(event);
        break;
      case "error":
        onError(event.content);
        break;
    }
  }
}
```

---

## Error Handling

All endpoints throw errors with appropriate HTTP status codes:

| Status | Description |
|--------|-------------|
| 200 | Success |
| 400 | Bad request (invalid JSON, missing fields) |
| 404 | Thread not found |
| 500 | Internal server error |

SSE stream errors are sent as events (not HTTP errors):

```event-stream
data: {"type": "error", "content": "Database connection failed"}
```
