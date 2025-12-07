#!/usr/bin/env python3
"""
合併 Crime 和 Zillow 資料成 JSON 檔案
對應任務: AS-5 - Combine house pricing and crime data into json file
"""
import pandas as pd
import json
import numpy as np
from datetime import datetime
from collections import defaultdict
import sys
import os

# 加入 calculate_index 模組的路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculate_index import calculate_composite_index, normalize_min_max

def combine_data_to_json():
    """
    合併 Crime 和 Zillow 資料，按 ZIP Code 組織成 JSON
    """
    print("=" * 70)
    print("合併 Crime 和 Zillow 資料成 JSON")
    print("=" * 70)
    
    # 讀取資料
    print("\n1. 讀取資料...")
    crime_df = pd.read_csv('DC_Crime_Incidents_in_2025_with_zipcode.csv')
    zillow_df = pd.read_csv('dc_zillow_2025_09_30.csv')
    
    print(f"   Crime 資料: {len(crime_df)} 筆")
    print(f"   Zillow 資料: {len(zillow_df)} 筆")
    
    # 清理 Crime 資料（只保留有 ZIP_CODE 的）
    crime_df = crime_df[crime_df['ZIP_CODE'].notna()].copy()
    crime_df['ZIP_CODE'] = crime_df['ZIP_CODE'].astype(int).astype(str)
    
    # 清理 Zillow 資料
    zillow_df['ZIPCode'] = zillow_df['ZIPCode'].astype(str)
    
    # 建立 Zillow 字典（快速查詢）
    zillow_dict = {}
    for _, row in zillow_df.iterrows():
        zip_code = str(row['ZIPCode'])
        zillow_dict[zip_code] = {
            'region_name': row['RegionName'],
            'state': row['State'],
            'metro': row['Metro'],
            'county_name': row['CountyName'],
            'mom': float(row['MOM']) if pd.notna(row['MOM']) else None,
            'yoy': float(row['YOY']) if pd.notna(row['YOY']) else None,
            'current_price': float(row['CurrentPrice']) if pd.notna(row['CurrentPrice']) else None
        }
    
    print(f"\n2. 計算統計範圍（用於標準化）...")
    
    # 計算統計量（用於標準化）
    crime_by_zip = crime_df.groupby('ZIP_CODE').size()
    min_crimes = int(crime_by_zip.min())
    max_crimes = int(crime_by_zip.max())
    
    min_price = float(zillow_df['CurrentPrice'].min()) if len(zillow_df) > 0 else None
    max_price = float(zillow_df['CurrentPrice'].max()) if len(zillow_df) > 0 else None
    
    print(f"   犯罪數範圍: {min_crimes} - {max_crimes}")
    if min_price and max_price:
        print(f"   房價範圍: ${min_price:,.0f} - ${max_price:,.0f}")
    
    print(f"\n3. 處理 Crime 資料統計並計算 Index...")
    
    # 按 ZIP Code 組織 Crime 資料
    zipcode_data = defaultdict(lambda: {
        'zip_code': None,
        'zillow_data': None,
        'crime_stats': {
            'total_crimes': 0,
            'by_offense': {},
            'by_shift': {},
            'by_ward': {},
            'recent_crimes': []
        },
        'indices': {
            'safety_index': None,
            'affordability_index': None,
            'premium_index': None,
            'quality_of_life_index': None,
            'investment_index': None,
            'crime_index': None
        },
        'crimes': []
    })
    
    # 處理每個 ZIP Code
    for zip_code in crime_df['ZIP_CODE'].unique():
        zip_code_str = str(zip_code)
        zip_crimes = crime_df[crime_df['ZIP_CODE'] == zip_code_str]
        
        zipcode_data[zip_code_str]['zip_code'] = zip_code_str
        
        # 加入 Zillow 資料
        if zip_code_str in zillow_dict:
            zipcode_data[zip_code_str]['zillow_data'] = zillow_dict[zip_code_str]
        
        # Crime 統計
        zipcode_data[zip_code_str]['crime_stats']['total_crimes'] = len(zip_crimes)
        
        # 按犯罪類型統計
        offense_counts = zip_crimes['OFFENSE'].value_counts().to_dict()
        zipcode_data[zip_code_str]['crime_stats']['by_offense'] = {
            k: int(v) for k, v in offense_counts.items()
        }
        
        # 按時段統計
        shift_counts = zip_crimes['SHIFT'].value_counts().to_dict()
        zipcode_data[zip_code_str]['crime_stats']['by_shift'] = {
            k: int(v) for k, v in shift_counts.items()
        }
        
        # 按 WARD 統計
        ward_counts = zip_crimes['WARD'].dropna().value_counts().to_dict()
        zipcode_data[zip_code_str]['crime_stats']['by_ward'] = {
            str(k): int(v) for k, v in ward_counts.items()
        }
        
        # 最近的犯罪記錄（最多 10 筆）
        if 'REPORT_DAT' in zip_crimes.columns:
            try:
                # 轉換為 datetime 並排序
                zip_crimes_sorted = zip_crimes.copy()
                zip_crimes_sorted['REPORT_DAT'] = pd.to_datetime(zip_crimes_sorted['REPORT_DAT'], errors='coerce')
                recent = zip_crimes_sorted.nlargest(10, 'REPORT_DAT')
            except:
                recent = zip_crimes.head(10)
        else:
            recent = zip_crimes.head(10)
        
        # 選擇需要的欄位
        recent_cols = ['CCN', 'REPORT_DAT', 'OFFENSE', 'BLOCK', 'LATITUDE', 'LONGITUDE']
        available_cols = [col for col in recent_cols if col in recent.columns]
        recent_dict = recent[available_cols].to_dict('records')
        # 將 NaN 轉換為 None (JSON 中的 null)
        zipcode_data[zip_code_str]['crime_stats']['recent_crimes'] = [
            {k: (None if pd.isna(v) else v) for k, v in record.items()}
            for record in recent_dict
        ]
        
        # 所有犯罪記錄（簡化版，只保留重要欄位）
        crimes_cols = ['CCN', 'REPORT_DAT', 'SHIFT', 'METHOD', 'OFFENSE', 'BLOCK',
                       'WARD', 'DISTRICT', 'LATITUDE', 'LONGITUDE', 'ZIP_CODE']
        crimes_dict = zip_crimes[crimes_cols].to_dict('records')
        # 將 NaN 轉換為 None (JSON 中的 null)
        zipcode_data[zip_code_str]['crimes'] = [
            {k: (None if pd.isna(v) else (int(v) if isinstance(v, (int, float)) and not pd.isna(v) and k in ['WARD', 'DISTRICT'] and pd.notna(v) else v)) 
             for k, v in record.items()}
            for record in crimes_dict
        ]
        # 更簡潔的方式處理 NaN
        for crime in zipcode_data[zip_code_str]['crimes']:
            for key, value in crime.items():
                if pd.isna(value):
                    crime[key] = None
                elif key in ['WARD', 'DISTRICT'] and value is not None:
                    try:
                        crime[key] = int(value) if not pd.isna(value) else None
                    except (ValueError, TypeError):
                        crime[key] = None
        
        # 計算 Index 分數
        crime_count = len(zip_crimes)
        price = zipcode_data[zip_code_str]['zillow_data']['current_price'] if zipcode_data[zip_code_str]['zillow_data'] else None
        
        if price is not None and not pd.isna(price):
            price = float(price)
        else:
            price = None
        
        # 計算各種指數
        indices = calculate_composite_index(
            crime_count=crime_count,
            price=price,
            min_crimes=min_crimes,
            max_crimes=max_crimes,
            min_price=min_price if min_price else 0,
            max_price=max_price if max_price else 1,
            crime_weight=0.6,  # 安全權重 60%
            price_weight=0.4   # 可負擔性權重 40%
        )
        
        zipcode_data[zip_code_str]['indices'] = indices
    
    # 轉換為標準字典
    result = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_zipcodes': len(zipcode_data),
            'total_crimes': len(crime_df),
            'total_zillow_records': len(zillow_df),
            'index_ranges': {
                'crime_range': {'min': int(min_crimes), 'max': int(max_crimes)},
                'price_range': {'min': float(min_price) if min_price else None, 'max': float(max_price) if max_price else None}
            }
        },
        'data': dict(zipcode_data)
    }
    
    # 儲存為 JSON（確保沒有 NaN 值）
    output_file = 'dc_crime_zillow_combined.json'
    print(f"\n4. 儲存 JSON 檔案: {output_file}")
    
    # 自訂 JSON encoder，將 NaN 轉換為 None
    def clean_for_json(obj):
        """遞迴清理物件，將 NaN 轉換為 None"""
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(item) for item in obj]
        elif pd.isna(obj):
            return None
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj) if not pd.isna(obj) else None
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    # 清理結果
    cleaned_result = clean_for_json(result)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False, default=str)
    
    # 計算檔案大小
    import os
    file_size = os.path.getsize(output_file) / 1024 / 1024  # MB
    print(f"   檔案大小: {file_size:.2f} MB")
    
    # 統計資訊
    print(f"\n5. 統計資訊:")
    print(f"   總 ZIP Code 數: {len(zipcode_data)}")
    print(f"   有 Zillow 資料的 ZIP Code: {sum(1 for z in zipcode_data.values() if z['zillow_data'] is not None)}")
    print(f"   總犯罪記錄數: {len(crime_df)}")
    
    # Index 統計
    quality_scores = [z['indices']['quality_of_life_index'] for z in zipcode_data.values() if z['indices']['quality_of_life_index'] is not None]
    if quality_scores:
        print(f"\n6. Index 統計:")
        print(f"   生活品質指數範圍: {min(quality_scores):.1f} - {max(quality_scores):.1f}")
        print(f"   平均生活品質指數: {np.mean(quality_scores):.1f}")
        print(f"   中位數: {np.median(quality_scores):.1f}")
    
    print(f"\n✅ JSON 檔案已生成: {output_file}")
    return output_file

if __name__ == "__main__":
    combine_data_to_json()

