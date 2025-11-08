import type { Pdf } from "@shared/schema";

const API_BASE = "/api";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: response.statusText }));
    throw new ApiError(response.status, error.error || response.statusText);
  }

  return response.json();
}

export const api = {
  // PDF operations
  pdfs: {
    list: (): Promise<Pdf[]> => request("/pdfs"),
    
    get: (id: string): Promise<Pdf> => request(`/pdfs/${id}`),
    
    upload: async (file: File): Promise<Pdf> => {
      const formData = new FormData();
      formData.append("pdf", file);
      
      const response = await fetch(`${API_BASE}/pdfs/upload`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: response.statusText }));
        throw new ApiError(response.status, error.error || response.statusText);
      }
      
      return response.json();
    },
    
    delete: (id: string): Promise<{ success: boolean }> => 
      request(`/pdfs/${id}`, { method: "DELETE" }),
    
    download: (id: string): string => `${API_BASE}/pdfs/${id}/download`,
    
    search: (query: string): Promise<Pdf[]> => 
      request(`/pdfs/search?q=${encodeURIComponent(query)}`),
  },
  // RAG chat
  rag: {
    chat: (messages: Array<{ role: string; content: string }>): Promise<{ reply: string; sources: Array<{ pdfId: string; originalName?: string; preview: string }> }> =>
      request("/rag/chat", {
        method: "POST",
        body: JSON.stringify({ messages }),
      }),
  },
};