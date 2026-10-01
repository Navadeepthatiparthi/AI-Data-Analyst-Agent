export interface Insight {
  column: string;
  total: number;
  average: number;
  minimum: number;
  maximum: number;
}

export interface InsightsResponse {
  success: boolean;
  dataset_id: string;
  dataset: string;
  insights: Insight[];
}