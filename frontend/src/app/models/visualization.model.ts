export interface VisualizationData {
  category?: string;
  date?: string;
  value: number;
}

export interface Visualization {
  chart_id: string;
  type: 'bar' | 'line';
  title: string;
  x_axis: string;
  y_axis: string;
  data: VisualizationData[];
}

export interface VisualizationsResponse {
  success: boolean;
  dataset_id: string;
  dataset: string;
  chart_count: number;
  charts: Visualization[];
}