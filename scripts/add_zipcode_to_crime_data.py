import pandas as pd
import numpy as np
import requests
import time
import os
from typing import Optional

def add_zipcode_to_crime_data(csv_file_path: str, output_file_path: str = None):
    """
    Add ZIP Code to crime data using latitude and longitude
    """
    
    df = pd.read_csv(csv_file_path)
    
    print(f"Total records: {len(df)}")
    
    # Initialize ZIP_CODE column if it doesn't exist
    if 'ZIP_CODE' not in df.columns:
        df['ZIP_CODE'] = None
    
    # Load existing output if it exists to resume work
    if output_file_path and os.path.exists(output_file_path):
        print(f"Loading existing progress from {output_file_path}...")
        df_existing = pd.read_csv(output_file_path)
        # Merge existing zipcodes back to main df
        # Assuming CCN is unique identifier
        if 'CCN' in df.columns and 'CCN' in df_existing.columns:
            # Create a map of CCN -> ZIP_CODE
            zip_map = df_existing.set_index('CCN')['ZIP_CODE'].to_dict()
            df['ZIP_CODE'] = df['CCN'].map(zip_map).fillna(df['ZIP_CODE'])
    

    
    # Filter for records that still need processing
    records_to_process = df[df['ZIP_CODE'].isna()]
    print(f"Records remaining to process: {len(records_to_process)}")
    
    if len(records_to_process) == 0:
        print("All records have ZIP codes. Skipping processing.")
        if output_file_path:
             df.to_csv(output_file_path, index=False)
        return df

    # Offline processing is fast, so we can process everything at once
    print(f"Processing all {len(records_to_process)} records using offline database...")
    
    success_count = 0
    
    # Process all records
    for idx, (index, row) in enumerate(records_to_process.iterrows()):
        if idx % 1000 == 0:
            print(f"Progress: {idx}/{len(records_to_process)}")
        
        lat = row['LATITUDE']
        lon = row['LONGITUDE']
        
        zipcode = get_zipcode_from_coordinates(lat, lon)
        
        if zipcode:
            df.at[index, 'ZIP_CODE'] = zipcode
            success_count += 1
        
        # No sleep needed for offline processing
    
    print(f"Successfully processed: {success_count}/{len(records_to_process)} records")
    
    if output_file_path:
        df.to_csv(output_file_path, index=False)
        print(f"Updated results saved to: {output_file_path}")
        
    return df

from uszipcode import SearchEngine

# Initialize SearchEngine (will download database on first run if needed)
search = SearchEngine()

def get_zipcode_from_coordinates(lat: float, lon: float) -> Optional[str]:
    """
    Use uszipcode (offline) to get ZIP Code from coordinates
    """
    try:
        # Search for nearest zipcode within 2 miles
        result = search.by_coordinates(lat, lon, radius=2, returns=1)
        
        if result:
            zipcode = result[0].zipcode
            # Ensure it's a DC zipcode (starts with 20)
            if zipcode and zipcode.startswith('20'):
                return zipcode
            
        return None
        
    except Exception as e:
        # print(f"Error getting zipcode: {e}")
        return None



def main():


    input_file = "DC_Crime_Incidents_in_2025.csv"
    output_file = "DC_Crime_Incidents_in_2025_with_zipcode.csv"
    
    try:
        result_df = add_zipcode_to_crime_data(input_file, output_file)
        
        
    except Exception as e:
        print(f"處理過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
