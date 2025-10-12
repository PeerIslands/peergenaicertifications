import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ChatRequest {
  message: string;
  model: string;
  session_id: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  confidence: number;
}

export interface UploadResponse {
  status: string;
  filename: string;
  chunks_created: number;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  uploadDocument(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(`${this.baseUrl}/upload`, formData);
  }

  chat(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.baseUrl}/chat`, request);
  }

  resetSession(sessionId: string = 'default'): Observable<any> {
    return this.http.post(`${this.baseUrl}/reset?session_id=${sessionId}`, {});
  }

  listDocuments(): Observable<any> {
    return this.http.get(`${this.baseUrl}/documents`);
  }

  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }
}
