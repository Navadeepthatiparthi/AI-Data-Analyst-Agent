import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import {
  ActivatedRoute,
  RouterLink,

} from '@angular/router';

import {
  DatasetService
} from '../../services/dataset';

import {
  QueryService,
  AskResponse
} from '../../services/query';

import {
  Dataset
} from '../../models/dataset.model';


@Component({
  selector: 'app-ai-analyst',

  standalone: true,

  imports: [
    CommonModule,
    RouterLink,
    FormsModule
  ],

  templateUrl: './ai-analyst.html',

  styleUrl: './ai-analyst.css'
})
export class AiAnalystComponent implements OnInit {

 
  // DATASET
  

  datasetId: string | null = null;

  dataset: Dataset | null = null;

  loadingDataset = true;


  
  // QUESTION
  question = '';

  asking = false;

  // RESPONSE

  response: AskResponse | null = null;

  errorMessage = '';


  constructor(
    private route: ActivatedRoute,
    private datasetService: DatasetService,
    private queryService: QueryService,
    private cdr: ChangeDetectorRef
  ) {}

  // INITIALIZE

  ngOnInit(): void {

    this.route.paramMap.subscribe(params => {

      const routeDatasetId =
        params.get('datasetId');

      if (routeDatasetId) {

        this.datasetId =
          routeDatasetId;

        this.loadDataset(
          routeDatasetId
        );

        return;
      }

      this.loadFirstDataset();

    });

  }


  
  // LOAD SELECTED DATASET
  private loadDataset(
    datasetId: string
  ): void {

    this.loadingDataset = true;

    this.errorMessage = '';

    this.cdr.markForCheck();


    this.datasetService
      .getDataset(datasetId)
      .subscribe({

        next: response => {

          this.dataset =
            response.dataset;

          this.loadingDataset =
            false;

          this.cdr.markForCheck();

        },


        error: error => {

          console.error(
            'AI Analyst dataset loading error:',
            error
          );

          this.loadingDataset =
            false;

          this.errorMessage =
            'Unable to load the selected dataset.';

          this.cdr.markForCheck();

        }

      });

  }


  // LOAD FIRST DATASET
  private loadFirstDataset(): void {

    this.loadingDataset = true;

    this.errorMessage = '';

    this.cdr.markForCheck();


    this.datasetService
      .getDatasets()
      .subscribe({

        next: response => {

          if (
            !response.datasets ||
            response.datasets.length === 0
          ) {

            this.loadingDataset =
              false;

            this.errorMessage =
              'No dataset is available. Upload a dataset first.';

            this.cdr.markForCheck();

            return;
          }


          const firstDataset =
            response.datasets[0];


          this.dataset =
            firstDataset;


          this.datasetId =
            firstDataset.dataset_id;


          this.loadingDataset =
            false;


          this.cdr.markForCheck();

        },


        error: error => {

          console.error(
            'Dataset loading error:',
            error
          );

          this.loadingDataset =
            false;

          this.errorMessage =
            'Unable to load your datasets.';

          this.cdr.markForCheck();

        }

      });

  }


  
  // ASK AI

  askQuestion(): void {

    const trimmedQuestion =
      this.question.trim();


    if (!trimmedQuestion) {

      this.errorMessage =
        'Please enter a question about your data.';

      this.cdr.markForCheck();

      return;

    }


    if (!this.datasetId) {

      this.errorMessage =
        'No dataset is selected.';

      this.cdr.markForCheck();

      return;

    }


    if (this.asking) {
      return;
    }


    this.asking = true;

    this.errorMessage = '';

    this.response = null;

    this.cdr.markForCheck();


    this.queryService
      .askQuestion(
        this.datasetId,
        trimmedQuestion
      )
      .subscribe({

        next: response => {

          console.log(
            'AI Analyst response:',
            response
          );


          this.response =
            response;


          this.asking =
            false;


          this.cdr.markForCheck();

        },


        error: error => {

          console.error(
            'AI Analyst error:',
            error
          );


          this.asking =
            false;


          this.errorMessage =
            error?.error?.detail ||
            'Unable to analyze your question. Please try again.';


          this.cdr.markForCheck();

        }

      });

  }


  
  // EXAMPLE QUESTIONS

  useExample(
    example: string
  ): void {

    this.question =
      example;

    this.errorMessage = '';

    this.cdr.markForCheck();

  }


  
  // ENTER KEY


  handleKeydown(
    event: KeyboardEvent
  ): void {

    if (
      event.key === 'Enter' &&
      !event.shiftKey
    ) {

      event.preventDefault();

      this.askQuestion();

    }

  }


 
  // RESULT HELPERS
 
  getResultColumns(): string[] {

    if (
      !this.response ||
      !this.response.results ||
      this.response.results.length === 0
    ) {

      return [];

    }


    return Object.keys(
      this.response.results[0]
    );

  }


  getResultValue(
    row: Record<string, unknown>,
    column: string
  ): unknown {

    return row[column];

  }


 
  // FORMAT VALUES
 

  formatValue(
    value: unknown
  ): string {

    if (
      value === null ||
      value === undefined
    ) {

      return '—';

    }


    if (
      typeof value === 'object'
    ) {

      return JSON.stringify(value);

    }


    return String(value);

  }


  
  // CLEAR RESULT
 

  clearResult(): void {

    this.response =
      null;

    this.errorMessage =
      '';

    this.cdr.markForCheck();

  }

}