import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private readonly baseUrl = 'http://127.0.0.1:8001';

  getBaseUrl(): string {
    return this.baseUrl;
  }

  buildUrl(endpoint: string): string {
    return `${this.baseUrl}${endpoint}`;
  }
}