import os
import logging
from .pdf_parser import extract_text_from_pdf
from .docx_parser import extract_text_from_docx
from .text_cleaner import clean_and_normalize

# Try to use the project logger, otherwise fallback to standard logging
try:
    from utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

def extract_resume(file_path: str, output_dir: str = None) -> str:
    """
    Main orchestrator to extract and clean text from a resume.
    
    Args:
        file_path: Path to the PDF or DOCX file.
        output_dir: Optional directory to save the cleaned text.
        
    Returns:
        The cleaned text as a string.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    
    logger.info(f"Extracting text from {file_path}")
    
    try:
        if ext == '.pdf':
            raw_text = extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            raw_text = extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only PDF and DOCX are supported.")
            
        logger.info("Cleaning and normalizing extracted text.")
        cleaned_text = clean_and_normalize(raw_text)
        
        # Save output if a directory is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.basename(file_path)
            output_file = os.path.join(output_dir, f"{os.path.splitext(base_name)[0]}_cleaned.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            logger.info(f"Saved cleaned text to {output_file}")
            
        return cleaned_text
        
    except Exception as e:
        logger.error(f"Error extracting resume: {str(e)}")
        raise
