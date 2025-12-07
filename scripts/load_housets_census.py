#!/usr/bin/env python3
"""
載入和處理 HouseTS Census Data
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import os

def load_housets_census_data(file_path: str) -> pd.DataFrame:
    """
    載入 HouseTS Census Data
    
    Args:
        file_path: HouseTS Census Data CSV 檔案路徑
    
    Returns:
        Census Data DataFrame
    """
    print(f"載入 HouseTS Census Data: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 檔案不存在: {file_path}")
        return pd.DataFrame()
    
    # 讀取 CSV
    df = pd.read_csv(file_path)
    
    print(f"✅ 載入成功: {len(df)} 筆記錄")
    print(f"   欄位: {list(df.columns)}")
    
    return df

def process_housets_census_for_dc(
    census_df: pd.DataFrame,
    dc_zip_codes: list
) -> Dict[str, Dict]:
    """
    處理 HouseTS Census Data，只保留 DC 的 ZIP Code
    
    Args:
        census_df: Census Data DataFrame
        dc_zip_codes: DC ZIP Code 列表
    
    Returns:
        字典，key 為 ZIP Code，value 為 Census 資料
    """
    print(f"\n處理 HouseTS Census Data for DC...")
    print(f"   DC ZIP Code 數: {len(dc_zip_codes)}")
    
    # 轉換 ZIP Code 為字串
    dc_zip_codes_str = [str(zip_code) for zip_code in dc_zip_codes]
    
    # 找出 ZIP Code 欄位名稱（可能是 'zip_code', 'ZIPCode', 'ZIP', 等）
    zip_column = None
    for col in ['zip_code', 'ZIPCode', 'ZIP', 'zipcode', 'ZIP_CODE']:
        if col in census_df.columns:
            zip_column = col
            break
    
    if zip_column is None:
        print("❌ 找不到 ZIP Code 欄位")
        print(f"   可用欄位: {list(census_df.columns)}")
        return {}
    
    print(f"   使用 ZIP Code 欄位: {zip_column}")
    
    # 轉換 ZIP Code 為字串
    census_df[zip_column] = census_df[zip_column].astype(str)
    
    # 篩選 DC ZIP Code
    dc_census = census_df[census_df[zip_column].isin(dc_zip_codes_str)].copy()
    
    print(f"✅ 找到 {len(dc_census)} 筆 DC Census 資料")
    
    # 轉換為字典
    census_dict = {}
    for _, row in dc_census.iterrows():
        zip_code = str(row[zip_column])
        
        # 提取 Census 資料
        census_data = {
            'total_population': int(row['Total Population']) if 'Total Population' in row and pd.notna(row['Total Population']) else None,
            'median_age': float(row['Median Age']) if 'Median Age' in row and pd.notna(row['Median Age']) else None,
            'per_capita_income': float(row['Per Capita Income']) if 'Per Capita Income' in row and pd.notna(row['Per Capita Income']) else None,
            'total_families_below_poverty': int(row['Total Families Below Poverty']) if 'Total Families Below Poverty' in row and pd.notna(row['Total Families Below Poverty']) else None,
            'total_housing_units': int(row['Total Housing Units']) if 'Total Housing Units' in row and pd.notna(row['Total Housing Units']) else None,
            'median_rent': float(row['Median Rent']) if 'Median Rent' in row and pd.notna(row['Median Rent']) else None,
            'median_home_value': float(row['Median Home Value']) if 'Median Home Value' in row and pd.notna(row['Median Home Value']) else None,
            'total_labor_force': int(row['Total Labor Force']) if 'Total Labor Force' in row and pd.notna(row['Total Labor Force']) else None,
            'unemployed_population': int(row['Unemployed Population']) if 'Unemployed Population' in row and pd.notna(row['Unemployed Population']) else None,
            'school_age_population': int(row['School-Age Population']) if 'School-Age Population' in row and pd.notna(row['School-Age Population']) else None,
            'school_enrollment': int(row['School Enrollment']) if 'School Enrollment' in row and pd.notna(row['School Enrollment']) else None,
            'median_commute_time': float(row['Median Commute Time']) if 'Median Commute Time' in row and pd.notna(row['Median Commute Time']) else None,
        }
        
        # 計算衍生指標
        if census_data['total_population'] and census_data['total_population'] > 0:
            # 貧困率
            if census_data['total_families_below_poverty'] is not None:
                census_data['poverty_rate'] = (census_data['total_families_below_poverty'] / census_data['total_population']) * 100
            else:
                census_data['poverty_rate'] = None
            
            # 失業率
            if census_data['total_labor_force'] and census_data['total_labor_force'] > 0 and census_data['unemployed_population'] is not None:
                census_data['unemployment_rate'] = (census_data['unemployed_population'] / census_data['total_labor_force']) * 100
            else:
                census_data['unemployment_rate'] = None
            
            # 就學率
            if census_data['school_age_population'] and census_data['school_age_population'] > 0 and census_data['school_enrollment'] is not None:
                census_data['school_enrollment_rate'] = (census_data['school_enrollment'] / census_data['school_age_population']) * 100
            else:
                census_data['school_enrollment_rate'] = None
        else:
            census_data['poverty_rate'] = None
            census_data['unemployment_rate'] = None
            census_data['school_enrollment_rate'] = None
        
        census_dict[zip_code] = census_data
    
    return census_dict

def get_census_data_summary(census_dict: Dict[str, Dict]) -> Dict:
    """
    取得 Census Data 統計摘要
    
    Args:
        census_dict: Census 資料字典
    
    Returns:
        統計摘要字典
    """
    if not census_dict:
        return {}
    
    # 收集所有數值
    populations = [d['total_population'] for d in census_dict.values() if d.get('total_population')]
    incomes = [d['per_capita_income'] for d in census_dict.values() if d.get('per_capita_income')]
    rents = [d['median_rent'] for d in census_dict.values() if d.get('median_rent')]
    home_values = [d['median_home_value'] for d in census_dict.values() if d.get('median_home_value')]
    
    summary = {
        'total_zip_codes': len(census_dict),
        'zip_codes_with_population': len(populations),
        'zip_codes_with_income': len(incomes),
        'zip_codes_with_rent': len(rents),
        'zip_codes_with_home_value': len(home_values),
    }
    
    if populations:
        summary['population'] = {
            'min': min(populations),
            'max': max(populations),
            'mean': np.mean(populations),
            'median': np.median(populations)
        }
    
    if incomes:
        summary['income'] = {
            'min': min(incomes),
            'max': max(incomes),
            'mean': np.mean(incomes),
            'median': np.median(incomes)
        }
    
    if rents:
        summary['rent'] = {
            'min': min(rents),
            'max': max(rents),
            'mean': np.mean(rents),
            'median': np.median(rents)
        }
    
    if home_values:
        summary['home_value'] = {
            'min': min(home_values),
            'max': max(home_values),
            'mean': np.mean(home_values),
            'median': np.median(home_values)
        }
    
    return summary

if __name__ == "__main__":
    # 測試
    print("測試 HouseTS Census Data 載入...")
    
    # 檢查檔案是否存在
    test_files = [
        'housets_census.csv',
        'HouseTS_Census.csv',
        'census_data.csv',
        'data/housets_census.csv'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n找到檔案: {file_path}")
            df = load_housets_census_data(file_path)
            if not df.empty:
                print(f"\n前 5 筆資料:")
                print(df.head())
                print(f"\n欄位資訊:")
                print(df.info())
            break
    else:
        print("\n❌ 找不到 HouseTS Census Data 檔案")
        print("   請將檔案放在專案根目錄或 data/ 資料夾中")

