"""
Unit tests for the Job Description Parser module.
"""

# No unused imports
from parsers.jd_parser import (
    clean_and_normalize_jd,
    split_jds,
    parse_single_jd,
    detect_skill_synonyms,
    normalize_skills,
    infer_experience_and_education,
    infer_salary_and_benefits,
    build_jd_profile,
    validate_jd_profile,
)


def test_clean_and_normalize_jd():
    raw = " \u200b  Job Overview \u200e\n\n\n• PCB design\n* Embedded C\n"
    cleaned = clean_and_normalize_jd(raw)
    assert "Job Overview" in cleaned
    assert "- PCB design" in cleaned
    assert "- Embedded C" in cleaned
    assert "  " not in cleaned


def test_split_jds():
    consolidated_text = """1. Firmware Engineer Trainee
Job Overview
Some overview text here.

2. Senior Hardware Design Architect
Job Overview
Another overview text here.
"""
    jds = split_jds(consolidated_text)
    assert len(jds) == 2

    assert jds[0][0] == 1
    assert jds[0][1] == "Firmware Engineer Trainee"
    assert "Some overview text here" in jds[0][2]

    assert jds[1][0] == 2
    assert jds[1][1] == "Senior Hardware Design Architect"
    assert "Another overview text here" in jds[1][2]


def test_parse_single_jd():
    jd_text = """Job Overview
Responsible for coding firmware.
Responsibilities
• Write code in C
• Debug using logic analyzer
Required Skills
• Embedded C
• Microcontrollers
• Communication skills (optional)
"""
    raw_data = parse_single_jd("Firmware Engineer Trainee", jd_text)
    assert raw_data["title"] == "Firmware Engineer Trainee"
    assert "Responsible for coding firmware." in raw_data["overview"]
    assert len(raw_data["responsibilities"]) == 2
    assert "Write code in C" in raw_data["responsibilities"]
    assert len(raw_data["skills"]) == 3
    assert "Embedded C" in raw_data["skills"]


def test_detect_skill_synonyms():
    # Test taxonomy mapping
    assert detect_skill_synonyms("Altium Designer") == "PCB Design"
    assert detect_skill_synonyms("KiCad") == "PCB Design"
    assert detect_skill_synonyms("embedded C programming") == "Embedded C/C++"
    assert detect_skill_synonyms("arduino") == "Microcontrollers"
    assert detect_skill_synonyms("STM32 microcontroller") == "Microcontrollers"
    assert detect_skill_synonyms("Diodes & Transistors") == "Analog Electronics"
    assert (
        detect_skill_synonyms("multimeter and oscilloscope")
        == "Hardware Testing & Troubleshooting"
    )

    # Test pass-through of unknown skill
    assert detect_skill_synonyms("Some Rare Tech Stack") == "Some Rare Tech Stack"


def test_normalize_skills():
    raw_skills = [
        "Altium Designer (preferred)",
        "PCB Layout",
        "Embedded C programming",
        "Microcontrollers (optional)",
        "Teamwork",
    ]

    mandatory, preferred = normalize_skills(raw_skills, "Beginner")

    # Altium and Microcontrollers have "preferred/optional", so they should end up in preferred
    # PCB Layout and Embedded C programming and Teamwork are mandatory
    mandatory_names = [s["name"] for s in mandatory]
    preferred_names = [s["name"] for s in preferred]

    assert "PCB Design" in mandatory_names
    assert "Embedded C/C++" in mandatory_names
    assert "Teamwork" in mandatory_names

    # Check that Altium Designer (mapped to PCB Design) is in preferred
    assert "PCB Design" in preferred_names
    assert "Microcontrollers" in preferred_names


def test_infer_experience_and_education():
    # Trainee
    exp, edu, seniority, emp_type = infer_experience_and_education(
        "Graduate Engineer Trainee (GET)"
    )
    assert seniority == "Beginner"
    assert exp["min_years"] == 0
    assert exp["max_years"] == 1
    assert "Bachelor" in edu[0]
    assert emp_type == "Full-time"

    # Junior
    exp, edu, seniority, emp_type = infer_experience_and_education(
        "Junior Hardware Engineer"
    )
    assert seniority == "Beginner"
    assert exp["min_years"] == 1
    assert exp["max_years"] == 3

    # Senior
    exp, edu, seniority, emp_type = infer_experience_and_education(
        "Senior Embedded Systems Engineer"
    )
    assert seniority == "Advanced"
    assert exp["min_years"] == 5
    assert exp["max_years"] == 8

    # Scientist / Research (PhD/Masters)
    exp, edu, seniority, emp_type = infer_experience_and_education(
        "Quantum Electronics Research Scientist"
    )
    assert "Ph.D." in edu[0]
    assert seniority == "Advanced" or seniority == "Expert"


def test_infer_salary_and_benefits():
    salary, benefits = infer_salary_and_benefits("Senior Engineer", "Advanced")
    assert salary["min"] == 100000
    assert salary["max"] == 140000
    assert "Retirement Matching (401k)" in benefits


def test_build_jd_profile_and_validate():
    raw_data = {
        "title": "Electronics Engineer (Trainee)",
        "overview": "Learn core electronics systems and troubleshooting under supervision.",
        "responsibilities": [
            "Assist in electronic circuit assembly and testing",
            "Support senior engineers in design tasks",
        ],
        "skills": [
            "Basic electronics (diodes, transistors)",
            "Circuit fundamentals",
            "Altium Designer (preferred)",
        ],
    }

    profile = build_jd_profile(raw_data)

    # Check key structure
    assert profile["job_title"] == "Electronics Engineer (Trainee)"
    assert profile["employment_type"] == "Full-time"
    assert profile["experience_required"]["min_years"] == 0
    assert profile["company_info"]["name"] == "Generic Electronics Corporation"

    # Validate against JSON schema
    is_valid, err = validate_jd_profile(profile)
    assert is_valid, f"Validation failed with error: {err}"
