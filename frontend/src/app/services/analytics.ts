import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ApiService } from './api';

import {
  InsightsResponse
} from '../models/insight.model';

import {
  AnomaliesResponse
} from '../models/anomaly.model';

import {
  VisualizationsResponse
} from '../models/visualization.model';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {

  constructor(
    private http: HttpClient,
    private api: ApiService
  ) {}

  getInsights(
    datasetId: string
  ): Observable<InsightsResponse> {

    const url = this.api.buildUrl(
      `/api/datasets/${datasetId}/insights`
    );

    return this.http.get<InsightsResponse>(url);
  }

  getAnomalies(
    datasetId: string
  ): Observable<AnomaliesResponse> {

    const url = this.api.buildUrl(
      `/api/datasets/${datasetId}/anomalies`
    );

    return this.http.get<AnomaliesResponse>(url);
  }

  getVisualizations(
    datasetId: string
  ): Observable<VisualizationsResponse> {

    const url = this.api.buildUrl(
      `/api/datasets/${datasetId}/visualizations`
    );

    return this.http.get<VisualizationsResponse>(url);
  }
}