# pyrefly: ignore [missing-import]
import docx
from docx.text.paragraph import Paragraph
from docx.table import Table

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    Iterates through elements in XML body order to preserve paragraph and table sequence.
    """
    extracted_text = []
    
    try:
        doc = docx.Document(file_path)
        
        # Iterate over the body elements to preserve logical document sequence
        for child in doc.element.body:
            tag = child.tag
            if tag.endswith('p'):
                # Handle paragraphs
                p = Paragraph(child, doc)
                text = p.text.strip()
                if text:
                    # Clean up multiple spaces, preserving structural content
                    text = " ".join(text.split())
                    extracted_text.append(text)
            elif tag.endswith('tbl'):
                # Handle tables
                t = Table(child, doc)
                table_lines = []
                cleaned_rows = []
                
                for row in t.rows:
                    cleaned_row = []
                    for cell in row.cells:
                        # cells can have multiple paragraphs/lines
                        cell_text = cell.text.strip()
                        cell_text = " ".join(cell_text.split())
                        cleaned_row.append(cell_text)
                    cleaned_rows.append(cleaned_row)
                    
                if cleaned_rows:
                    num_cols = max(len(r) for r in cleaned_rows)
                    for i, row in enumerate(cleaned_rows):
                        # Pad row if short
                        row = row + [""] * (num_cols - len(row))
                        table_lines.append("| " + " | ".join(row) + " |")
                        if i == 0:
                            # Add divider line below header
                            table_lines.append("| " + " | ".join(["---"] * num_cols) + " |")
                            
                    extracted_text.append("\n" + "\n".join(table_lines) + "\n")
                    
        return "\n\n".join(extracted_text)
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX {file_path}: {str(e)}")

