import { CommonModule } from '@angular/common';

import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import {
  ActivatedRoute,
  RouterLink
} from '@angular/router';

import {
  AnalyticsService
} from '../../services/analytics';

import {
  DatasetService
} from '../../services/dataset';

import {
  Dataset
} from '../../models/dataset.model';

import {
  Insight
} from '../../models/insight.model';

import {
  Visualization
} from '../../models/visualization.model';

import {
  Anomaly
} from '../../models/anomaly.model';

import {
  ChartCardComponent
} from '../../components/chart-card/chart-card';


@Component({
  selector: 'app-analytics',

  standalone: true,

  imports: [
    CommonModule,
    RouterLink,
    ChartCardComponent
  ],

  templateUrl: './analytics.html',

  styleUrl: './analytics.css'
})
export class AnalyticsComponent implements OnInit {

  datasetId: string | null = null;

  dataset: Dataset | null = null;

  insights: Insight[] = [];

  charts: Visualization[] = [];

  anomalies: Anomaly[] = [];

  loading = true;

  errorMessage = '';

  totalRevenue = 0;

  totalProfit = 0;

  averageRevenue = 0;

  totalQuantity = 0;


  constructor(
    private route: ActivatedRoute,
    private analyticsService: AnalyticsService,
    private datasetService: DatasetService,
    private cdr: ChangeDetectorRef
  ) {}


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


  private loadFirstDataset(): void {

    this.loading = true;

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

            this.loading = false;

            this.errorMessage =
              'No dataset is available for analysis.';

            this.cdr.markForCheck();

            return;
          }


          const firstDataset =
            response.datasets[0];

          this.datasetId =
            firstDataset.dataset_id;

          this.dataset =
            firstDataset;

          this.cdr.markForCheck();


          this.loadAnalytics(
            firstDataset.dataset_id
          );

        },


        error: error => {

          console.error(
            'Dataset loading error:',
            error
          );

          this.loading = false;

          this.errorMessage =
            'Unable to load your dataset.';

          this.cdr.markForCheck();

        }

      });
  }


  private loadDataset(
    datasetId: string
  ): void {

    this.loading = true;

    this.cdr.markForCheck();


    this.datasetService
      .getDataset(datasetId)
      .subscribe({

        next: response => {

          this.dataset =
            response.dataset;

          this.cdr.markForCheck();


          this.loadAnalytics(
            datasetId
          );

        },


        error: error => {

          console.error(
            'Dataset loading error:',
            error
          );

          this.loading = false;

          this.errorMessage =
            'Unable to load the selected dataset.';

          this.cdr.markForCheck();

        }

      });
  }


  private loadAnalytics(
    datasetId: string
  ): void {

    this.loading = true;

    this.errorMessage = '';

    this.insights = [];

    this.charts = [];

    this.anomalies = [];

    this.resetKpis();

    this.cdr.markForCheck();


    this.analyticsService
      .getInsights(datasetId)
      .subscribe({

        next: response => {

          if (response.success) {

            this.insights =
              response.insights || [];

            this.calculateKpis();

          }

          this.cdr.markForCheck();

        },


        error: error => {

          console.error(
            'Insights error:',
            error
          );

          this.errorMessage =
            'Unable to load analytical insights.';

          this.cdr.markForCheck();

        }

      });


    this.analyticsService
      .getVisualizations(datasetId)
      .subscribe({

        next: response => {

          if (response.success) {

            this.charts =
              response.charts || [];

          }

          this.cdr.markForCheck();

        },


        error: error => {

          console.error(
            'Visualizations error:',
            error
          );

          this.errorMessage =
            'Unable to load visualizations.';

          this.cdr.markForCheck();

        }

      });


    this.analyticsService
      .getAnomalies(datasetId)
      .subscribe({

        next: response => {

          if (response.success) {

            this.anomalies =
              response.anomalies || [];

          }

          this.loading = false;

          this.cdr.markForCheck();

        },


        error: error => {

          console.error(
            'Anomaly error:',
            error
          );

          this.loading = false;

          this.cdr.markForCheck();

        }

      });

  }


  private resetKpis(): void {

    this.totalRevenue = 0;

    this.totalProfit = 0;

    this.averageRevenue = 0;

    this.totalQuantity = 0;

  }


  private calculateKpis(): void {

    const revenue =
      this.insights.find(
        insight =>
          insight.column.toLowerCase() === 'revenue'
      );


    const profit =
      this.insights.find(
        insight =>
          insight.column.toLowerCase() === 'profit'
      );


    const quantity =
      this.insights.find(
        insight =>
          insight.column.toLowerCase() === 'quantity'
      );


    if (revenue) {

      this.totalRevenue =
        revenue.total;

      this.averageRevenue =
        revenue.average;

    }


    if (profit) {

      this.totalProfit =
        profit.total;

    }


    if (quantity) {

      this.totalQuantity =
        quantity.total;

    }

  }


  getChart(
    chartId: string
  ): Visualization | undefined {

    return this.charts.find(
      chart =>
        chart.chart_id === chartId
    );

  }


  formatCurrency(
    value: number
  ): string {

    return new Intl.NumberFormat(
      'en-IN',
      {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
      }
    ).format(value);

  }


  formatNumber(
    value: number
  ): string {

    return new Intl.NumberFormat(
      'en-IN',
      {
        maximumFractionDigits: 0
      }
    ).format(value);

  }

}