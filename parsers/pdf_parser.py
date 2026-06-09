# pyrefly: ignore [missing-import]
import pdfplumber
import logging

def extract_block_text(crop_page, page_x0: float, page_x1: float) -> str:
    """
    Extracts text from a page crop, checking for a vertical column layout.
    """
    words = crop_page.extract_words()
    if not words:
        return ""
        
    width = page_x1 - page_x0
    # Analyze the occupancy of character bounding boxes along the X-axis relative to page_x0
    x_occupancy = [0] * int(width + 1)
    for w in words:
        x0 = max(0, int(w['x0'] - page_x0))
        x1 = min(int(width), int(w['x1'] - page_x0))
        for x in range(x0, x1 + 1):
            if 0 <= x < len(x_occupancy):
                x_occupancy[x] += 1
                
    # Search for a gutter near the middle of the width (between 25% and 75%)
    mid_start = int(width * 0.25)
    mid_end = int(width * 0.75)
    
    best_gutter_start = -1
    best_gutter_width = 0
    current_gutter_start = -1
    current_gutter_width = 0
    
    for x in range(mid_start, mid_end):
        if x < len(x_occupancy) and x_occupancy[x] == 0:
            if current_gutter_start == -1:
                current_gutter_start = x
            current_gutter_width += 1
        else:
            if current_gutter_width > best_gutter_width:
                best_gutter_width = current_gutter_width
                best_gutter_start = current_gutter_start
            current_gutter_start = -1
            current_gutter_width = 0
            
    if current_gutter_width > best_gutter_width:
        best_gutter_width = current_gutter_width
        best_gutter_start = current_gutter_start
        
    # If we find a clean gutter of at least 15pt width, split into left & right columns
    if best_gutter_width >= 15:
        split_x = page_x0 + best_gutter_start + best_gutter_width / 2.0
        top_y = crop_page.bbox[1]
        bottom_y = crop_page.bbox[3]
        
        try:
            left_crop = crop_page.crop((page_x0, top_y, split_x, bottom_y))
            right_crop = crop_page.crop((split_x, top_y, page_x1, bottom_y))
            
            left_text = left_crop.extract_text(layout=True) or ""
            right_text = right_crop.extract_text(layout=True) or ""
            
            left_clean = "\n".join(line.strip() for line in left_text.split("\n") if line.strip())
            right_clean = "\n".join(line.strip() for line in right_text.split("\n") if line.strip())
            
            if left_clean or right_clean:
                return f"{left_clean}\n\n{right_clean}"
        except Exception:
            pass
            
    # Fallback to normal layout-preserving text extraction
    text = crop_page.extract_text(layout=True) or ""
    return "\n".join(line.strip() for line in text.split("\n") if line.strip())

def format_table_as_markdown(table_data) -> str:
    """
    Formats raw list of lists representing a table into a clean markdown table.
    """
    if not table_data:
        return ""
        
    cleaned_rows = []
    for row in table_data:
        cleaned_row = []
        for cell in row:
            val = cell.strip() if cell else ""
            val = " ".join(val.split())  # normalize spaces
            cleaned_row.append(val)
        cleaned_rows.append(cleaned_row)
        
    # Get column count
    num_cols = max(len(r) for r in cleaned_rows) if cleaned_rows else 0
    if num_cols == 0:
        return ""
        
    markdown_lines = []
    for i, row in enumerate(cleaned_rows):
        row = row + [""] * (num_cols - len(row))
        markdown_lines.append("| " + " | ".join(row) + " |")
        if i == 0:
            markdown_lines.append("| " + " | ".join(["---"] * num_cols) + " |")
            
    return "\n" + "\n".join(markdown_lines) + "\n"

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    Attempts to preserve layout to maintain column separation and structures tables.
    """
    # Setup logger
    try:
        from utils.logger import get_logger
        logger = get_logger(__name__)
    except ImportError:
        logger = logging.getLogger(__name__)
        
    extracted_text = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                raw_page_text = page.extract_text()
                words = page.extract_words()
                
                # Check for image-only (scanned) pages
                if not raw_page_text and not words:
                    if page.images:
                        logger.warning(
                            f"Page {page.page_number} in {file_path} contains images but no extractable text. "
                            "It may be a scanned image PDF."
                        )
                    continue
                    
                # Use page.bbox to get actual coordinate boundaries
                page_x0, page_top, page_x1, page_bottom = page.bbox
                
                # Identify and sort tables
                tables = page.find_tables()
                tables = sorted(tables, key=lambda t: t.bbox[1])
                
                page_parts = []
                current_y = page_top
                
                for t in tables:
                    t_x0, t_top, t_x1, t_bottom = t.bbox
                    
                    # Extract text block above the table
                    if t_top > current_y + 1.0:
                        y_start = max(page_top, current_y)
                        y_end = min(page_bottom, t_top)
                        if y_end > y_start + 1.0:
                            text_crop = page.crop((page_x0, y_start, page_x1, y_end))
                            text = extract_block_text(text_crop, page_x0, page_x1)
                            if text:
                                page_parts.append(text)
                                
                    # Extract and format table
                    table_data = t.extract()
                    table_md = format_table_as_markdown(table_data)
                    if table_md:
                        page_parts.append(table_md)
                        
                    current_y = max(current_y, t_bottom)
                    
                # Extract remaining text block below the last table
                if current_y < page_bottom - 1.0:
                    y_start = max(page_top, current_y)
                    y_end = page_bottom
                    if y_end > y_start + 1.0:
                        text_crop = page.crop((page_x0, y_start, page_x1, y_end))
                        text = extract_block_text(text_crop, page_x0, page_x1)
                        if text:
                            page_parts.append(text)
                            
                page_str = "\n\n".join(page_parts)
                if page_str.strip():
                    extracted_text.append(page_str)
                    
        return "\n\n".join(extracted_text)
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF {file_path}: {str(e)}")


