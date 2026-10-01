import { CommonModule } from '@angular/common';

import {
  Component,
  Input,
  OnChanges,
  SimpleChanges
} from '@angular/core';

import {
  ChartData,
  ChartOptions,
  ChartType,
  Chart,
  CategoryScale,
  LinearScale,
  BarController,
  BarElement,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
  Legend
} from 'chart.js';

import { BaseChartDirective } from 'ng2-charts';

import { Visualization } from '../../models/visualization.model';


Chart.register(
  CategoryScale,
  LinearScale,
  BarController,
  BarElement,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
  Legend
);


@Component({
  selector: 'app-chart-card',

  standalone: true,

  imports: [
    CommonModule,
    BaseChartDirective
  ],

  templateUrl: './chart-card.html',

  styleUrl: './chart-card.css'
})
export class ChartCardComponent implements OnChanges {

  @Input() chart?: Visualization;


  chartType: ChartType = 'bar';


  chartData: ChartData = {
    labels: [],
    datasets: []
  };


  chartOptions: ChartOptions = {

    responsive: true,

    maintainAspectRatio: false,


    animation: {
      duration: 700
    },


    plugins: {

      legend: {
        display: false
      },


      tooltip: {

        backgroundColor: '#2d2926',

        titleColor: '#f6f0e5',

        bodyColor: '#f6f0e5',

        borderColor: '#b59b6d',

        borderWidth: 1,

        padding: 12,

        displayColors: false
      }
    },


    scales: {

      x: {

        grid: {
          display: false
        },


        ticks: {

          color: '#6f665c',

          font: {
            size: 12
          }
        },


        border: {
          color: '#d8cdbb'
        }
      },


      y: {

        beginAtZero: true,


        grid: {
          color: '#ebe4d8'
        },


        ticks: {

          color: '#6f665c',

          font: {
            size: 12
          }
        },


        border: {
          display: false
        }
      }
    }
  };


  ngOnChanges(changes: SimpleChanges): void {

    if (
      changes['chart'] &&
      this.chart
    ) {

      this.prepareChart();

    }

  }


  private prepareChart(): void {

    if (!this.chart) {
      return;
    }


    /*
     * Tell Chart.js whether this is
     * a bar chart or line chart.
     */

    this.chartType = this.chart.type;


    /*
     * Create X-axis labels.
     *
     * Product charts:
     * Phone, Laptop, Chair...
     *
     * Time charts:
     * 01 Jun, 03 Jun, 05 Jun...
     */

    const labels = this.chart.data.map(

      item =>
        item.category ??
        this.formatDate(item.date)

    );


    /*
     * Extract numerical values.
     */

    const values = this.chart.data.map(

      item =>
        item.value

    );


    /*
     * Build Chart.js data.
     */

    this.chartData = {

      labels: labels,


      datasets: [

        {

          data: values,

          label: this.chart.y_axis,


          backgroundColor:

            this.chart.type === 'bar'

              ? 'rgba(125, 93, 55, 0.82)'

              : 'rgba(125, 93, 55, 0.12)',


          borderColor: '#7d5d37',


          borderWidth:

            this.chart.type === 'line'
              ? 2.5
              : 1,


          borderRadius:

            this.chart.type === 'bar'
              ? 5
              : 0,


          pointBackgroundColor:
            '#7d5d37',


          pointBorderColor:
            '#f8f3ea',


          pointBorderWidth: 2,


          pointRadius:

            this.chart.type === 'line'
              ? 4
              : 0,


          tension:

            this.chart.type === 'line'
              ? 0.35
              : 0,


          fill:

            this.chart.type === 'line'

        }

      ]

    };

  }


  /*
   * Convert backend ISO dates
   * into clean labels.
   *
   * Example:
   *
   * 2026-06-01T00:00:00
   *
   * becomes:
   *
   * 01 Jun
   */

  private formatDate(
    date?: string
  ): string {

    if (!date) {
      return '';
    }


    const parsedDate =
      new Date(date);


    if (
      Number.isNaN(
        parsedDate.getTime()
      )
    ) {

      return date;

    }


    return parsedDate.toLocaleDateString(

      'en-IN',

      {

        day: '2-digit',

        month: 'short'

      }

    );

  }

}