# pyrefly: ignore [missing-import]
import docx

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    Extracts text from paragraphs and tables.
    """
    extracted_text = []
    
    try:
        doc = docx.Document(file_path)
        
        # Read all elements sequentially? python-docx doesn't easily interleave tables and paragraphs.
        # But we can iterate over the document block level elements if needed.
        # For simplicity, we usually extract all paragraphs then all tables, or we can use the element tree.
        # To keep it simple but somewhat ordered, let's just extract paragraphs first.
        # Most resumes in word are formatted with paragraphs, though some use tables for layout.
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                extracted_text.append(text)
                
        # Also extract tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    # A cell might contain multiple paragraphs, python-docx joins them with \n
                    # but we clean it up
                    cell_text = " ".join(cell_text.split())
                    if cell_text and cell_text not in row_text:
                        row_text.append(cell_text)
                if row_text:
                    extracted_text.append(" | ".join(row_text))

        return "\n".join(extracted_text)
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX {file_path}: {str(e)}")
