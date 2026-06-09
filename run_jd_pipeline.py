"""
Job Description Parsing Pipeline Orchestrator.

Splits consolidated job description files into individual .txt files in data/jds txt files/,
then parses each individual text file into structured validated JSON profiles in data/jd json file/.
"""

import os
import re
import sys
import json

# Try to use the project logger, otherwise fallback to standard logging
try:
    from utils.logger import get_logger

    logger = get_logger("jd_parsing_pipeline")
except ImportError:
    import logging

    logger = logging.getLogger("jd_parsing_pipeline")

from parsers.jd_parser import (
    split_jds,
    parse_single_jd,
    build_jd_profile,
    validate_jd_profile,
)


def slugify(text: str) -> str:
    """
    Converts a job title to a safe slug format for filenames.

    Args:
        text: The job title.

    Returns:
        A safe filename string.
    """
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "_", s)
    return s.strip("_")


def clean_old_files():
    """
    Removes any old report files or old output directories.
    """
    # Delete jd_parsing_report.json if it exists anywhere
    paths_to_delete = [
        os.path.join("data", "json", "jd_parsing_report.json"),
        os.path.join("data", "json", "jds", "jd_parsing_report.json"),
        os.path.join("data", "jd_parsing_report.json"),
    ]
    for p in paths_to_delete:
        if os.path.exists(p):
            try:
                os.remove(p)
                logger.info(f"Removed old report file: {p}")
            except Exception as e:
                logger.error(f"Could not delete old report file {p}: {str(e)}")


def run_pipeline():
    """
    Orchestrates splitting JDs into TXT files, then converting them to JSON files.
    """
    clean_old_files()

    input_dir = os.path.join("data", "jds")
    txt_output_dir = os.path.join("data", "jds txt files")
    json_output_dir = os.path.join("data", "jd json file")

    if not os.path.exists(input_dir):
        logger.error(f"Input directory does not exist: {input_dir}")
        print(f"Error: Input directory '{input_dir}' not found.")
        sys.exit(1)

    os.makedirs(txt_output_dir, exist_ok=True)
    os.makedirs(json_output_dir, exist_ok=True)

    # 1. SCAN AND SPLIT INPUT FILES INTO INDIVIDUAL TXT FILES
    all_consolidated_files = [
        f for f in os.listdir(input_dir) if os.path.splitext(f)[1].lower() == ".txt"
    ]

    if not all_consolidated_files:
        logger.warning(f"No text job descriptions found in {input_dir}")
        print(f"No text files found in {input_dir}")
        return

    print(f"Step 1: Splitting consolidated JDs from '{input_dir}'...")
    logger.info(f"Found {len(all_consolidated_files)} consolidated JD files to split.")

    txt_files_created = 0

    for filename in all_consolidated_files:
        filepath = os.path.join(input_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            jd_blocks = split_jds(content)
            for idx, title, jd_text in jd_blocks:
                clean_title = slugify(title)
                txt_filename = f"{idx}_{clean_title}.txt"
                txt_filepath = os.path.join(txt_output_dir, txt_filename)

                # Write the individual text file (Title on line 1, then content body)
                with open(txt_filepath, "w", encoding="utf-8") as txt_f:
                    txt_f.write(f"{title}\n\n{jd_text}")
                txt_files_created += 1

        except Exception as e:
            logger.error(f"Error splitting consolidated file {filename}: {str(e)}")
            print(f"Error splitting consolidated file {filename}: {str(e)}")

    print(
        f"Successfully generated {txt_files_created} individual JD text files in '{txt_output_dir}'."
    )
    logger.info(f"Generated {txt_files_created} text files in {txt_output_dir}.")

    # 2. READ EACH TXT FILE AND GENERATE CORRESPONDING JSON FILES
    all_individual_txts = [
        f
        for f in os.listdir(txt_output_dir)
        if os.path.splitext(f)[1].lower() == ".txt"
    ]

    print("\nStep 2: Converting individual JD text files into JSON profiles...")
    logger.info(f"Converting {len(all_individual_txts)} individual text files to JSON.")

    json_files_created = 0
    failed_conversions = 0

    for txt_filename in all_individual_txts:
        txt_filepath = os.path.join(txt_output_dir, txt_filename)
        prefix = os.path.splitext(txt_filename)[0]
        json_filename = f"{prefix}.json"
        json_filepath = os.path.join(json_output_dir, json_filename)

        try:
            with open(txt_filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                raise ValueError("Text file is empty")

            # Extract title from the first line
            title = lines[0].strip()
            # The remaining lines are the JD body
            jd_text = "".join(lines[1:]).strip()

            # Parse the individual JD content
            raw_data = parse_single_jd(title, jd_text)
            profile = build_jd_profile(raw_data)

            # Validate structured profile
            is_valid, validation_err = validate_jd_profile(profile)
            if not is_valid:
                raise ValueError(f"Schema validation failed: {validation_err}")

            # Save structured JSON profile
            with open(json_filepath, "w", encoding="utf-8") as out_f:
                json.dump(profile, out_f, indent=2, ensure_ascii=False)
            json_files_created += 1

        except Exception as e:
            failed_conversions += 1
            logger.error(f"Failed to convert {txt_filename} to JSON: {str(e)}")
            print(f"Error converting {txt_filename}: {str(e)}")

    print("\n" + "=" * 50)
    print("JOB DESCRIPTION REFACTORED PIPELINE SUMMARY")
    print("=" * 50)
    print(f"Consolidated Files Read:      {len(all_consolidated_files)}")
    print(f"Individual TXT Files Created: {txt_files_created}")
    print(f"Individual JSON Files Created: {json_files_created}")
    print(f"Failed Conversions:           {failed_conversions}")
    success_rate = (json_files_created / txt_files_created * 100) if txt_files_created > 0 else 0.0
    print(f"Success Rate:                 {success_rate:.2f}%")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()
