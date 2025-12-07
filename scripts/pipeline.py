#!/usr/bin/env python3
"""
Data Automation Pipeline
Orchestrates the flow: Ingest -> Process -> Upload -> Export
"""
import os
import sys
import argparse
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_step(step_name, command):
    """Run a shell command and check for errors"""
    logger.info(f"Starting step: {step_name}")
    exit_code = os.system(command)
    if exit_code != 0:
        logger.error(f"Step failed: {step_name}")
        sys.exit(exit_code)
    logger.info(f"Step completed: {step_name}")

def main():
    parser = argparse.ArgumentParser(description="DC Crime & Zillow Data Pipeline")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip data ingestion/processing")
    parser.add_argument("--skip-upload", action="store_true", help="Skip uploading to Supabase")
    parser.add_argument("--export-json", action="store_true", help="Export JSON after processing")
    args = parser.parse_args()

    logger.info("Starting Data Pipeline")

    # 1. Process Crime Data (Add Zipcodes)
    if not args.skip_ingest:
        # Assuming the input file is standard, or we could make this configurable
        # For now, we use the existing script's default or pass arguments if needed
        # We need to ensure the input file exists. 
        # In a real scenario, we might scan for new CSVs.
        # For this MVP, we'll run the existing script.
        run_step("Add Zipcodes to Crime Data", f"{sys.executable} scripts/add_zipcode_to_crime_data.py")

    # 2. Upload to Supabase
    if not args.skip_upload:
        run_step("Upload to Supabase", f"{sys.executable} scripts/upload_to_supabase.py")

    # 3. Export JSON (Optional, for backward compatibility)
    if args.export_json:
        run_step("Export JSON", f"{sys.executable} scripts/combine_data_to_json.py")

    logger.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
