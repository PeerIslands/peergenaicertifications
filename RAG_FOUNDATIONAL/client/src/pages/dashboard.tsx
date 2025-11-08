import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Link } from "wouter"
import { PdfCard } from "@/components/pdf-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { Search, Plus, FileText, Loader2 } from "lucide-react"
import { api } from "@/lib/api"
import type { Pdf } from "@shared/schema"

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("")
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Fetch PDFs - either all PDFs or search results
  const { data: pdfs = [], isLoading, error } = useQuery({
    queryKey: searchQuery.trim() ? ["/api/pdfs/search", searchQuery.trim()] : ["/api/pdfs"],
    queryFn: searchQuery.trim() 
      ? () => api.pdfs.search(searchQuery.trim())
      : api.pdfs.list,
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: api.pdfs.delete,
    onSuccess: () => {
      // Invalidate both lists and search results
      queryClient.invalidateQueries({ queryKey: ["/api/pdfs"] })
      queryClient.invalidateQueries({ queryKey: ["/api/pdfs/search"] })
      toast({
        title: "Success",
        description: "PDF deleted successfully",
      })
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to delete PDF",
        variant: "destructive",
      })
    },
  })

  // No need for client-side filtering since server does the search
  const filteredPdfs = pdfs

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this PDF?")) {
      deleteMutation.mutate(id)
    }
  }

  const handleDownload = (id: string) => {
    const downloadUrl = api.pdfs.download(id)
    window.open(downloadUrl, '_blank')
  }

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <h3 className="text-lg font-medium mb-2">Error loading documents</h3>
          <p className="text-muted-foreground mb-4">
            {error.message || "Failed to load your documents"}
          </p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold mb-2" data-testid="text-page-title">Dashboard</h1>
          <p className="text-muted-foreground">
            Manage and search through your uploaded PDF documents
          </p>
        </div>
        <Button asChild data-testid="button-upload-new">
          <Link href="/upload">
            <Plus className="h-4 w-4 mr-2" />
            Upload New
          </Link>
        </Button>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
            data-testid="input-search-documents"
          />
        </div>
        <div className="text-sm text-muted-foreground">
          {isLoading ? (
            <div className="flex items-center gap-2">
              <Loader2 className="h-3 w-3 animate-spin" />
              Loading...
            </div>
          ) : (
            `${filteredPdfs.length} document${filteredPdfs.length !== 1 ? 's' : ''} found`
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : filteredPdfs.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <FileText className="h-16 w-16 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">
            {searchQuery ? "No documents found" : "No documents uploaded"}
          </h3>
          <p className="text-muted-foreground mb-4 max-w-sm">
            {searchQuery 
              ? "Try adjusting your search terms or upload new documents"
              : "Upload your first PDF document to get started with AI-powered search and analysis"
            }
          </p>
          <Button asChild data-testid="button-upload-first">
            <Link href="/upload">
              <Plus className="h-4 w-4 mr-2" />
              Upload Your First Document
            </Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredPdfs.map((pdf) => (
            <PdfCard
              key={pdf.id}
              pdf={pdf}
              onDelete={handleDelete}
              onDownload={handleDownload}
            />
          ))}
        </div>
      )}
    </div>
  )
}