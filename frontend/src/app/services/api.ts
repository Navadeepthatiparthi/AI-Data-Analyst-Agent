import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private readonly baseUrl =
    'https://ai-data-analyst-agent-8rpi.onrender.com';

  getBaseUrl(): string {
    return this.baseUrl;
  }

  buildUrl(endpoint: string): string {
    return `${this.baseUrl}${endpoint}`;
  }
}