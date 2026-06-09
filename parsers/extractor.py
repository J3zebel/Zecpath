import os
import logging
import json
import datetime
from .pdf_parser import extract_text_from_pdf
from .docx_parser import extract_text_from_docx
from .text_cleaner import clean_and_normalize, segment_resume_by_sections

# Try to use the project logger, otherwise fallback to standard logging
try:
    from utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

def extract_resume(file_path: str, output_dir: str = None, json_output_dir: str = None) -> str:
    """
    Main orchestrator to extract, clean, normalize, and segment text from a resume.
    
    Args:
        file_path: Path to the PDF or DOCX file.
        output_dir: Optional directory to save the cleaned text.
        json_output_dir: Optional directory to save the structured JSON. If not provided,
                         it defaults to output_dir.
        
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
        
        # Parse into structured sections
        sections = segment_resume_by_sections(cleaned_text)
        
        # Collect statistics and metadata
        file_size = os.path.getsize(file_path)
        word_count = len(cleaned_text.split())
        char_count = len(cleaned_text)
        
        structured_data = {
            "metadata": {
                "filename": os.path.basename(file_path),
                "filepath": os.path.abspath(file_path),
                "file_size_bytes": file_size,
                "format": ext,
                "word_count": word_count,
                "char_count": char_count,
                "extracted_at": datetime.datetime.utcnow().isoformat() + "Z"
            },
            "sections": sections,
            "raw_cleaned_text": cleaned_text
        }
        
        # Save output files if directories are provided
        if output_dir or json_output_dir:
            base_name = os.path.basename(file_path)
            prefix = os.path.splitext(base_name)[0]
            
            # Save plain cleaned text
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                txt_output_file = os.path.join(output_dir, f"{prefix}_cleaned.txt")
                with open(txt_output_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
                logger.info(f"Saved cleaned text to {txt_output_file}")
            
            # Save structured JSON
            target_json_dir = json_output_dir if json_output_dir else output_dir
            if target_json_dir:
                os.makedirs(target_json_dir, exist_ok=True)
                json_output_file = os.path.join(target_json_dir, f"{prefix}_structured.json")
                with open(json_output_file, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved structured JSON to {json_output_file}")
            
        return cleaned_text
        
    except Exception as e:
        logger.error(f"Error extracting resume {file_path}: {str(e)}")
        raise


