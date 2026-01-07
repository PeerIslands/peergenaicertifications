// Use dynamic import to properly load pdf-parse as ESM
let pdfParseModule: any;

async function getPdfParseClass() {
  if (!pdfParseModule) {
    pdfParseModule = await import("pdf-parse");
  }
  // pdf-parse v2 exports PDFParse as a named export (class, not function)
  return pdfParseModule.PDFParse;
}

export interface PDFContent {
  text: string;
  pages: number;
}

export async function extractTextFromPDF(buffer: Buffer): Promise<PDFContent> {
  try {
    const PDFParse = await getPdfParseClass();
    // pdf-parse v2: Create instance with buffer as data option, then call getText()
    const parser = new PDFParse({ data: buffer });
    const result = await parser.getText();
    
    // Get page count from info
    const info = await parser.getInfo({ parsePageInfo: true });
    const numPages = info.numPages || 1;
    
    return {
      text: result.text,
      pages: numPages,
    };
  } catch (error) {
    console.error("PDF parsing error:", error);
    throw new Error("Failed to parse PDF");
  }
}

export interface TextChunk {
  content: string;
  page: number;
}

export function chunkText(
  text: string, 
  chunkSize: number = 500, 
  overlap: number = 50
): TextChunk[] {
  const chunks: TextChunk[] = [];
  
  // Split text by pages (rough approximation using double newlines)
  const paragraphs = text.split(/\n\s*\n/);
  
  let currentChunk = "";
  let currentPage = 1;
  let charCount = 0;
  
  for (const paragraph of paragraphs) {
    const trimmedParagraph = paragraph.trim();
    if (!trimmedParagraph) continue;
    
    // Estimate page breaks (approximately every 3000 characters)
    charCount += trimmedParagraph.length;
    if (charCount > 3000) {
      currentPage++;
      charCount = trimmedParagraph.length;
    }
    
    if (currentChunk.length + trimmedParagraph.length > chunkSize) {
      if (currentChunk.trim()) {
        chunks.push({
          content: currentChunk.trim(),
          page: currentPage,
        });
      }
      
      // Start new chunk with overlap from previous
      const overlapStart = Math.max(0, currentChunk.length - overlap);
      currentChunk = currentChunk.slice(overlapStart) + " " + trimmedParagraph;
    } else {
      currentChunk += (currentChunk ? " " : "") + trimmedParagraph;
    }
  }
  
  // Add final chunk
  if (currentChunk.trim()) {
    chunks.push({
      content: currentChunk.trim(),
      page: currentPage,
    });
  }
  
  return chunks;
}
