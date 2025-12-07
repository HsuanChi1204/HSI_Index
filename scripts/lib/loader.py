"""
從 HouseTS.csv 載入和處理 Census 資料
這個 CSV 檔案包含了房價、POI、Census 等所有資料
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import os

def load_housets_csv(file_path: str, dc_zip_codes: Optional[List[str]] = None) -> pd.DataFrame:
    """
    載入 HouseTS.csv 並篩選 DC 地區的資料
    """
    print(f"載入 HouseTS.csv: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 檔案不存在: {file_path}")
        return pd.DataFrame()
    
    # 檢查檔案大小
    file_size = os.path.getsize(file_path) / 1024 / 1024
    print(f"   檔案大小: {file_size:.2f} MB")
    
    # 如果提供了 DC ZIP Codes，直接篩選
    if dc_zip_codes:
        print(f"   篩選 DC ZIP Codes: {len(dc_zip_codes)} 個")
        # 處理不同的 ZIP Code 格式（可能是 '20001.0' 或 '20001'）
        dc_zips_int = []
        for z in dc_zip_codes:
            try:
                # 先轉換為浮點數，再轉換為整數（處理 '20001.0' 格式）
                zip_int = int(float(str(z).strip()))
                if 20000 <= zip_int < 21000:  # DC ZIP Code 範圍
                    dc_zips_int.append(zip_int)
            except (ValueError, TypeError):
                continue
        
        print(f"   有效的 DC ZIP Codes: {len(dc_zips_int)} 個")
        
        # 分批讀取並篩選
        chunks = []
        chunk_size = 100000
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
            # 篩選 DC ZIP Codes
            dc_chunk = chunk[chunk['zipcode'].isin(dc_zips_int)]
            if len(dc_chunk) > 0:
                chunks.append(dc_chunk)
                # print(f"   處理中... 找到 {len(dc_chunk)} 筆資料")
        
        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            print(f"✅ 載入成功: {len(df)} 筆 DC 資料")
            return df
        else:
            print("❌ 沒有找到匹配的 DC 資料")
            return pd.DataFrame()
    else:
        # 沒有提供 ZIP Codes，嘗試根據城市名稱篩選
        print("   根據城市名稱篩選 DC 地區...")
        chunks = []
        chunk_size = 100000
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
            # 篩選 Washington DC 地區
            dc_chunk = chunk[
                chunk['city_full'].str.contains(
                    'washington.*arlington|washington.*alexandria|washington.*dc',
                    case=False, na=False, regex=True
                )
            ]
            if len(dc_chunk) > 0:
                chunks.append(dc_chunk)
        
        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            print(f"✅ 載入成功: {len(df)} 筆 DC 資料")
            return df
        else:
            print("❌ 沒有找到 DC 地區資料")
            return pd.DataFrame()

def extract_latest_census_data(housets_df: pd.DataFrame) -> Dict[str, Dict]:
    """
    從 HouseTS 資料中提取最新的 Census 資料
    """
    print(f"\n提取最新的 Census 資料...")
    
    if housets_df.empty:
        return {}
    
    # 確保 zipcode 是字串
    housets_df['zipcode'] = housets_df['zipcode'].astype(str)
    
    # 找出每個 ZIP Code 最新的資料（根據 year 和 date）
    # 先按 year 排序，然後按 date 排序
    housets_df = housets_df.sort_values(['zipcode', 'year', 'date'], ascending=[True, False, False])
    
    # 取得每個 ZIP Code 的最新一筆資料
    latest_data = housets_df.groupby('zipcode').first().reset_index()
    
    print(f"   找到 {len(latest_data)} 個 ZIP Code 的最新資料")
    
    # 提取 Census 資料
    census_dict = {}
    
    census_fields = {
        'total_population': 'Total Population',
        'median_age': 'Median Age',
        'per_capita_income': 'Per Capita Income',
        'total_families_below_poverty': 'Total Families Below Poverty',
        'total_housing_units': 'Total Housing Units',
        'median_rent': 'Median Rent',
        'median_home_value': 'Median Home Value',
        'total_labor_force': 'Total Labor Force',
        'unemployed_population': 'Unemployed Population',
        'school_age_population': 'Total School Age Population',
        'school_enrollment': 'Total School Enrollment',
        'median_commute_time': 'Median Commute Time'
    }
    
    for _, row in latest_data.iterrows():
        zip_code = str(row['zipcode'])
        
        # 提取 Census 資料
        census_data = {}
        for key, field in census_fields.items():
            if field in row and pd.notna(row[field]):
                if key in ['total_population', 'total_families_below_poverty', 'total_housing_units',
                          'total_labor_force', 'unemployed_population', 'school_age_population',
                          'school_enrollment']:
                    # 整數欄位
                    try:
                        census_data[key] = int(float(row[field]))
                    except (ValueError, TypeError):
                        census_data[key] = None
                else:
                    # 浮點數欄位
                    try:
                        census_data[key] = float(row[field])
                    except (ValueError, TypeError):
                        census_data[key] = None
            else:
                census_data[key] = None
        
        # 計算衍生指標
        if census_data.get('total_population') and census_data['total_population'] > 0:
            # 貧困率
            if census_data.get('total_families_below_poverty') is not None:
                census_data['poverty_family_rate'] = (census_data['total_families_below_poverty'] / 
                                                      census_data['total_population']) * 100
                census_data['poverty_rate'] = census_data['poverty_family_rate']
            else:
                census_data['poverty_rate'] = None
                census_data['poverty_family_rate'] = None
            
            # 失業率
            if (census_data.get('total_labor_force') and 
                census_data['total_labor_force'] > 0 and 
                census_data.get('unemployed_population') is not None):
                census_data['unemployment_rate'] = (census_data['unemployed_population'] / 
                                                   census_data['total_labor_force']) * 100
            else:
                census_data['unemployment_rate'] = None
            
            # 就學率
            if (census_data.get('school_age_population') and 
                census_data['school_age_population'] > 0 and 
                census_data.get('school_enrollment') is not None):
                census_data['school_enrollment_rate'] = (census_data['school_enrollment'] / 
                                                        census_data['school_age_population']) * 100
            else:
                census_data['school_enrollment_rate'] = None
        else:
            census_data['poverty_rate'] = None
            census_data['unemployment_rate'] = None
            census_data['school_enrollment_rate'] = None
        
        # 加入 POI 資料
        poi_fields = {
            'bank': 'bank',
            'bus': 'bus',
            'hospital': 'hospital',
            'mall': 'mall',
            'park': 'park',
            'restaurant': 'restaurant',
            'school_poi': 'school',
            'station': 'station',
            'supermarket': 'supermarket'
        }
        
        for key, field in poi_fields.items():
            if field in row and pd.notna(row[field]):
                try:
                    census_data[key] = int(float(row[field]))
                except (ValueError, TypeError):
                    census_data[key] = 0
            else:
                census_data[key] = 0
        
        census_dict[zip_code] = census_data
    
    return census_dict

def get_census_data_summary(census_dict: Dict[str, Dict]) -> Dict:
    """
    取得 Census Data 統計摘要
    """
    if not census_dict:
        return {}
    
    populations = [d['total_population'] for d in census_dict.values() 
                   if d.get('total_population') and d['total_population'] > 0]
    incomes = [d['per_capita_income'] for d in census_dict.values() 
               if d.get('per_capita_income') and d['per_capita_income'] > 0]
    rents = [d['median_rent'] for d in census_dict.values() 
             if d.get('median_rent') and d['median_rent'] > 0]
    home_values = [d['median_home_value'] for d in census_dict.values() 
                   if d.get('median_home_value') and d['median_home_value'] > 0]
    
    summary = {
        'total_zip_codes': len(census_dict),
        'zip_codes_with_population': len(populations),
        'zip_codes_with_income': len(incomes),
        'zip_codes_with_rent': len(rents),
        'zip_codes_with_home_value': len(home_values),
    }
    
    if populations:
        summary['population'] = {
            'min': int(min(populations)),
            'max': int(max(populations)),
            'mean': float(np.mean(populations)),
            'median': float(np.median(populations))
        }
    
    if incomes:
        summary['income'] = {
            'min': float(min(incomes)),
            'max': float(max(incomes)),
            'mean': float(np.mean(incomes)),
            'median': float(np.median(incomes))
        }
    
    if rents:
        summary['rent'] = {
            'min': float(min(rents)),
            'max': float(max(rents)),
            'mean': float(np.mean(rents)),
            'median': float(np.median(rents))
        }
    
    if home_values:
        summary['home_value'] = {
            'min': float(min(home_values)),
            'max': float(max(home_values)),
            'mean': float(np.mean(home_values)),
            'median': float(np.median(home_values))
        }
    
    return summary
