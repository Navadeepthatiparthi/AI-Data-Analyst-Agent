import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ApiService } from './api';
import {
  QueryHistoryResponse
} from '../models/query-history.model';

@Injectable({
  providedIn: 'root'
})
export class QueryHistoryService {

  constructor(
    private http: HttpClient,
    private api: ApiService
  ) {}

  getHistory(
    datasetId: string,
    limit: number = 20
  ): Observable<QueryHistoryResponse> {

    const url = this.api.buildUrl(
      `/api/datasets/${datasetId}/history?limit=${limit}`
    );

    return this.http.get<QueryHistoryResponse>(url);
  }
}