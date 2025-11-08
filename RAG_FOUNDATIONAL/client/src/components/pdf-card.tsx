import { FileText, Download, Trash2, Calendar } from "lucide-react"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { Pdf } from "@shared/schema"

interface PdfCardProps {
  pdf: Pdf
  onDelete?: (id: string) => void
  onDownload?: (id: string) => void
}

export function PdfCard({ pdf, onDelete, onDownload }: PdfCardProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const formatDate = (date: Date | null) => {
    if (!date) return "Unknown"
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(new Date(date))
  }

  return (
    <Card className="hover-elevate transition-all duration-200" data-testid={`pdf-card-${pdf.id}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className="p-2 bg-primary/10 rounded-lg">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="font-medium text-sm leading-tight truncate" title={pdf.originalName}>
                {pdf.originalName}
              </h3>
              <p className="text-xs text-muted-foreground mt-1">
                {formatFileSize(pdf.fileSize)}
              </p>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0 pb-3">
        <div className="space-y-2">
          {pdf.pageCount && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{pdf.pageCount} pages</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>Uploaded {formatDate(pdf.uploadedAt)}</span>
          </div>
          <div className="flex gap-1">
            <Badge variant="secondary" className="text-xs">
              {pdf.processedAt ? "Processed" : "Processing"}
            </Badge>
          </div>
        </div>
      </CardContent>

      <CardFooter className="pt-0 flex gap-2">
        <Button
          size="sm"
          variant="outline"
          onClick={() => onDownload?.(pdf.id)}
          data-testid={`button-download-${pdf.id}`}
          className="flex-1"
        >
          <Download className="h-3 w-3 mr-1" />
          Download
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onDelete?.(pdf.id)}
          data-testid={`button-delete-${pdf.id}`}
        >
          <Trash2 className="h-3 w-3" />
        </Button>
      </CardFooter>
    </Card>
  )
}