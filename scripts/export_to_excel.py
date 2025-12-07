#!/usr/bin/env python3
"""
Export frontend_data.json to Excel
"""
import pandas as pd
import json
import os

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def main():
    input_file = 'frontend_data.json'
    output_file = 'frontend_data.xlsx'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return
        
    print(f"Reading {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)
        
    # Convert dictionary of dicts to list of dicts
    # data is { "20001": { ... }, "20002": { ... } }
    rows = []
    for zip_code, values in data.items():
        # Flatten nested structures like 'hci' and 'census'
        flat_row = flatten_dict(values)
        rows.append(flat_row)
        
    df = pd.DataFrame(rows)
    
    # Reorder columns to put zipcode first
    if 'zipcode' in df.columns:
        cols = ['zipcode'] + [c for c in df.columns if c != 'zipcode']
        df = df[cols]
        
    print(f"Writing to {output_file}...")
    try:
        df.to_excel(output_file, index=False)
        print(f"✅ Successfully created {output_file}")
    except ImportError:
        print("Error: Missing optional dependency 'openpyxl'. Installing...")
        os.system("pip install openpyxl")
        df.to_excel(output_file, index=False)
        print(f"✅ Successfully created {output_file}")

if __name__ == "__main__":
    main()
