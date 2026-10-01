import { CommonModule } from '@angular/common';

import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import {
  Router
} from '@angular/router';

import {
  DatasetService
} from '../../services/dataset';

import {
  Dataset
} from '../../models/dataset.model';


@Component({
  selector: 'app-datasets',

  standalone: true,

  imports: [
    CommonModule
  ],

  templateUrl: './datasets.html',

  styleUrl: './datasets.css'
})
export class DatasetsComponent implements OnInit {

  datasets: Dataset[] = [];

  loading = true;

  uploading = false;

  errorMessage = '';

  successMessage = '';

  selectedFile: File | null = null;

  dragActive = false;


  constructor(
    private datasetService: DatasetService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}


  ngOnInit(): void {
    this.loadDatasets();
  }


  loadDatasets(): void {

    this.loading = true;

    this.errorMessage = '';

    this.datasetService
      .getDatasets()
      .subscribe({

        next: response => {

          console.log(
            'Datasets loaded:',
            response
          );

          this.datasets =
            response.datasets || [];

          this.loading = false;

          this.cdr.markForCheck();

        },


        error: error => {

          console.error(
            'Dataset loading error:',
            error
          );

          this.errorMessage =
            'Unable to load your datasets.';

          this.loading = false;

          this.cdr.markForCheck();

        }

      });
  }


  onFileSelected(
    event: Event
  ): void {

    const input =
      event.target as HTMLInputElement;

    if (
      input.files &&
      input.files.length > 0
    ) {

      this.setSelectedFile(
        input.files[0]
      );
    }
  }


  setSelectedFile(
    file: File
  ): void {

    const extension =
      file.name
        .split('.')
        .pop()
        ?.toLowerCase();

    if (
      extension !== 'csv' &&
      extension !== 'xlsx'
    ) {

      this.errorMessage =
        'Only CSV and XLSX files are supported.';

      this.selectedFile = null;

      return;
    }

    this.errorMessage = '';

    this.successMessage = '';

    this.selectedFile = file;

    this.cdr.markForCheck();
  }


  onDragOver(
    event: DragEvent
  ): void {

    event.preventDefault();

    this.dragActive = true;
  }


  onDragLeave(
    event: DragEvent
  ): void {

    event.preventDefault();

    this.dragActive = false;
  }


  onDrop(
    event: DragEvent
  ): void {

    event.preventDefault();

    this.dragActive = false;

    const files =
      event.dataTransfer?.files;

    if (
      files &&
      files.length > 0
    ) {

      this.setSelectedFile(
        files[0]
      );
    }
  }


  uploadDataset(): void {

    if (
      !this.selectedFile ||
      this.uploading
    ) {

      return;
    }

    this.uploading = true;

    this.errorMessage = '';

    this.successMessage = '';

    this.cdr.markForCheck();


    this.datasetService
      .uploadDataset(
        this.selectedFile
      )
      .subscribe({

        next: response => {

          console.log(
            'Dataset uploaded:',
            response
          );

          this.uploading = false;

          this.successMessage =
            `${this.selectedFile?.name} uploaded successfully.`;

          this.selectedFile = null;

          this.cdr.markForCheck();

          this.loadDatasets();

        },


        error: error => {

          console.error(
            'Dataset upload error:',
            error
          );

          this.uploading = false;

          this.errorMessage =
            error?.error?.detail ||
            'Unable to upload the dataset.';

          this.cdr.markForCheck();

        }

      });
  }


  openDataset(
  dataset: Dataset
): void {

  if (!dataset.dataset_id) {
    return;
  }

  this.router.navigate([
    '/analytics',
    dataset.dataset_id
  ]);
}


  formatDate(
    value?: string
  ): string {

    if (!value) {
      return '—';
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {

      return value;
    }

    return date.toLocaleDateString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      }
    );
  }


  formatNumber(
    value?: number
  ): string {

    if (
      value === undefined ||
      value === null
    ) {

      return '—';
    }

    return new Intl.NumberFormat(
      'en-IN'
    ).format(value);
  }


  getFileType(
    filename?: string
  ): string {

    if (!filename) {
      return 'DATA';
    }

    const extension =
      filename
        .split('.')
        .pop()
        ?.toUpperCase();

    return extension || 'DATA';
  }


  clearSelection(): void {

    this.selectedFile = null;

    this.errorMessage = '';

    this.successMessage = '';

    this.cdr.markForCheck();
  }
}