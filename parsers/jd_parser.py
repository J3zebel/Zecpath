"""
Job Description Parser Module.

Provides functions to clean, split, parse, normalize, and validate job descriptions
against the standard JSON schema.
"""

import os
import re
import json
import logging
from typing import Any, Dict, List, Tuple
import jsonschema

# Try to use the project logger, otherwise fallback to standard logging
try:
    from utils.logger import get_logger

    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# Standard skill taxonomy and their common keywords (in lowercase)
STANDARD_SKILL_TAXONOMY = {
    "PCB Design": [
        "pcb",
        "altium",
        "kicad",
        "eagle",
        "orcad",
        "allegro",
        "gerber",
        "routing",
        "schematic",
        "layout",
        "multi-layer pcb",
        "printed circuit board",
    ],
    "Embedded C/C++": [
        "embedded c",
        "c++",
        "c programming",
        "low-level coding",
        "firmware programming",
    ],
    "Microcontrollers": [
        "microcontroller",
        "microcontrollers",
        "micro-controller",
        "mcu",
        "arduino",
        "stm32",
        "pic",
        "arm",
        "avr",
        "esp32",
        "raspberry pi",
        "msp430",
        "atmel",
    ],
    "Analog Electronics": [
        "analog",
        "diode",
        "diodes",
        "transistor",
        "transistors",
        "op-amp",
        "op-amps",
        "amplifier",
        "amplifiers",
        "filters",
        "oscillator",
        "oscillators",
        "analog circuit",
    ],
    "Digital Electronics": [
        "digital",
        "logic design",
        "boolean",
        "flip-flop",
        "flip-flops",
        "counter",
        "counters",
        "register",
        "registers",
        "combinational",
        "sequential",
        "digital circuit",
    ],
    "Hardware Testing & Troubleshooting": [
        "test equipment",
        "multimeter",
        "oscilloscope",
        "spectrum analyzer",
        "network analyzer",
        "logic analyzer",
        "troubleshoot",
        "troubleshooting",
        "debugging",
        "validation",
        "hardware testing",
        "fault finding",
        "calibration",
    ],
    "IoT & Sensor Integration": [
        "iot",
        "mqtt",
        "coap",
        "ble",
        "bluetooth",
        "wifi",
        "lora",
        "sensor",
        "sensors",
        "actuator",
        "actuators",
        "wireless communication",
        "zigbee",
    ],
    "VLSI & IC Design": [
        "vlsi",
        "asic",
        "ic design",
        "rtl",
        "verilog",
        "vhdl",
        "systemverilog",
        "synthesis",
        "timing analysis",
        "floorplanning",
        "cadence",
        "synopsys",
        "cmos",
        "semiconductor physics",
    ],
    "FPGA Design": ["fpga", "xilinx", "quartus", "vivado", "altera"],
    "MATLAB / Simulink": [
        "matlab",
        "simulink",
        "simulation tools",
        "spice",
        "ltspice",
        "multisim",
        "psim",
        "plecs",
    ],
    "Control Systems": [
        "control system",
        "control systems",
        "control theory",
        "pid",
        "state-space",
        "feedback control",
        "motor control",
        "foc",
    ],
    "Industrial Automation": [
        "plc",
        "scada",
        "modbus",
        "opc",
        "industrial automation",
        "ladder logic",
        "fbd",
        "stl",
        "industrial networking",
        "wonderware",
        "wincc",
        "ignition",
    ],
    "Robotics": [
        "robot",
        "robots",
        "robotics",
        "kinematics",
        "dynamics",
        "robotic arm",
    ],
    "Digital Signal Processing (DSP)": [
        "dsp",
        "signal processing",
        "fourier",
        "filter design",
        "wavelet",
        "noise reduction",
    ],
    "SMT & Soldering": [
        "smt",
        "surface mount",
        "soldering",
        "pick-and-place",
        "reflow",
    ],
    "Semiconductor Technology": [
        "cleanroom",
        "wafer",
        "lithography",
        "etching",
        "doping",
        "fabrication process",
    ],
    "Power & EV Electronics": [
        "power electronics",
        "converter",
        "converters",
        "inverter",
        "inverters",
        "mosfet",
        "igbt",
        "sic",
        "gan",
        "bms",
        "battery",
        "lithium-ion",
        "solar",
        "mppt",
        "ev ",
        "powertrain",
    ],
    "Edge AI / Machine Learning": [
        "machine learning",
        "deep learning",
        "neural network",
        "neural networks",
        "computer vision",
        "tensorflow",
        "pytorch",
        "edge ai",
        "npu",
        "gpu",
        "tpu",
        "parallel computing",
    ],
    "Quantum Electronics": [
        "quantum",
        "cryogenic",
        "qubit",
        "qubits",
        "low-noise circuit",
    ],
    "Neuromorphic Engineering": [
        "neuromorphic",
        "spiking neural",
        "snn",
        "event-driven computing",
    ],
    "Space Electronics": [
        "radiation-hardened",
        "space qualification",
        "satellite",
        "spacecraft",
        "telemetry",
    ],
}

