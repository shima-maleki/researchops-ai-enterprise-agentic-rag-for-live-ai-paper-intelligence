import type {
  ChatResponse,
  IngestResponse,
  PaperCategory,
  PapersResponse,
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
