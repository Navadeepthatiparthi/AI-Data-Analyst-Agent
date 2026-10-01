import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ApiService } from './api';

export interface AskRequest {
  question: string;
}

export interface AskResponse {
  success: boolean;
  dataset_id: string;
  question: string;
  sql: string;
  row_count: number;
  results: Record<string, unknown>[];
}

@Injectable({
  providedIn: 'root'
})
export class QueryService {

  constructor(
    private http: HttpClient,
    private api: ApiService
  ) {}

  askQuestion(
    datasetId: string,
    question: string
  ): Observable<AskResponse> {

    const url = this.api.buildUrl(
      `/api/datasets/${datasetId}/ask`
    );

    const request: AskRequest = {
      question: question.trim()
    };

    return this.http.post<AskResponse>(
      url,
      request
    );
  }
}