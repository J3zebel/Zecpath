import os
import pytest
from parsers.text_cleaner import clean_and_normalize
from parsers.extractor import extract_resume

def test_text_cleaner_basic():
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

def test_extractor_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_resume("non_existent_file.pdf")

# We can also mock pdfplumber and python-docx to test the extraction integration,
# but for now we rely on the text cleaner tests to verify the core logic.
# Actual file extraction tests would require sample files.
