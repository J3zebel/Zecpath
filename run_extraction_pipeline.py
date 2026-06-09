import os
import sys
import time
import json
import datetime
import traceback
import shutil
from parsers.extractor import extract_resume
from utils.logger import get_logger

logger = get_logger("extraction_pipeline")

def run_pipeline():
    start_time = time.time()
    input_dir = os.path.join("data", "resumes")
    output_dir = os.path.join("data", "processed")
    json_output_dir = os.path.join("data", "json")
    
    if not os.path.exists(input_dir):
        logger.error(f"Input directory does not exist: {input_dir}")
        print(f"Error: Input directory '{input_dir}' not found.")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(json_output_dir, exist_ok=True)
    
    # Get all PDF and DOCX files in the resumes directory
    all_files = [f for f in os.listdir(input_dir) if os.path.splitext(f)[1].lower() in ['.pdf', '.docx']]
    
    if not all_files:
        logger.warning(f"No PDF or DOCX resumes found in {input_dir}")
        print(f"No PDF or DOCX files found in {input_dir}")
        return
        
    print(f"Found {len(all_files)} resumes to process in '{input_dir}'.")
    logger.info(f"Starting pipeline execution for {len(all_files)} files.")
    
    results = []
    success_count = 0
    
    for filename in all_files:
        filepath = os.path.join(input_dir, filename)
        file_ext = os.path.splitext(filename)[1].lower()
        file_size = os.path.getsize(filepath)
        
        print(f"Processing: {filename}...", end="", flush=True)
        file_start = time.time()
        
        try:
            cleaned_text = extract_resume(filepath, output_dir=output_dir, json_output_dir=json_output_dir)
            duration = time.time() - file_start
            word_count = len(cleaned_text.split())
            char_count = len(cleaned_text)
            
            # Find the structured JSON file to check extracted sections
            prefix = os.path.splitext(filename)[0]
            json_file = os.path.join(json_output_dir, f"{prefix}_structured.json")
            sections_list = []
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sections_list = list(data.get("sections", {}).keys())
            
            results.append({
                "filename": filename,
                "status": "SUCCESS",
                "format": file_ext,
                "file_size_bytes": file_size,
                "duration_seconds": round(duration, 3),
                "word_count": word_count,
                "char_count": char_count,
                "sections_found": sections_list
            })
            success_count += 1
            print(f" SUCCESS in {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - file_start
            err_msg = str(e)
            logger.error(f"Failed to process {filename}: {err_msg}\n{traceback.format_exc()}")
            results.append({
                "filename": filename,
                "status": "FAILED",
                "format": file_ext,
                "file_size_bytes": file_size,
                "duration_seconds": round(duration, 3),
                "error": err_msg
            })
            print(f" FAILED in {duration:.2f}s - Error: {err_msg}")
            
    total_duration = time.time() - start_time
    success_rate = (success_count / len(all_files)) * 100
    
    summary = {
        "execution_summary": {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "total_files": len(all_files),
            "successful_runs": success_count,
            "failed_runs": len(all_files) - success_count,
            "success_rate_percent": round(success_rate, 2),
            "total_duration_seconds": round(total_duration, 3),
        },
        "file_details": results
    }
    
    # Save the execution report
    report_file = os.path.join(json_output_dir, "extraction_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Pipeline finished. Success rate: {success_rate:.2f}%. Report saved to {report_file}")
    
    # Print final console summary report
    print("\n" + "="*50)
    print("EXTRACTION PIPELINE SUMMARY")
    print("="*50)
    print(f"Total Files Processed: {len(all_files)}")
    print(f"Successful Parsed:    {success_count}")
    print(f"Failed Runs:          {len(all_files) - success_count}")
    print(f"Success Rate:         {success_rate:.2f}%")
    print(f"Total Duration:       {total_duration:.2f}s")
    print(f"Report JSON Saved:    {report_file}")
    print("="*50)

if __name__ == "__main__":
    run_pipeline()

