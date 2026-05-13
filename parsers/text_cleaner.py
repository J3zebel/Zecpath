import re
import string

def clean_and_normalize(raw_text: str) -> str:
    """
    Cleans unwanted symbols, noise, formatting issues and normalizes text.
    Handles capitalization, bullet points, and section headings.
    """
    if not raw_text:
        return ""

    # Remove zero-width spaces and other invisible formatting characters
    text = re.sub(r'[\u200b\u200e\u200f\u202a-\u202e]', '', raw_text)
    
    # Normalize bullet points (•, *, ◦, ▪, etc.) to a standard '-'
    text = re.sub(r'[\u2022\u25E6\u25AA\u2023\u2043\u2219\*]', '-', text)
    
    # Normalize excessive newlines to double newlines (paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Normalize excessive spaces
    text = re.sub(r' {2,}', ' ', text)

    # Normalize Section headings: We attempt to find common section names that might be surrounded by noise
    # and ensure they are properly capitalized and on their own line.
    sections = [
        "EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT", "SKILLS", 
        "EDUCATION", "CERTIFICATIONS", "PROJECTS", "SUMMARY", "PROFILE", "OBJECTIVE"
    ]
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(stripped)
            continue
            
        # Check if line matches a known section header (case insensitive)
        upper_stripped = stripped.upper()
        is_section = False
        for sec in sections:
            # Match exactly or with trailing colons
            if upper_stripped == sec or upper_stripped == sec + ":":
                cleaned_lines.append(f"\n{sec}")  # Normalize to pure uppercase, ensure empty line before
                is_section = True
                break
                
        if not is_section:
            # Capitalize the first letter if it's a normal sentence, but preserve other casing
            # (In resumes, many lines are fragments or bullet points, so we are careful)
            if stripped.startswith('- '):
                # Bullet point
                content = stripped[2:]
                if content:
                    content = content[0].upper() + content[1:]
                cleaned_lines.append(f"- {content}")
            else:
                cleaned_lines.append(stripped)

    # Join back together
    text = '\n'.join(cleaned_lines)
    
    # Clean up any leftover leading/trailing whitespace
    return text.strip()
