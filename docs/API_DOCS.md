# Chatbot API Documentation

Base URL: `http://localhost:8000` (or your deployed server URL)

## Endpoint: Chat with AI
**URL:** `/api/chat`
**Method:** `POST`
**Content-Type:** `application/json`

### Description
This endpoint sends a user query to the context-aware AI chatbot. The AI has access to real-time database tools and a knowledge base (RAG) to answer questions about DC crime, real estate, and the HCI methodology.

### Request Body
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | Yes | The user's question. |
| `history` | `array` | No | List of previous messages for context. |
| `client_context` | `object` | No | **[New]** Frontend state to make the AI context-aware. |

#### `client_context` Object
| Field | Type | Description |
| :--- | :--- | :--- |
| `current_zip` | `string` | The ZIP code currently selected or viewed by the user (e.g., "20002"). |
| `weights` | `object` | The current values of the user's preference sliders. |

#### `weights` Object
| Field | Type | Description |
| :--- | :--- | :--- |
| `growth_w1` | `float` | Weight for Investment Potential (0.0 - 1.0). |
| `safety_w2` | `float` | Weight for Safety (0.0 - 1.0). |

---

### Example Request
```json
{
  "query": "Is this area good for a long-term investment?",
  "history": [
    {"role": "user", "content": "Hi"},
    {"role": "model", "content": "Hello! How can I help you with DC real estate?"}
  ],
  "client_context": {
    "current_zip": "20002",
    "weights": {
      "growth_w1": 0.8,
      "safety_w2": 0.2
    }
  }
}
```

### Example Response
```json
{
  "response": "Based on your high preference for growth (w1=0.8), ZIP 20002 is an excellent choice. The HCI score is 0.75, driven by a strong 5% YoY appreciation. Although the crime rate is moderate, your lower safety weight (0.2) makes this less of a penalty for your specific index.",
  "data_sources": []
}
```

### Integration Notes for Frontend Developers
1.  **State Management**: Always send the `client_context` if the user has selected a ZIP code or adjusted sliders. This allows the AI to give personalized advice without the user repeating themselves.
2.  **History**: Keep a local array of the last 5-10 messages and send them in the `history` field to maintain conversation continuity.
3.  **Markdown**: The `response` field contains Markdown (headers, lists, bold text). Ensure your frontend renders it properly (e.g., using `react-markdown`).