# Standard roles categories
STANDARD_ROLE_CATEGORIES = {
    "Trainee Engineer": [
        "trainee",
        "get",
        "graduate engineer trainee",
        "intern",
        "fresher",
    ],
    "Junior Engineer": ["junior", "jr.", "associate"],
    "Senior Engineer": [
        "senior",
        "sr.",
        "lead",
        "principal",
        "expert",
        "architect",
        "manager",
    ],
    "Academic / Research": [
        "professor",
        "lecturer",
        "scientist",
        "researcher",
        "scholar",
    ],
}


def clean_and_normalize_jd(raw_text: str) -> str:
    """
    Cleans unwanted symbols, noise, formatting issues and normalizes JD text.

    Handles capitalization, bullet points, and spacing.

    Args:
        raw_text: The raw job description text.

    Returns:
        The normalized cleaned text.
    """
    if not raw_text:
        return ""

    # Remove zero-width spaces and other invisible formatting characters
    text = re.sub(r"[\u200b\u200e\u200f\u202a-\u202e]", "", raw_text)

    # Normalize bullet points (•, *, ◦, ▪, etc.) to a standard '-'
    text = re.sub(r"[\u2022\u25E6\u25AA\u2023\u2043\u2219\*]", "-", text)

    # Normalize excessive newlines to double newlines (paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize excessive spaces (excluding leading spaces in layout)
    text = re.sub(r" {2,}", " ", text)

    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue

        # Bullet point standardization
        if stripped.startswith("-"):
            content = stripped[1:].strip()
            if content:
                content = content[0].upper() + content[1:]
            cleaned_lines.append(f"- {content}")
        else:
            # Preserve case layouts but ensure basic formatting
            cleaned_lines.append(stripped)

    # Join back together
    text = "\n".join(cleaned_lines)

    # Deduplicate empty lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_jds(file_content: str) -> List[Tuple[int, str, str]]:
    """
    Splits a consolidated raw text file containing multiple JDs into individual sections.

    Detects job titles starting with a number (e.g. "1. Electronics Engineer (Trainee)").

    Args:
        file_content: Entire content of the job descriptions text file.

    Returns:
        A list of tuples: (index, job_title, jd_text_block).
    """
    # Regex to find lines like "1. Electronics Engineer (Trainee)"
    heading_pattern = re.compile(r"^(\d+)\.\s+(.+)$", re.MULTILINE)

    matches = list(heading_pattern.finditer(file_content))
    jds = []

    for i in range(len(matches)):
        match = matches[i]
        idx = int(match.group(1))
        title = match.group(2).strip()

        start_pos = match.end()
        # End position is the start of the next match, or the end of the file
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(file_content)

        jd_text = file_content[start_pos:end_pos].strip()
        jds.append((idx, title, jd_text))

    return jds


