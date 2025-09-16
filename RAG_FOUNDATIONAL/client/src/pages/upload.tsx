import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useLocation } from "wouter"
import { UploadZone } from "@/components/upload-zone"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { FileText, Zap, Search, Shield, CheckCircle } from "lucide-react"
import { api } from "@/lib/api"

export default function Upload() {
  const [, setLocation] = useLocation()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const maxUploadMb = Number(import.meta.env.VITE_MAX_UPLOAD_MB || 50)

  const uploadMutation = useMutation({
    mutationFn: api.pdfs.upload,
    onSuccess: (pdf) => {
      queryClient.invalidateQueries({ queryKey: ["/api/pdfs"] })
      setUploadedFiles(prev => [...prev, pdf.originalName])
      toast({
        title: "Success",
        description: `${pdf.originalName} uploaded successfully`,
      })
    },
    onError: (error) => {
      toast({
        title: "Upload failed",
        description: error.message || "Failed to upload PDF",
        variant: "destructive",
      })
    },
  })

  const handleUpload = async (files: File[]) => {
    for (const file of files) {
      try {
        await uploadMutation.mutateAsync(file)
      } catch (error) {
        // Error handling is done in the mutation
        console.error("Upload error:", error)
      }
    }
  }

  const features = [
    {
      icon: FileText,
      title: "PDF Processing",
      description: "Automatic text extraction and metadata analysis"
    },
    {
      icon: Zap,
      title: "AI-Powered",
      description: "Advanced embeddings for semantic search capabilities"
    },
    {
      icon: Search,
      title: "Smart Search",
      description: "Find information across all your documents instantly"
    },
    {
      icon: Shield,
      title: "Secure Storage",
      description: "Your documents are encrypted and securely stored"
    }
  ]

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold mb-2" data-testid="text-page-title">Upload Documents</h1>
        <p className="text-muted-foreground">
          Upload your PDF documents to enable AI-powered search and analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <UploadZone onUpload={handleUpload} />
          
          {uploadedFiles.length > 0 && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  Recently Uploaded
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {uploadedFiles.map((fileName, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm">
                      <FileText className="h-4 w-4 text-primary" />
                      <span>{fileName}</span>
                    </div>
                  ))}
                </div>
                <Button 
                  className="mt-4" 
                  onClick={() => setLocation("/")}
                  data-testid="button-view-dashboard"
                >
                  View Dashboard
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
        
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">How it works</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {features.map((feature, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <feature.icon className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium text-sm">{feature.title}</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Upload Guidelines</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>• PDF files only (up to {maxUploadMb}MB each)</p>
              <p>• Text-based PDFs work best</p>
              <p>• Scanned documents may have limited searchability</p>
              <p>• Processing typically takes 30-60 seconds</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}