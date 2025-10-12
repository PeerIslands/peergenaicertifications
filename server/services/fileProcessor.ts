import mammoth from 'mammoth';
import fs from 'fs';
import pdfParse from 'pdf-parse/lib/pdf-parse.js';

export class FileProcessor {
  /**
   * Extract text content from uploaded file based on its MIME type
   */
  static async extractText(filePath: string, mimeType: string): Promise<string> {
    try {
      switch (mimeType) {
        case 'application/pdf':
          return await this.extractFromPDF(filePath);
        case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
          return await this.extractFromDocx(filePath);
        case 'text/plain':
          return await this.extractFromTxt(filePath);
        default:
          throw new Error(`Unsupported file type: ${mimeType}`);
      }
    } catch (error) {
      console.error('Error extracting text from file:', error);
      throw new Error(`Failed to extract text from file: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Extract text from PDF file
   */
  private static async extractFromPDF(filePath: string): Promise<string> {

    try {
      // console.log("Trying to extract PDF from:", filePath);
      if (!fs.existsSync(filePath)) {
        throw new Error("File does not exist: " + filePath);
      }
      const dataBuffer = fs.readFileSync(filePath);
      console.log("typeof dataBuffer:", typeof dataBuffer);
      console.log("is Buffer:", Buffer.isBuffer(dataBuffer));
      console.log("filePath:", filePath);
      const pdfData = await pdfParse(dataBuffer);
      if (!pdfData.text.trim()) {
        throw new Error("PDF has no extractable text (possibly scanned images).");
      }
      return pdfData.text;
    } catch (err: any) {
      console.error("PDF extraction failed:", err.message);
      throw new Error("Failed to extract text from PDF file: " + err.message);
    }
  }

  /**
   * Extract text from DOCX file
   */
  private static async extractFromDocx(filePath: string): Promise<string> {
    const result = await mammoth.extractRawText({ path: filePath });
    return result.value;
  }

  /**
   * Extract text from TXT file
   */
  private static async extractFromTxt(filePath: string): Promise<string> {
    return fs.readFileSync(filePath, 'utf8');
  }

  /**
   * Validate file type
   */
  static isValidFileType(mimeType: string): boolean {
    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    return allowedTypes.includes(mimeType);
  }

  /**
   * Get file extension from MIME type
   */
  static getFileExtension(mimeType: string): string {
    const extensions: Record<string, string> = {
      'application/pdf': '.pdf',
      'text/plain': '.txt',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
    };
    return extensions[mimeType] || '';
  }

  /**
   * Clean up temporary file
   */
  static cleanupFile(filePath: string): void {
    try {
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    } catch (error) {
      console.error('Error cleaning up file:', error);
    }
  }
}
