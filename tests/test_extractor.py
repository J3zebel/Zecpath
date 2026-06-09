import os
# pyrefly: ignore [missing-import]
import pytest
from parsers.text_cleaner import clean_and_normalize, segment_resume_by_sections
from parsers.extractor import extract_resume
from parsers.pdf_parser import format_table_as_markdown

def test_text_cleaner_basic():
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Successfully started Resume Extraction Engine tests.")
    raw = " \u200b  Here is some text \u200e\n\n\n\nWith multiple   spaces\n"
    cleaned = clean_and_normalize(raw)
    assert "Here is some text\n\nWith multiple spaces" in cleaned

def test_text_cleaner_bullets():
    raw = "• Python\n* Java\n◦ C++\n"
    cleaned = clean_and_normalize(raw)
    assert "- Python\n- Java\n- C++" in cleaned

def test_text_cleaner_sections():
    raw = "work experience\n- software engineer at Google"
    cleaned = clean_and_normalize(raw)
    assert "WORK EXPERIENCE" in cleaned
    assert "- Software engineer at Google" in cleaned

def test_text_cleaner_heading_normalization():
    # Test mapping of different variations to standardized uppercase headers
    variations = [
        "Professional Experience", 
        "Work History:", 
        "EMPLOYMENT HISTORY -",
        "Technical Skills", 
        "Technology Stack", 
        "Education Background:",
        "Academic Profile"
    ]
    for var in variations:
        cleaned = clean_and_normalize(var)
        # Verify it normalized to one of the standard headings
        assert cleaned in ["WORK EXPERIENCE", "SKILLS", "EDUCATION"]

def test_segmentation():
    text = """John Doe
Email: john@example.com

SUMMARY
Passionate software developer.

WORK EXPERIENCE
- Software Engineer at Google

SKILLS
- Python
- JavaScript
"""
    cleaned = clean_and_normalize(text)
    segmented = segment_resume_by_sections(cleaned)
    
    assert "HEADER" in segmented
    assert "John Doe" in segmented["HEADER"]
    assert "SUMMARY" in segmented
    assert "Passionate software developer." in segmented["SUMMARY"]
    assert "WORK EXPERIENCE" in segmented
    assert "- Software Engineer at Google" in segmented["WORK EXPERIENCE"]
    assert "SKILLS" in segmented
    assert "- Python\n- JavaScript" in segmented["SKILLS"]

def test_table_formatting():
    table_data = [
        ["Degree", "Institution", "Year"],
        ["B.S. CS", "Stanford University", "2022"],
        ["M.S. CS", "MIT", "2024"]
    ]
    markdown = format_table_as_markdown(table_data)
    expected = (
        "\n"
        "| Degree | Institution | Year |\n"
        "| --- | --- | --- |\n"
        "| B.S. CS | Stanford University | 2022 |\n"
        "| M.S. CS | MIT | 2024 |\n"
    )
    assert markdown == expected

def test_extractor_missing_file():
    import logging
    logging.disable(logging.ERROR)
    try:
        with pytest.raises(FileNotFoundError):
            extract_resume("non_existent_file.pdf")
    finally:
        logging.disable(logging.NOTSET)

