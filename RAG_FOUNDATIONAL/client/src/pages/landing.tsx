import { FileText, Upload, MessageSquare, LayoutDashboard, Users, Zap, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Landing() {
  const features = [
    {
      icon: Upload,
      title: "Upload PDFs",
      description: "Easily upload and organize your PDF documents in one secure location"
    },
    {
      icon: Search,
      title: "AI-Powered Search",
      description: "Find specific information across all your documents with intelligent search"
    },
    {
      icon: MessageSquare,
      title: "Chat with Documents",
      description: "Ask questions about your documents and get instant, accurate answers"
    },
    {
      icon: LayoutDashboard,
      title: "Organized Dashboard",
      description: "View and manage all your documents from a clean, intuitive interface"
    },
    {
      icon: Zap,
      title: "Fast Processing",
      description: "Quick text extraction and analysis using advanced AI technology"
    },
    {
      icon: Users,
      title: "Secure Access",
      description: "Your documents are private and secure with industry-standard encryption"
    }
  ]

  const handleLogin = () => {
    window.location.href = "/api/login"
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <div className="container mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="p-3 bg-primary/10 rounded-lg">
              <FileText className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-4xl font-bold">RAG</h1>
          </div>
          
          <h2 className="text-3xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
            AI-Powered PDF Search & Analysis
          </h2>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Upload your PDF documents and unlock the power of AI-driven search and analysis. 
            Find information instantly, ask questions, and get insights from your document library.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              onClick={handleLogin}
              data-testid="button-get-started"
              className="px-8 py-3 text-lg"
            >
              Get Started with Google
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
              data-testid="button-learn-more"
              className="px-8 py-3 text-lg"
            >
              Learn More
            </Button>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className="mb-16">
          <h3 className="text-2xl font-semibold text-center mb-12">
            Everything you need to manage your documents
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="hover-elevate transition-all duration-200">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <feature.icon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* How it Works */}
        <div className="text-center mb-16">
          <h3 className="text-2xl font-semibold mb-12">How DocuRAG Works</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-primary">1</span>
              </div>
              <h4 className="text-lg font-medium mb-2">Upload Documents</h4>
              <p className="text-muted-foreground text-center">
                Securely upload your PDF documents to our platform
              </p>
            </div>
            
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-primary">2</span>
              </div>
              <h4 className="text-lg font-medium mb-2">AI Processing</h4>
              <p className="text-muted-foreground text-center">
                Our AI extracts and analyzes text content for intelligent search
              </p>
            </div>
            
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-primary">3</span>
              </div>
              <h4 className="text-lg font-medium mb-2">Search & Chat</h4>
              <p className="text-muted-foreground text-center">
                Find information instantly or chat with your documents
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <Card className="max-w-2xl mx-auto">
            <CardContent className="pt-8 pb-8">
              <h3 className="text-2xl font-semibold mb-4">Ready to get started?</h3>
              <p className="text-muted-foreground mb-6">
                Join thousands of users who trust DocuRAG for their document management needs.
              </p>
              <Button 
                size="lg" 
                onClick={handleLogin}
                data-testid="button-sign-up-cta"
                className="px-8 py-3 text-lg"
              >
                Sign Up with Google
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}