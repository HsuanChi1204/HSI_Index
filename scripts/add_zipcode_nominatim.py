#!/usr/bin/env python3
"""
Add ZIP Code to crime data using Nominatim API (Online)
Based on scripts/batch_process_zipcode.py
"""
import pandas as pd
import requests
import time
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Tuple

def get_zipcode_from_api(lat: float, lon: float) -> Dict:
    """
    Use Nominatim API to get ZIP Code
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {'User-Agent': 'DC_Crime_Analysis_Tool/1.0'}
        
        # Nominatim requires 1 second between requests
        time.sleep(1.0)
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            postcode = address.get('postcode')
            
            # Clean postcode (sometimes it has suffix like 20001-1234)
            if postcode:
                postcode = postcode.split('-')[0]
            
            if postcode and postcode.startswith('20') and len(postcode) == 5:
                return {
                    'success': True,
                    'zipcode': postcode,
                    'city': address.get('city', ''),
                    'state': address.get('state', ''),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'zipcode': None,
                    'city': None,
                    'state': None,
                    'error': f'Non-DC ZIP: {postcode}'
                }
        else:
            return {
                'success': False,
                'zipcode': None,
                'city': None,
                'state': None,
                'error': f'HTTP {response.status_code}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'zipcode': None,
            'city': None,
            'state': None,
            'error': str(e)
        }

def process_batch(df: pd.DataFrame, batch_indices: list) -> Tuple[int, int]:
    """
    Process a batch of records
    """
    success_count = 0
    failed_count = 0
    
    for i, idx in enumerate(batch_indices):
        row = df.loc[idx]
        lat = row['LATITUDE']
        lon = row['LONGITUDE']
        
        print(f"  Processing {i+1}/{len(batch_indices)}: Record {idx}...", end='\r')
        
        try:
            result = get_zipcode_from_api(lat, lon)
            
            if result['success']:
                df.at[idx, 'ZIP_CODE'] = result['zipcode']
                df.at[idx, 'CITY'] = result['city']
                df.at[idx, 'STATE'] = result['state']
                df.at[idx, 'PROCESSING_STATUS'] = 'success'
                df.at[idx, 'PROCESSING_ERROR'] = None
                success_count += 1
                # print(f"    ✅ Success: {result['zipcode']}")
            else:
                df.at[idx, 'PROCESSING_STATUS'] = 'failed'
                df.at[idx, 'PROCESSING_ERROR'] = result['error']
                failed_count += 1
                # print(f"    ❌ Failed: {result['error']}")
                
        except Exception as e:
            df.at[idx, 'PROCESSING_STATUS'] = 'failed'
            df.at[idx, 'PROCESSING_ERROR'] = str(e)
            failed_count += 1
            # print(f"    ❌ Error: {e}")
            
    print(f"  Batch complete. Success: {success_count}, Failed: {failed_count}        ")
    return success_count, failed_count

def main():
    input_file = "DC_Crime_Incidents_in_2025.csv"
    output_file = "DC_Crime_Incidents_in_2025_with_zipcode_nominatim.csv"
    batch_size = 50 # Smaller batch size for frequent saving
    
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    # Check if output file exists to resume
    if os.path.exists(output_file):
        print(f"Resuming from {output_file}...")
        df = pd.read_csv(output_file)
        
        # Ensure columns exist
        if 'PROCESSING_STATUS' not in df.columns:
            df['PROCESSING_STATUS'] = 'pending'
    else:
        print("Starting fresh...")
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found.")
            return
            
        df = pd.read_csv(input_file)
        df['ZIP_CODE'] = None
        df['CITY'] = None
        df['STATE'] = None
        df['PROCESSING_STATUS'] = 'pending'
        df['PROCESSING_ERROR'] = None
    
    # Filter for pending records
    mask = (df['LATITUDE'].notna()) & (df['LONGITUDE'].notna()) & (df['PROCESSING_STATUS'] != 'success')
    pending_records = df[mask]
    
    total_records = len(df)
    remaining = len(pending_records)
    
    print(f"Total Records: {total_records}")
    print(f"Remaining: {remaining}")
    
    if remaining == 0:
        print("All records processed!")
        return

    # Process in batches
    total_success = 0
    total_failed = 0
    
    for batch_start in range(0, remaining, batch_size):
        batch_end = min(batch_start + batch_size, remaining)
        batch_records = pending_records.iloc[batch_start:batch_end]
        batch_indices = batch_records.index.tolist()
        
        print(f"\nBatch {batch_start // batch_size + 1}: Records {batch_start + 1} to {batch_end} (of {remaining})")
        
        s, f = process_batch(df, batch_indices)
        total_success += s
        total_failed += f
        
        # Save progress
        df.to_csv(output_file, index=False)
        print(f"✅ Saved progress to {output_file}")
        
    print("\n=== Processing Complete ===")
    print(f"Total Success: {total_success}")
    print(f"Total Failed: {total_failed}")

if __name__ == "__main__":
    main()