def parse_single_jd(title: str, jd_text: str) -> Dict[str, Any]:
    """
    Parses a single JD text block and extracts structured sections.

    Args:
        title: The job title string (without index prefix).
        jd_text: The body text of the job description.

    Returns:
        A dictionary containing raw extracted fields.
    """
    sections = {"title": title, "overview": "", "responsibilities": [], "skills": []}

    # Clean and normalize the text first
    normalized_text = clean_and_normalize_jd(jd_text)

    # Split text into lines to look for headers
    lines = normalized_text.split("\n")

    current_section = "overview"
    overview_lines = []

    # Common header pattern matchers
    resp_headers = [
        "responsibilities",
        "key responsibilities",
        "what you will do",
        "role description",
    ]
    skills_headers = [
        "required skills",
        "skills required",
        "skills",
        "key skills",
        "what you need",
    ]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if line is a section header
        header_check = re.sub(r"[:\-\_\s]+$", "", stripped.lower()).strip()

        if header_check in resp_headers:
            current_section = "responsibilities"
            continue
        elif header_check in skills_headers:
            current_section = "skills"
            continue
        elif header_check == "job overview":
            current_section = "overview"
            continue

        # Append content based on current section
        if current_section == "overview":
            overview_lines.append(stripped)
        elif current_section == "responsibilities":
            # Extract bullet point text or add raw text
            if stripped.startswith("-"):
                sections["responsibilities"].append(stripped[1:].strip())
            else:
                sections["responsibilities"].append(stripped)
        elif current_section == "skills":
            if stripped.startswith("-"):
                sections["skills"].append(stripped[1:].strip())
            else:
                sections["skills"].append(stripped)

    sections["overview"] = " ".join(overview_lines).strip()
    return sections


def detect_skill_synonyms(raw_skill: str) -> str:
    """
    Maps a raw skill description to its standardized name in our taxonomy.

    Args:
        raw_skill: The raw skill string from the JD (e.g. "Altium Designer").

    Returns:
        The standardized skill name if found, otherwise the normalized raw skill.
    """
    cleaned = raw_skill.lower()

    for std_name, keywords in STANDARD_SKILL_TAXONOMY.items():
        for kw in keywords:
            # If the keyword is purely alphanumeric, use word boundaries
            if re.match(r"^\w+$", kw):
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, cleaned):
                    return std_name
            else:
                # For special characters like C++, Analog & Digital, etc.
                if kw in cleaned:
                    return std_name

    # Clean up the original text casing for pass-through
    core_original = re.sub(r"\(.*?\)", "", raw_skill).strip()
    core_original = re.sub(r"[\s\-+/,]+$", "", core_original).strip()
    return core_original if core_original else raw_skill


