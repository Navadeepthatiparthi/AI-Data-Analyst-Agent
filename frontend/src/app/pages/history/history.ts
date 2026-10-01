import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';
import { RouterLink } from '@angular/router';

import { DatasetService } from '../../services/dataset';
import { QueryHistoryService } from '../../services/query-history.service';

import { Dataset } from '../../models/dataset.model';
import {
  QueryHistory
} from '../../models/query-history.model';


@Component({
  selector: 'app-history',

  standalone: true,

  imports: [
    CommonModule,
    RouterLink
  ],

  templateUrl: './history.html',

  styleUrl: './history.css'
})
export class HistoryComponent implements OnInit {

  // -------------------------------------------------
  // DATASET
  // -------------------------------------------------

  datasets: Dataset[] = [];

  selectedDatasetId: string | null = null;

  selectedDataset: Dataset | null = null;


  // -------------------------------------------------
  // HISTORY
  // -------------------------------------------------

  history: QueryHistory[] = [];

  expandedHistoryId: number | null = null;


  // -------------------------------------------------
  // STATE
  // -------------------------------------------------

  loadingDatasets = true;

  loadingHistory = false;

  errorMessage = '';


  constructor(
    private datasetService: DatasetService,
    private queryHistoryService: QueryHistoryService,
    private cdr: ChangeDetectorRef
  ) {}


  // -------------------------------------------------
  // INITIAL LOAD
  // -------------------------------------------------

  ngOnInit(): void {
    this.loadDatasets();
  }


  // -------------------------------------------------
  // LOAD DATASETS
  // -------------------------------------------------

  private loadDatasets(): void {

    this.loadingDatasets = true;

    this.errorMessage = '';

    this.cdr.markForCheck();


    this.datasetService.getDatasets().subscribe({

      next: response => {

        this.datasets = response.datasets || [];

        this.loadingDatasets = false;


        if (this.datasets.length === 0) {

          this.selectedDatasetId = null;

          this.selectedDataset = null;

          this.history = [];

          this.errorMessage =
            'No datasets are available. Upload a dataset first.';

          this.cdr.markForCheck();

          return;
        }


        const firstDataset = this.datasets[0];

        this.selectedDatasetId =
          firstDataset.dataset_id;

        this.selectedDataset =
          firstDataset;


        this.loadHistory(
          firstDataset.dataset_id
        );

      },


      error: error => {

        console.error(
          'History dataset loading error:',
          error
        );

        this.loadingDatasets = false;

        this.errorMessage =
          'Unable to load your datasets.';

        this.cdr.markForCheck();

      }

    });

  }


  // -------------------------------------------------
  // DATASET CHANGE
  // -------------------------------------------------

  selectDataset(datasetId: string): void {

    if (!datasetId) {
      return;
    }


    const dataset = this.datasets.find(
      item => item.dataset_id === datasetId
    );


    if (!dataset) {
      return;
    }


    this.selectedDatasetId = datasetId;

    this.selectedDataset = dataset;

    this.expandedHistoryId = null;

    this.errorMessage = '';


    this.loadHistory(datasetId);

  }


  // -------------------------------------------------
  // LOAD HISTORY
  // -------------------------------------------------

  private loadHistory(datasetId: string): void {

    this.loadingHistory = true;

    this.errorMessage = '';

    this.history = [];

    this.expandedHistoryId = null;

    this.cdr.markForCheck();


    this.queryHistoryService
      .getHistory(datasetId, 100)
      .subscribe({

        next: response => {

          this.history =
            response.history || [];

          this.loadingHistory = false;

          this.cdr.markForCheck();

        },


        error: error => {

          console.error(
            'Query history loading error:',
            error
          );

          this.loadingHistory = false;

          this.errorMessage =
            error?.error?.detail ||
            'Unable to load query history.';

          this.cdr.markForCheck();

        }

      });

  }


  // -------------------------------------------------
  // EXPAND / COLLAPSE
  // -------------------------------------------------

  toggleHistory(
  historyId: number
): void {

    if (this.expandedHistoryId === historyId) {

      this.expandedHistoryId = null;

    } else {

      this.expandedHistoryId = historyId;

    }

    this.cdr.markForCheck();

  }


  // -------------------------------------------------
  // CHECK EXPANDED
  // -------------------------------------------------

 isExpanded(
  historyId: number
): boolean {

    return this.expandedHistoryId === historyId;

  }


  // -------------------------------------------------
  // FORMAT RESULT
  // -------------------------------------------------

  formatResult(
    value: unknown
  ): string {

    if (
      value === null ||
      value === undefined
    ) {
      return '—';
    }


    if (typeof value === 'object') {

      return JSON.stringify(
        value,
        null,
        2
      );

    }


    return String(value);

  }


  // -------------------------------------------------
  // FORMAT DATE
  // -------------------------------------------------

  formatDate(
    value?: string
  ): string {

    if (!value) {
      return 'Unknown date';
    }


    const date = new Date(value);


    if (Number.isNaN(date.getTime())) {
      return value;
    }


    return date.toLocaleString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }
    );

  }


  // -------------------------------------------------
  // TRACK BY
  // -------------------------------------------------
trackByHistoryId(
  index: number,
  item: QueryHistory
): number {

    return item.id;

  }

}