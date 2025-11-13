import fitz  # PyMuPDF
import docx
import pandas as pd

def extract_text(file_path, filename):
    if filename.endswith(".pdf"):
        doc = fitz.open(file_path)
        text = " ".join(page.get_text() for page in doc)
        doc.close()
        return text

    elif filename.endswith(".docx"):
        doc = docx.Document(file_path)
        return " ".join([p.text for p in doc.paragraphs])

    elif filename.endswith(".csv"):
        df = pd.read_csv(file_path)
        return df.to_string()

    else:
        return ""
