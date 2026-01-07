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

export async function extractTextFromPDF(file: File): Promise<string> {
  // Read file as text for PDF extraction
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const arrayBuffer = reader.result as ArrayBuffer;
        const response = await fetch("/api/extract-text", {
          method: "POST",
          headers: {
            "Content-Type": "application/octet-stream",
          },
          body: arrayBuffer,
        });

        if (!response.ok) {
          reject(new Error("Failed to extract text from PDF"));
          return;
        }

        const data = await response.json();
        resolve(data.text);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.readAsArrayBuffer(file);
  });
}
