#!/usr/bin/env python3
"""
Unified Data Processing Script
Consolidates data loading, index calculation (HCI & Legacy), and JSON generation.
"""
import pandas as pd
import numpy as np
import json
import argparse
import os
import sys
from typing import Dict, List, Optional

# Add parent directory to path to allow imports from scripts.lib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.lib import hci, indices, loader

def load_crime_data(file_path: str) -> pd.DataFrame:
    print(f"Loading Crime Data: {file_path}")
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return pd.DataFrame()
    return pd.read_csv(file_path)

def load_zillow_data(file_path: str) -> pd.DataFrame:
    print(f"Loading Zillow Data: {file_path}")
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return pd.DataFrame()
    return pd.read_csv(file_path)

def process_zillow_data(zillow_df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Process Zillow data.
    Returns a dictionary keyed by ZIP code.
    """
    print("Processing Zillow Data...")
    if zillow_df.empty:
        return {}

    zillow_data = {}
    
    # Ensure ZIPCode is string
    if 'ZIPCode' in zillow_df.columns:
        zillow_df['ZIPCode'] = zillow_df['ZIPCode'].astype(str)
        
    for _, row in zillow_df.iterrows():
        zip_code = str(row['ZIPCode'])
        
        # Extract pre-calculated metrics
        mom = float(row['MOM']) if 'MOM' in row and pd.notna(row['MOM']) else None
        yoy = float(row['YOY']) if 'YOY' in row and pd.notna(row['YOY']) else None
        price = float(row['CurrentPrice']) if 'CurrentPrice' in row and pd.notna(row['CurrentPrice']) else None
        
        zillow_data[zip_code] = {
            'current_price': price,
            'mom': mom,
            'yoy': yoy,
            'region_name': row.get('RegionName'),
            'state': row.get('State'),
            'metro': row.get('Metro'),
            'county_name': row.get('CountyName')
        }
        
    return zillow_data

def main():
    parser = argparse.ArgumentParser(description="Process DC Crime & Zillow Data")
    parser.add_argument("--crime-csv", default="DC_Crime_Incidents_in_2025_with_zipcode.csv", help="Path to Crime CSV")
    parser.add_argument("--zillow-csv", default="dc_zillow_2025_09_30.csv", help="Path to Zillow CSV")
    parser.add_argument("--housets-census-csv", default="HouseTS.csv", help="Path to HouseTS CSV")
    parser.add_argument("--output", default="dc_crime_zillow_combined.json", help="Output JSON file")
    parser.add_argument("--frontend-output", default="frontend_data.json", help="Frontend JSON file")
    args = parser.parse_args()

    # 1. Load Data
    crime_df = load_crime_data(args.crime_csv)
    zillow_raw_df = load_zillow_data(args.zillow_csv)
    
    # Load HouseTS and extract Census
    dc_zip_codes = None
    if not crime_df.empty and 'ZIP_CODE' in crime_df.columns:
        # Ensure ZIP_CODE is string and handle float/int conversion
        crime_df['ZIP_CODE'] = pd.to_numeric(crime_df['ZIP_CODE'], errors='coerce')
        crime_df = crime_df.dropna(subset=['ZIP_CODE'])
        crime_df['ZIP_CODE'] = crime_df['ZIP_CODE'].astype(int).astype(str)
        dc_zip_codes = crime_df['ZIP_CODE'].unique().tolist()
    
    housets_df = loader.load_housets_csv(args.housets_census_csv, dc_zip_codes=dc_zip_codes)
    census_data = loader.extract_latest_census_data(housets_df)
    
    # Fallback for missing census data (e.g., 20024)
    from uszipcode import SearchEngine
    search = SearchEngine()
    
    for zip_code in dc_zip_codes:
        if zip_code not in census_data or not census_data[zip_code].get('total_population'):
            print(f"⚠️ Missing Census Data for {zip_code}. Attempting fallback with uszipcode...")
            z = search.by_zipcode(zip_code)
            if z:
                # uszipcode SimpleZipcode object attributes
                # Note: It does not have median_rent or per_capita_income in the simple db
                census_data[zip_code] = {
                    'total_population': z.population,
                    'median_home_value': z.median_home_value,
                    'median_rent': None, # Not available in simple db
                    'per_capita_income': None, # Not available in simple db
                    'median_income': z.median_household_income,
                    # Add other fields as needed or leave None
                    'poverty_rate': None,
                    'unemployment_rate': None
                }
                print(f"   ✅ Recovered {zip_code}: Pop={z.population}")
            else:
                print(f"   ❌ Failed to recover {zip_code}")

    census_summary = loader.get_census_data_summary(census_data)

    # 2. Process Data
    # Zillow
    zillow_data = process_zillow_data(zillow_raw_df)
    
    # Crime Stats Aggregation
    print("Aggregating Crime Stats...")
    crime_stats = {}
    if not crime_df.empty:
        # Group by ZIP_CODE
        grouped = crime_df.groupby('ZIP_CODE')
        
        for zip_code, group in grouped:
            zip_str = str(zip_code)
            
            # Total Crimes
            total = len(group)
            
            # By Offense
            by_offense = group['OFFENSE'].value_counts().to_dict()
            
            # By Shift
            by_shift = group['SHIFT'].value_counts().to_dict()
            
            # By Ward
            by_ward = group['WARD'].value_counts().to_dict()
            # Convert ward keys to string if needed
            by_ward = {str(k): v for k, v in by_ward.items()}
            
            crime_stats[zip_str] = {
                'total_crimes': total,
                'by_offense': by_offense,
                'by_shift': by_shift,
                'by_ward': by_ward
            }

    # 3. Calculate Statistics for Normalization
    # Collect all values to find min/max/percentiles
    crime_values = [s['total_crimes'] for s in crime_stats.values()]
    mom_values = [d['mom'] for d in zillow_data.values() if d['mom'] is not None]
    yoy_values = [d['yoy'] for d in zillow_data.values() if d['yoy'] is not None]
    prices = [d['current_price'] for d in zillow_data.values() if d['current_price'] is not None]
    
    # Calculate Crime Rate (per 1000) for normalization
    crime_rates = []
    for zip_code, stats in crime_stats.items():
        pop = census_data.get(zip_code, {}).get('total_population')
        if pop and pop > 0:
            rate = (stats['total_crimes'] / pop) * 1000
            crime_rates.append(rate)
            
    # Tukey's IQR Method for Threshold
    if crime_rates:
        q1 = np.percentile(crime_rates, 25)
        q3 = np.percentile(crime_rates, 75)
        iqr = q3 - q1
        upper_cap = q3 + 1.5 * iqr
        
        # Winsorization (Clipping)
        # Instead of dropping, we cap the values at upper_cap for normalization purposes
        clipped_rates = [min(r, upper_cap) for r in crime_rates]
        
        min_rate = min(clipped_rates)
        max_rate = max(clipped_rates) # This will be upper_cap if any value was clipped
    else:
        min_rate = 0
        max_rate = 0
        upper_cap = 0

    stats = {
        'min_crime_count': min(crime_values) if crime_values else 0,
        'max_crime_count': max(crime_values) if crime_values else 0,
        'min_mom': min(mom_values) if mom_values else -0.1,
        'max_mom': max(mom_values) if mom_values else 0.1,
        'min_yoy': min(yoy_values) if yoy_values else -0.1,
        'max_yoy': max(yoy_values) if yoy_values else 0.1,
        'min_crime_rate': min_rate,
        'max_crime_rate': max_rate,
        'min_price': min(prices) if prices else 0,
        'max_price': max(prices) if prices else 0,
        # Store the ceiling for reference
        'crime_ceiling': float(upper_cap)
    }
    
    print("\nStatistics:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # 4. Build Combined Data
    combined_data = {}
    all_zips = set(crime_stats.keys()) | set(zillow_data.keys()) | set(census_data.keys())
    
    for zip_code in all_zips:
        # Basic Data
        c_stats = crime_stats.get(zip_code, {
            'total_crimes': 0,
            'by_offense': {},
            'by_shift': {},
            'by_ward': {}
        })
        z_data = zillow_data.get(zip_code, {})
        cen_data = census_data.get(zip_code, {})
        
        # Prepare data for HCI calculation
        calc_data = {
            'mom': z_data.get('mom'),
            'yoy': z_data.get('yoy'),
            'crime_count': c_stats['total_crimes'],
            'population': cen_data.get('total_population')
        }
        
        # Calculate HCI
        hci_result = hci.calculate_hci_with_custom_weights(
            zip_data=calc_data,
            ranges=stats,
            w1=0.5,
            w2=0.5,
            alpha=0.5
        )
        
        # Calculate Legacy Indices
        legacy_indices = indices.calculate_composite_index(
            crime_count=c_stats['total_crimes'],
            price=z_data.get('current_price'),
            min_crimes=stats['min_crime_count'],
            max_crimes=stats['max_crime_count'],
            min_price=stats['min_price'],
            max_price=stats['max_price']
        )
        
        # Structure matching user request
        combined_data[zip_code] = {
            'zip_code': zip_code,
            'zillow_data': z_data,
            'census_data': cen_data,
            'crime_stats': c_stats,
            'indices': legacy_indices,
            'hci': {
                'default': hci_result,
                'ranges': {
                    'min_mom': stats['min_mom'],
                    'max_mom': stats['max_mom'],
                    'min_yoy': stats['min_yoy'],
                    'max_yoy': stats['max_yoy'],
                    'min_crime_count': stats['min_crime_count'],
                    'max_crime_count': stats['max_crime_count'],
                    'min_crime_rate': stats['min_crime_rate'],
                    'max_crime_rate': stats['max_crime_rate']
                }
            }
        }

    # 5. Save Main JSON
    output_data = {
        'metadata': {
            'generated_at': pd.Timestamp.now().isoformat(),
            'total_zipcodes': len(combined_data),
            'total_crimes': len(crime_df),
            'total_zillow_records': len(zillow_data),
            'total_census_records': len(census_data),
            'index_ranges': {
                'crime_range': {
                    'min': int(stats['min_crime_count']),
                    'max': int(stats['max_crime_count'])
                },
                'price_range': {
                    'min': float(stats['min_price']),
                    'max': float(stats['max_price'])
                },
                'mom_range': {
                    'min': float(stats['min_mom']),
                    'max': float(stats['max_mom'])
                },
                'yoy_range': {
                    'min': float(stats['min_yoy']),
                    'max': float(stats['max_yoy'])
                },
                'crime_rate_range': {
                    'min': float(stats['min_crime_rate']),
                    'max': float(stats['max_crime_rate'])
                }
            },
            'census_summary': census_summary
        },
        'data': combined_data
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"\nSaved combined data to {args.output}")
    
    # 6. Generate Frontend Data (Matching structure)
    print("Generating Frontend Data...")
    with open(args.frontend_output, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"Saved frontend data to {args.frontend_output}")

if __name__ == "__main__":
    main()
