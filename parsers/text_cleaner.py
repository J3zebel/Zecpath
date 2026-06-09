import re
import string

# Dictionary mapping standardized section headings to their common variations
NORMALIZED_SECTIONS = {
    "SUMMARY": [
        "SUMMARY", "PROFESSIONAL SUMMARY", "PROFILE", "OBJECTIVE", 
        "CAREER OBJECTIVE", "ABOUT ME", "EXECUTIVE SUMMARY", "CAREER SUMMARY"
    ],
    "WORK EXPERIENCE": [
        "WORK EXPERIENCE", "EXPERIENCE", "EMPLOYMENT", "EMPLOYMENT HISTORY", 
        "PROFESSIONAL EXPERIENCE", "WORK HISTORY", "JOB HISTORY", "CAREER HISTORY",
        "PROFESSIONAL BACKGROUND", "CAREER BACKGROUND"
    ],
    "SKILLS": [
        "SKILLS", "TECHNICAL SKILLS", "KEY SKILLS", "AREAS OF EXPERTISE", 
        "CORE COMPETENCIES", "SKILLS & TECHNOLOGIES", "TECHNOLOGY STACK", "TECHNOLOGIES"
    ],
    "EDUCATION": [
        "EDUCATION", "ACADEMIC PROFILE", "ACADEMIC BACKGROUND", "ACADEMIC QUALIFICATIONS",
        "EDUCATION AND CREDENTIALS", "EDUCATION BACKGROUND"
    ],
    "CERTIFICATIONS": [
        "CERTIFICATIONS", "CERTIFICATES", "LICENSES & CERTIFICATIONS", "LICENSES",
        "PROFESSIONAL CERTIFICATIONS"
    ],
    "PROJECTS": [
        "PROJECTS", "ACADEMIC PROJECTS", "PERSONAL PROJECTS", "KEY PROJECTS", "SELECTED PROJECTS"
    ],
    "LANGUAGES": ["LANGUAGES", "LANGUAGES KNOWN", "LANGUAGE SKILLS"],
    "AWARDS": ["AWARDS", "HONORS", "HONORS & AWARDS", "ACHIEVEMENTS", "KEY ACHIEVEMENTS"],
    "COURSES": ["COURSES", "RELEVANT COURSES", "ADDITIONAL EDUCATION", "TRAININGS"],
    "PUBLICATIONS": ["PUBLICATIONS", "RESEARCH & PUBLICATIONS"],
    "INTERESTS": ["INTERESTS", "HOBBIES", "ACTIVITIES"]
}

def clean_and_normalize(raw_text: str) -> str:
    """
    Cleans unwanted symbols, noise, formatting issues and normalizes text.
    Handles capitalization, bullet points, and maps section headings to standardized forms.
    """
    if not raw_text:
        return ""

    # Remove zero-width spaces and other invisible formatting characters
    text = re.sub(r'[\u200b\u200e\u200f\u202a-\u202e]', '', raw_text)
    
    # Normalize bullet points (•, *, ◦, ▪, etc.) to a standard '-'
    text = re.sub(r'[\u2022\u25E6\u25AA\u2023\u2043\u2219\*]', '-', text)
    
    # Normalize excessive newlines to double newlines (paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Normalize excessive spaces (excluding leading spaces in layout)
    text = re.sub(r' {2,}', ' ', text)
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(stripped)
            continue
            
        # Normalize and clean lines that might be section headers
        upper_stripped = stripped.upper()
        # Remove trailing colons, spaces, and dashes from heading checks
        header_check = re.sub(r'[:\-\_\s]+$', '', upper_stripped).strip()
        
        is_section = False
        for std_heading, variations in NORMALIZED_SECTIONS.items():
            if header_check == std_heading or header_check in variations:
                cleaned_lines.append(f"\n{std_heading}")  # Add empty line before for formatting
                is_section = True
                break
                
        if not is_section:
            # Bullet point standardization
            if stripped.startswith('-'):
                # Extract text after bullet
                content = stripped[1:].strip()
                if content:
                    # Capitalize first letter of bullet point content
                    content = content[0].upper() + content[1:]
                cleaned_lines.append(f"- {content}")
            elif stripped.startswith('*'):
                content = stripped[1:].strip()
                if content:
                    content = content[0].upper() + content[1:]
                cleaned_lines.append(f"- {content}")
            else:
                # Capitalize first character if it's start of a word
                # but preserve other case layouts
                if stripped and stripped[0].isalpha():
                    stripped = stripped[0].upper() + stripped[1:]
                cleaned_lines.append(stripped)

    # Join back together
    text = '\n'.join(cleaned_lines)
    
    # Deduplicate empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def segment_resume_by_sections(cleaned_text: str) -> dict:
    """
    Segments the cleaned resume text into a dictionary based on normalized section headings.
    Any text before the first heading is placed in the 'HEADER' key.
    """
    standard_headings = list(NORMALIZED_SECTIONS.keys())
    
    lines = cleaned_text.split('\n')
    sections = {"HEADER": []}
    current_section = "HEADER"
    
    for line in lines:
        stripped = line.strip()
        if stripped in standard_headings:
            current_section = stripped
            sections[current_section] = []
        else:
            sections[current_section].append(line)
            
    segmented = {}
    for sec, sec_lines in sections.items():
        sec_text = "\n".join(sec_lines).strip()
        if sec_text:
            segmented[sec] = sec_text
            
    return segmented

