export interface QueryHistory {
  id: number;
  dataset_id: string;
  question: string;
  sql: string;
  row_count: number;
  created_at: string;
  results: Record<string, unknown>[];
}

export interface QueryHistoryResponse {
  success: boolean;
  dataset_id: string;
  count: number;
  history: QueryHistory[];
}