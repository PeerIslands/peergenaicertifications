import { PdfCard } from '../pdf-card'
import { clientLogger } from "@/lib/logger";
import type { Pdf } from "@shared/schema"

const mockPdf: Pdf = {
  id: "1",
  userId: "user1",
  fileName: "machine_learning_basics.pdf",
  originalName: "Machine Learning Basics.pdf",
  filePath: "/uploads/machine_learning_basics.pdf",
  fileSize: 2456789,
  pageCount: 45,
  extractedText: "Machine learning fundamentals...",
  metadata: { author: "Dr. Smith", subject: "AI/ML" },
  uploadedAt: new Date("2024-01-15"),
  processedAt: new Date("2024-01-15"),
}

export default function PdfCardExample() {
  return (
    <PdfCard 
      pdf={mockPdf}
      onDelete={(id) => clientLogger.info('Delete', { id })}
      onDownload={(id) => clientLogger.info('Download', { id })}
    />
  )
}