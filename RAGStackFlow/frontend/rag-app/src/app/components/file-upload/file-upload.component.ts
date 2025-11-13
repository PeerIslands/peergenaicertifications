import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatProgressBarModule, MatSnackBarModule],
  templateUrl: './file-upload.component.html',
  styleUrl: './file-upload.component.scss'
})
export class FileUploadComponent {
  @Output() fileUploaded = new EventEmitter<void>();
  
  isDragging = false;
  isUploading = false;
  uploadedFiles: string[] = [];

  constructor(
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) {}

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFiles(files);
    }
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.handleFiles(input.files);
    }
  }

  handleFiles(files: FileList) {
    const allowedExtensions = ['.pdf', '.docx', '.xlsx', '.txt', '.csv', '.md'];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!allowedExtensions.includes(ext)) {
        this.snackBar.open(`File type ${ext} not supported`, 'Close', { duration: 3000 });
        continue;
      }
      
      this.uploadFile(file);
    }
  }

  uploadFile(file: File) {
    this.isUploading = true;
    
    this.apiService.uploadDocument(file).subscribe({
      next: (response) => {
        this.uploadedFiles.push(file.name);
        this.snackBar.open(
          `${file.name} uploaded successfully (${response.chunks_created} chunks)`, 
          'Close', 
          { duration: 3000 }
        );
        this.isUploading = false;
        this.fileUploaded.emit();
      },
      error: (error) => {
        this.snackBar.open(`Failed to upload ${file.name}: ${error.error?.detail || error.message}`, 'Close', { duration: 5000 });
        this.isUploading = false;
      }
    });
  }
}
