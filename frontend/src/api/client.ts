import type {
  ChatResponse,
  ChatStreamEvent,
  IngestResponse,
  PaperCategory,
  PapersResponse,
  Source,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail ?? `Request failed with ${response.status}`;
    throw new Error(detail);
  }
  return data as T;
}

export function sendChatMessage(message: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export async function streamChatMessage(
  message: string,
  handlers: {
    onDelta: (content: string) => void;
    onSources: (sources: Source[]) => void;
  },
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    const detail = data?.detail ?? `Request failed with ${response.status}`;
    throw new Error(detail);
  }

  if (!response.body) {
    throw new Error("Streaming is not supported by this browser");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      const event = JSON.parse(trimmed) as ChatStreamEvent;

      if (event.type === "delta") {
        handlers.onDelta(event.content);
      }
      if (event.type === "sources") {
        handlers.onSources(event.sources);
      }
      if (event.type === "error") {
        throw new Error(event.detail);
      }
    }
  }
}

export function ingestPapers(params: {
  limit: number;
  categories: PaperCategory[];
}): Promise<IngestResponse> {
  return request<IngestResponse>("/ingest", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function searchPapers(params: {
  keyword?: string;
  category?: PaperCategory | "";
  limit?: number;
}): Promise<PapersResponse> {
  const query = new URLSearchParams();
  if (params.keyword?.trim()) query.set("keyword", params.keyword.trim());
  if (params.category) query.set("category", params.category);
  if (params.limit) query.set("limit", String(params.limit));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return request<PapersResponse>(`/papers${suffix}`);
}
