export interface Dataset {
  dataset_id: string;
  user_id?: string;
  filename: string;
  file_path?: string;
  table_name?: string;
  rows?: number;
  columns?: number;
  uploaded_at?: string;
}