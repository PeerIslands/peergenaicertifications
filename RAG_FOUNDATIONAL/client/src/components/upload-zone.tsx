import { useState } from "react"
import { Upload, FileText, X, CheckCircle } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

interface FileUpload {
  id: string
  file: File
  progress: number
  status: "uploading" | "completed" | "error"
}

interface UploadZoneProps {
  onUpload?: (files: File[]) => void
  className?: string
}

export function UploadZone({ onUpload, className }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploads, setUploads] = useState<FileUpload[]>([])
  const maxUploadMb = Number(import.meta.env.VITE_MAX_UPLOAD_MB || 50)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
      .filter(file => file.type === "application/pdf")
      .filter(file => file.size <= maxUploadMb * 1024 * 1024)
    
    const rejected = Array.from(e.dataTransfer.files).filter(
      file => file.type !== "application/pdf" || file.size > maxUploadMb * 1024 * 1024
    )
    if (rejected.length > 0) {
      // eslint-disable-next-line no-alert
      alert(`Some files were rejected. Only PDF files up to ${maxUploadMb}MB are allowed.`)
    }
    
    if (files.length > 0) {
      handleFiles(files)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length > 0) {
      const allowed = files
        .filter(file => file.type === "application/pdf")
        .filter(file => file.size <= maxUploadMb * 1024 * 1024)
      const rejected = files.filter(file => file.type !== "application/pdf" || file.size > maxUploadMb * 1024 * 1024)
      if (rejected.length > 0) {
        // eslint-disable-next-line no-alert
        alert(`Some files were rejected. Only PDF files up to ${maxUploadMb}MB are allowed.`)
      }
      handleFiles(allowed)
    }
  }

  const handleFiles = (files: File[]) => {
    const newUploads: FileUpload[] = files.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      progress: 0,
      status: "uploading" as const
    }))
    
    setUploads(prev => [...prev, ...newUploads])
    
    // Start actual upload via parent callback
    onUpload?.(files)
    
    // Simulate progress for UI feedback
    newUploads.forEach(upload => {
      let progress = 0
      const interval = setInterval(() => {
        progress += Math.random() * 25 + 5
        if (progress >= 100) {
          progress = 100
          clearInterval(interval)
          setUploads(prev => prev.map(u => 
            u.id === upload.id ? { ...u, progress: 100, status: "completed" } : u
          ))
        } else {
          setUploads(prev => prev.map(u => 
            u.id === upload.id ? { ...u, progress } : u
          ))
        }
      }, 300)
    })
  }

  const removeUpload = (id: string) => {
    setUploads(prev => prev.filter(u => u.id !== id))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  return (
    <div className={className}>
      <Card 
        className={`border-2 border-dashed transition-colors ${
          isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        data-testid="upload-zone"
      >
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <Upload className={`h-12 w-12 mb-4 ${isDragging ? "text-primary" : "text-muted-foreground"}`} />
          <h3 className="text-lg font-medium mb-2">Upload PDF Documents</h3>
          <p className="text-muted-foreground mb-4 max-w-sm">
            Drag and drop your PDF files here, or click to browse
          </p>
          <input
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileInput}
            className="hidden"
            id="file-upload"
            data-testid="input-file-upload"
          />
          <Button asChild data-testid="button-browse-files">
            <label htmlFor="file-upload" className="cursor-pointer">
              Browse Files
            </label>
          </Button>
          <p className="text-xs text-muted-foreground mt-2">
            Supports PDF files up to {maxUploadMb}MB
          </p>
        </CardContent>
      </Card>

      {uploads.length > 0 && (
        <div className="mt-6 space-y-3">
          <h4 className="font-medium">Uploading Files</h4>
          {uploads.map((upload) => (
            <Card key={upload.id} className="p-4" data-testid={`upload-item-${upload.id}`}>
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-primary flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium truncate">{upload.file.name}</p>
                    <div className="flex items-center gap-2">
                      {upload.status === "completed" && (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeUpload(upload.id)}
                        data-testid={`button-remove-upload-${upload.id}`}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                    <span>{formatFileSize(upload.file.size)}</span>
                    <span>•</span>
                    <span>{upload.status === "completed" ? "Completed" : `${Math.round(upload.progress)}%`}</span>
                  </div>
                  {upload.status === "uploading" && (
                    <Progress value={upload.progress} className="h-1" />
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}