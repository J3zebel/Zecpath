# pyrefly: ignore [missing-import]
import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    Attempts to preserve layout to maintain column separation.
    """
    extracted_text = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Extract text preserving layout (helps with columns and tables)
                text = page.extract_text(layout=True)
                if text:
                    extracted_text.append(text)
                    
        return "\n\n".join(extracted_text)
    except Exception as e:
        # Re-raise with context
        raise RuntimeError(f"Failed to extract text from PDF {file_path}: {str(e)}")
