import { Injectable } from '@angular/core';

import {
  HttpClient
} from '@angular/common/http';

import {
  Observable
} from 'rxjs';

import {
  ApiService
} from './api';

import {
  Dataset
} from '../models/dataset.model';


@Injectable({
  providedIn: 'root'
})
export class DatasetService {

  constructor(
    private http: HttpClient,
    private api: ApiService
  ) {}


  
  // GET ALL DATASETS FOR CURRENT USER
  
  getDatasets(): Observable<{
    success: boolean;
    count: number;
    datasets: Dataset[];
  }> {

    const url =
      this.api.buildUrl(
        '/api/datasets'
      );

    return this.http.get<{
      success: boolean;
      count: number;
      datasets: Dataset[];
    }>(url);
  }


 
  // GET ONE DATASET
  

 getDataset(
  datasetId: string
): Observable<{
  success: boolean;
  dataset: Dataset;
}> {

    const url =
      this.api.buildUrl(
        `/api/datasets/${datasetId}`
      );

    return this.http.get<{
      success: boolean;
      dataset: Dataset;
    }>(url);
  }


  
  // UPLOAD DATASET

  uploadDataset(
    file: File
  ): Observable<{
    success: boolean;
    dataset_id: string;
    filename: string;

    profile: unknown;

    quality: unknown;

    storage: {
      file_path: string;
      table_name: string;
    };

    schema: unknown[];
  }> {

    const formData =
      new FormData();

    formData.append(
      'file',
      file
    );

    const url =
      this.api.buildUrl(
        '/api/datasets/upload'
      );

    return this.http.post<{
      success: boolean;
      dataset_id: string;
      filename: string;

      profile: unknown;

      quality: unknown;

      storage: {
        file_path: string;
        table_name: string;
      };

      schema: unknown[];
    }>(
      url,
      formData
    );
  }

}