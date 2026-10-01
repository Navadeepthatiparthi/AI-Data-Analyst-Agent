export interface Anomaly {
  id?: string;
  column?: string;
  value?: number;
  expected?: number;
  deviation?: number;
  severity?: string;
  message?: string;
  description?: string;
  [key: string]: unknown;
}

export interface AnomaliesResponse {
  success: boolean;
  dataset_id: string;
  dataset?: string;
  anomaly_count?: number;
  anomalies: Anomaly[];
}