def normalize_skills(
    raw_skills: List[str], seniority_level: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Separates skills into mandatory and preferred, and standardizes them.

    Args:
        raw_skills: The list of raw skills extracted from the JD.
        seniority_level: The inferred seniority level of the role (e.g. Beginner, Intermediate, Advanced).

    Returns:
        A tuple of (mandatory_skills_list, preferred_skills_list).
    """
    mandatory = []
    preferred = []

    # Set default skill level based on seniority
    skill_level = "Intermediate"
    if seniority_level == "Beginner":
        skill_level = "Beginner"
    elif seniority_level in ["Advanced", "Expert"]:
        skill_level = "Advanced"

    seen_mandatory = set()
    seen_preferred = set()

    for skill_text in raw_skills:
        # Check if the skill mentions "preferred", "optional", or similar
        is_preferred = False
        lower_skill = skill_text.lower()

        if (
            "prefer" in lower_skill
            or "option" in lower_skill
            or "nice to have" in lower_skill
        ):
            is_preferred = True

        std_name = detect_skill_synonyms(skill_text)

        # If it's preferred
        if is_preferred:
            if std_name not in seen_preferred:
                preferred.append({"name": std_name, "level": skill_level})
                seen_preferred.add(std_name)
        else:
            # Check if there are specific preferred tools listed in parentheses
            # E.g. "PCB design software (Altium, KiCad, Eagle - preferred)"
            # Extract Altium, KiCad, Eagle as preferred skills, and PCB Design as mandatory
            paren_match = re.search(r"\((.*?)\)", skill_text)
            if paren_match:
                inner_text = paren_match.group(1).lower()
                if "prefer" in inner_text or "option" in inner_text:
                    # Clean the parenthesized list
                    clean_inner = re.sub(
                        r"\-?\s*(preferred|optional|nice to have)", "", inner_text
                    ).strip()
                    tools = [
                        t.strip() for t in re.split(r"[,/|]", clean_inner) if t.strip()
                    ]
                    for tool in tools:
                        std_tool = detect_skill_synonyms(tool)
                        if std_tool not in seen_preferred and std_tool != std_name:
                            preferred.append({"name": std_tool, "level": skill_level})
                            seen_preferred.add(std_tool)

            if std_name not in seen_mandatory:
                # Inferred years of experience for mandatory skills is 0 for beginners,
                # 2 for intermediate, 5 for advanced
                yoe = 0
                if skill_level == "Intermediate":
                    yoe = 2
                elif skill_level == "Advanced":
                    yoe = 5

                mandatory.append(
                    {"name": std_name, "level": skill_level, "years_of_experience": yoe}
                )
                seen_mandatory.add(std_name)

    return mandatory, preferred


def infer_experience_and_education(
    title: str,
) -> Tuple[Dict[str, Any], List[str], str, str]:
    """
    Infers experience, education requirements, seniority, and employment type from title.

    Args:
        title: The job title.

    Returns:
        A tuple of (experience_required_dict, education_requirements_list, seniority_level, employment_type).
    """
    lower_title = title.lower()

    # 1. Seniority & Experience
    seniority = "Intermediate"
    employment_type = "Full-time"
    min_years = 2
    max_years = 5

    if any(
        k in lower_title
        for k in ["trainee", "get", "fresh", "graduate", "intern", "apprentice"]
    ):
        seniority = "Beginner"
        min_years = 0
        max_years = 1
        if "intern" in lower_title:
            employment_type = "Internship"
        else:
            employment_type = "Full-time"  # Trainees are typically full-time
    elif any(k in lower_title for k in ["junior", "jr.", "associate"]):
        seniority = "Beginner"
        min_years = 1
        max_years = 3
    elif any(
        k in lower_title for k in ["scientist", "research", "professor", "lecturer"]
    ):
        seniority = "Advanced"
        min_years = 5
        max_years = 10
    elif any(
        k in lower_title
        for k in ["senior", "sr.", "lead", "principal", "architect", "manager", "head"]
    ):
        seniority = "Advanced"
        min_years = 5
        max_years = 8
        if any(
            k in lower_title
            for k in ["lead", "principal", "architect", "manager", "head"]
        ):
            seniority = "Expert"
            min_years = 8
            max_years = 12
    elif "freelance" in lower_title or "consultant" in lower_title:
        employment_type = "Contract"
        min_years = 5
        max_years = 10
        seniority = "Advanced"

    experience_required = {"min_years": min_years, "max_years": max_years}

    # 2. Education Requirements
    education = []
    if any(
        k in lower_title for k in ["research", "quantum", "neuromorphic", "scientist"]
    ):
        education.append(
            "Master's or Ph.D. in Electronics Engineering, Physics, "
            "or a closely related quantitative field."
        )
    elif any(k in lower_title for k in ["trainee", "get", "graduate"]):
        education.append(
            "Bachelor of Engineering (B.E.) or Bachelor of Technology "
            "(B.Tech.) in Electronics & Communication, Electrical "
            "Engineering, or related discipline."
        )
    else:
        education.append(
            "Bachelor's degree in Electronics Engineering, Electrical "
            "Engineering, Computer Science, or a related technical field."
        )

    return experience_required, education, seniority, employment_type


def infer_salary_and_benefits(
    title: str, seniority: str
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Infers realistic salary range and benefits based on the role and seniority.

    Args:
        title: The job title.
        seniority: The inferred seniority level.

    Returns:
        A tuple of (salary_range_dict, benefits_list).
    """
    # Default benefits
    benefits = [
        "Health Insurance",
        "Paid Time Off (PTO)",
        "Professional Development Assistance",
    ]

    # Salary in USD (default in schema)
    salary_range = {"min": 80000, "max": 120000, "currency": "USD", "period": "Yearly"}

    if seniority == "Beginner":
        salary_range["min"] = 35000
        salary_range["max"] = 55000
        benefits.append("Mentorship & Training Programs")
    elif seniority == "Intermediate":
        salary_range["min"] = 65000
        salary_range["max"] = 95000
        benefits.append("Performance Bonus")
    elif seniority == "Advanced":
        salary_range["min"] = 100000
        salary_range["max"] = 140000
        benefits.extend(["Performance Bonus", "Retirement Matching (401k)"])
    elif seniority == "Expert":
        salary_range["min"] = 135000
        salary_range["max"] = 180000
        benefits.extend(
            ["Performance Bonus", "Retirement Matching (401k)", "Flexible Schedule"]
        )

    # Adjust for consulting/freelance
    if "consultant" in title.lower() or "freelance" in title.lower():
        salary_range["min"] = 50
        salary_range["max"] = 100
        salary_range["period"] = "Hourly"
        benefits = ["Flexible Working Hours", "Remote Work Options"]

    return salary_range, benefits


def build_jd_profile(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assembles extracted raw data into a structured Job Profile.

    Matches schemas/jd_schema.json structure.

    Args:
        raw_data: Raw parsed sections from parse_single_jd.

    Returns:
        A dictionary compliant with the JD schema.
    """
    title = raw_data["title"]

    # 1. Infer Experience, Education, Seniority and Employment Type
    exp_required, edu_reqs, seniority, emp_type = infer_experience_and_education(title)

    # 2. Extract and Normalize Skills
    mandatory_skills, preferred_skills = normalize_skills(raw_data["skills"], seniority)

    # 3. Infer Salary and Benefits
    salary, benefits = infer_salary_and_benefits(title, seniority)

    # 4. Construct the structured job profile object
    profile = {
        "job_title": title,
        "company_info": {
            "name": "Generic Electronics Corporation",
            "industry": "Semiconductors & Electronics Manufacturing",
            "description": "A pioneering engineering firm specializing in advanced electronic design and systems.",
        },
        "location": {
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "is_remote": False,
            "remote_type": "On-site",
        },
        "employment_type": emp_type,
        "experience_required": exp_required,
        "responsibilities": raw_data["responsibilities"],
        "mandatory_skills": mandatory_skills,
        "preferred_skills": preferred_skills,
        "education_requirements": edu_reqs,
        "salary_range": salary,
        "benefits": benefits,
    }

    # Remote variations
    if "remote" in title.lower():
        profile["location"]["is_remote"] = True
        profile["location"]["remote_type"] = "Fully Remote"
    elif "hybrid" in title.lower():
        profile["location"]["is_remote"] = True
        profile["location"]["remote_type"] = "Hybrid"

    # If the job description overview explicitly mentions remote
    if "remote" in raw_data["overview"].lower():
        profile["location"]["is_remote"] = True
        profile["location"]["remote_type"] = "Fully Remote"

    return profile


def validate_jd_profile(
    profile: Dict[str, Any], schema_path: str = None
) -> Tuple[bool, str]:
    """
    Validates a structured Job Profile dictionary against the JD JSON schema.

    Args:
        profile: The structured Job Profile dictionary.
        schema_path: Optional path to schemas/jd_schema.json. If None, it will be resolved.

    Returns:
        A tuple of (is_valid: bool, error_message: str).
    """
    if not schema_path:
        # Resolve path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, "..", "schemas", "jd_schema.json")

    if not os.path.exists(schema_path):
        return False, f"Schema file not found at {schema_path}"

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        jsonschema.validate(instance=profile, schema=schema)
        return True, ""
    except jsonschema.exceptions.ValidationError as ve:
        logger.error(
            f"Schema validation failed for '{profile.get('job_title')}': {str(ve)}"
        )
        return False, str(ve)
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        return False, str(e)
