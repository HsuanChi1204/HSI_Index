#!/usr/bin/env python3
"""
合併 Crime、Zillow 和 HouseTS Census 資料成 JSON 檔案
包含論文中的 HCI 計算和現有的多個指數
"""
import pandas as pd
import json
import numpy as np
from datetime import datetime
from collections import defaultdict
from typing import Optional, Dict
import sys
import os

# 加入模組路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculate_index import calculate_composite_index, normalize_min_max
from calculate_hci_paper import calculate_hci_paper_formula

# 嘗試導入 HouseTS 載入模組
try:
    from load_housets_from_csv import load_housets_csv, extract_latest_census_data, get_census_data_summary
    HOUSETS_CSV_AVAILABLE = True
except ImportError:
    try:
        from load_housets_census import load_housets_census_data, process_housets_census_for_dc, get_census_data_summary
        HOUSETS_CSV_AVAILABLE = False
    except ImportError:
        HOUSETS_CSV_AVAILABLE = False
        get_census_data_summary = lambda x: {}

def combine_data_to_json_with_hci(
    crime_csv: str = 'DC_Crime_Incidents_2025_08_09_with_zipcode.csv',
    zillow_csv: str = 'dc_zillow_2025_09_30.csv',
    housets_census_csv: Optional[str] = None,
    output_file: str = 'dc_crime_zillow_combined.json'
):
    """
    合併所有資料並計算各種指數
    
    Args:
        crime_csv: Crime 資料 CSV 檔案路徑
        zillow_csv: Zillow 資料 CSV 檔案路徑
        housets_census_csv: HouseTS Census 資料 CSV 檔案路徑（可選）
        output_file: 輸出 JSON 檔案路徑
    """
    print("=" * 70)
    print("合併 Crime、Zillow 和 HouseTS Census 資料成 JSON")
    print("=" * 70)
    
    # 讀取資料
    print("\n1. 讀取資料...")
    crime_df = pd.read_csv(crime_csv)
    zillow_df = pd.read_csv(zillow_csv)
    
    print(f"   Crime 資料: {len(crime_df)} 筆")
    print(f"   Zillow 資料: {len(zillow_df)} 筆")
    
    # 載入 HouseTS Census Data（如果提供）
    census_dict = {}
    if housets_census_csv and os.path.exists(housets_census_csv):
        print(f"\n   載入 HouseTS 資料...")
        
        # 取得所有 ZIP Code
        crime_df_clean = crime_df[crime_df['ZIP_CODE'].notna()].copy()
        dc_zip_codes = crime_df_clean['ZIP_CODE'].astype(str).unique().tolist()
        
        # 檢查是否是 HouseTS.csv 格式
        if housets_census_csv.endswith('HouseTS.csv') or 'housets' in housets_census_csv.lower():
            # 使用新的 HouseTS CSV 載入方式
            if HOUSETS_CSV_AVAILABLE:
                try:
                    housets_df = load_housets_csv(housets_census_csv, dc_zip_codes=dc_zip_codes)
                    if not housets_df.empty:
                        census_dict = extract_latest_census_data(housets_df)
                        census_summary = get_census_data_summary(census_dict)
                        print(f"   ✅ 載入 {len(census_dict)} 筆 Census 資料")
                        if census_summary:
                            print(f"      有人口資料的 ZIP Code: {census_summary.get('zip_codes_with_population', 0)}")
                    else:
                        print(f"   ⚠️  沒有找到 DC 地區的資料")
                except Exception as e:
                    print(f"   ❌ 載入 HouseTS CSV 失敗: {e}")
                    print(f"   ⚠️  將使用犯罪總數而非犯罪率")
            else:
                print(f"   ⚠️  HouseTS CSV 載入模組不可用")
        else:
            # 使用舊的 Census CSV 載入方式
            try:
                census_df = load_housets_census_data(housets_census_csv)
                if not census_df.empty:
                    census_dict = process_housets_census_for_dc(census_df, dc_zip_codes)
                    census_summary = get_census_data_summary(census_dict)
                    print(f"   ✅ 載入 {len(census_dict)} 筆 Census 資料")
                    if census_summary:
                        print(f"      有人口資料的 ZIP Code: {census_summary.get('zip_codes_with_population', 0)}")
            except Exception as e:
                print(f"   ❌ 載入 Census 資料失敗: {e}")
    else:
        print(f"   ⚠️  未提供 HouseTS 資料，將使用犯罪總數而非犯罪率")
    
    # 清理 Crime 資料
    crime_df = crime_df[crime_df['ZIP_CODE'].notna()].copy()
    crime_df['ZIP_CODE'] = crime_df['ZIP_CODE'].astype(int).astype(str)
    
    # 清理 Zillow 資料
    zillow_df['ZIPCode'] = zillow_df['ZIPCode'].astype(str)
    
    # 建立 Zillow 字典
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
    
    # 計算統計量
    crime_by_zip = crime_df.groupby('ZIP_CODE').size()
    min_crimes = int(crime_by_zip.min())
    max_crimes = int(crime_by_zip.max())
    
    min_price = float(zillow_df['CurrentPrice'].min()) if len(zillow_df) > 0 else None
    max_price = float(zillow_df['CurrentPrice'].max()) if len(zillow_df) > 0 else None
    
    # MoM 和 YoY 範圍
    min_mom = float(zillow_df['MOM'].min()) if len(zillow_df) > 0 and zillow_df['MOM'].notna().any() else None
    max_mom = float(zillow_df['MOM'].max()) if len(zillow_df) > 0 and zillow_df['MOM'].notna().any() else None
    min_yoy = float(zillow_df['YOY'].min()) if len(zillow_df) > 0 and zillow_df['YOY'].notna().any() else None
    max_yoy = float(zillow_df['YOY'].max()) if len(zillow_df) > 0 and zillow_df['YOY'].notna().any() else None
    
    # 犯罪率範圍（如果有 Census 資料）
    crime_rates = []
    if census_dict:
        for zip_code, census_data in census_dict.items():
            if census_data.get('total_population') and zip_code in crime_by_zip.index:
                crime_count = crime_by_zip[zip_code]
                crime_rate = (crime_count / census_data['total_population']) * 1000
                crime_rates.append(crime_rate)
    
    min_crime_rate = float(min(crime_rates)) if crime_rates else None
    max_crime_rate = float(max(crime_rates)) if crime_rates else None
    
    # Calculate 90th percentile for Clipped Score
    crime_ceiling = float(np.percentile(crime_rates, 90)) if crime_rates else None
    
    print(f"   犯罪數範圍: {min_crimes} - {max_crimes}")
    if min_price and max_price:
        print(f"   房價範圍: ${min_price:,.0f} - ${max_price:,.0f}")
    if min_mom is not None and max_mom is not None:
        print(f"   MoM 範圍: {min_mom:.4f} - {max_mom:.4f}")
    if min_yoy is not None and max_yoy is not None:
        print(f"   YoY 範圍: {min_yoy:.4f} - {max_yoy:.4f}")
    if min_crime_rate is not None and max_crime_rate is not None:
        print(f"   犯罪率範圍（每 1000 居民）: {min_crime_rate:.2f} - {max_crime_rate:.2f}")
    if crime_ceiling is not None:
        print(f"   犯罪率天花板 (90th percentile): {crime_ceiling:.2f}")
    
    print(f"\n3. 處理 Crime 資料統計並計算 Index...")
    
    # 按 ZIP Code 組織資料
    zipcode_data = defaultdict(lambda: {
        'zip_code': None,
        'zillow_data': None,
        'census_data': None,
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
        'hci': {
            'default': None,  # 預設權重 (w1=0.5, w2=0.5, alpha=0.5)
            'ranges': None,   # 範圍資訊（用於前端動態計算）
        },
        'crimes': []
    })
    
    # 處理每個 ZIP Code
    for zip_code in crime_by_zip.index:
        zip_code_str = str(zip_code)
        zip_crimes = crime_df[crime_df['ZIP_CODE'] == zip_code_str]
        
        zipcode_data[zip_code_str]['zip_code'] = zip_code_str
        
        # 加入 Zillow 資料
        if zip_code_str in zillow_dict:
            zipcode_data[zip_code_str]['zillow_data'] = zillow_dict[zip_code_str]
        
        # 加入 Census 資料
        if zip_code_str in census_dict:
            zipcode_data[zip_code_str]['census_data'] = census_dict[zip_code_str]
        
        # Crime 統計
        crime_count = len(zip_crimes)
        zipcode_data[zip_code_str]['crime_stats']['total_crimes'] = crime_count
        
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
        
        # 最近的犯罪記錄
        if 'REPORT_DAT' in zip_crimes.columns:
            try:
                zip_crimes_sorted = zip_crimes.copy()
                zip_crimes_sorted['REPORT_DAT'] = pd.to_datetime(zip_crimes_sorted['REPORT_DAT'], errors='coerce')
                recent = zip_crimes_sorted.nlargest(10, 'REPORT_DAT')
            except:
                recent = zip_crimes.head(10)
        else:
            recent = zip_crimes.head(10)
        
        recent_cols = ['CCN', 'REPORT_DAT', 'OFFENSE', 'BLOCK', 'LATITUDE', 'LONGITUDE']
        available_cols = [col for col in recent_cols if col in recent.columns]
        recent_dict = recent[available_cols].to_dict('records')
        zipcode_data[zip_code_str]['crime_stats']['recent_crimes'] = [
            {k: (None if pd.isna(v) else v) for k, v in record.items()}
            for record in recent_dict
        ]
        
        # 所有犯罪記錄
        crimes_cols = ['CCN', 'REPORT_DAT', 'SHIFT', 'METHOD', 'OFFENSE', 'BLOCK',
                       'WARD', 'DISTRICT', 'LATITUDE', 'LONGITUDE', 'ZIP_CODE']
        crimes_dict = zip_crimes[crimes_cols].to_dict('records')
        zipcode_data[zip_code_str]['crimes'] = [
            {k: (None if pd.isna(v) else v) for k, v in record.items()}
            for record in crimes_dict
        ]
        
        # 清理 NaN
        for crime in zipcode_data[zip_code_str]['crimes']:
            for key, value in crime.items():
                if pd.isna(value):
                    crime[key] = None
                elif key in ['WARD', 'DISTRICT'] and value is not None:
                    try:
                        crime[key] = int(value) if not pd.isna(value) else None
                    except (ValueError, TypeError):
                        crime[key] = None
        
        # 計算現有的多個指數
        price = zipcode_data[zip_code_str]['zillow_data']['current_price'] if zipcode_data[zip_code_str]['zillow_data'] else None
        if price is not None and not pd.isna(price):
            price = float(price)
        else:
            price = None
        
        indices = calculate_composite_index(
            crime_count=crime_count,
            price=price,
            min_crimes=min_crimes,
            max_crimes=max_crimes,
            min_price=min_price if min_price else 0,
            max_price=max_price if max_price else 1,
            crime_weight=0.6,
            price_weight=0.4
        )
        zipcode_data[zip_code_str]['indices'] = indices
        
        # 計算論文中的 HCI（預設權重）
        zillow_data = zipcode_data[zip_code_str]['zillow_data']
        census_data = zipcode_data[zip_code_str]['census_data']
        
        mom_rate = zillow_data['mom'] if zillow_data else None
        yoy_rate = zillow_data['yoy'] if zillow_data else None
        population = census_data['total_population'] if census_data else None
        
        # 計算預設 HCI (w1=0.5, w2=0.5, alpha=0.5)
        hci_default = calculate_hci_paper_formula(
            mom_rate=mom_rate,
            yoy_rate=yoy_rate,
            crime_count=crime_count,
            population=population,
            min_mom=min_mom,
            max_mom=max_mom,
            min_yoy=min_yoy,
            max_yoy=max_yoy,
            min_crime_count=min_crimes,
            max_crime_count=max_crimes,
            min_crime_rate=min_crime_rate,
            max_crime_rate=max_crime_rate,
            alpha=0.5,
            w1=0.5,
            w2=0.5,
            use_population=population is not None,
            crime_ceiling=crime_ceiling
        )
        zipcode_data[zip_code_str]['hci']['default'] = hci_default
        
        # 儲存範圍資訊（供前端動態計算）
        zipcode_data[zip_code_str]['hci']['ranges'] = {
            'min_mom': float(min_mom) if min_mom is not None else None,
            'max_mom': float(max_mom) if max_mom is not None else None,
            'min_yoy': float(min_yoy) if min_yoy is not None else None,
            'max_yoy': float(max_yoy) if max_yoy is not None else None,
            'min_crime_count': int(min_crimes),
            'max_crime_count': int(max_crimes),
            'min_crime_rate': float(min_crime_rate) if min_crime_rate is not None else None,
            'max_crime_rate': float(max_crime_rate) if max_crime_rate is not None else None,
            'crime_ceiling': float(crime_ceiling) if crime_ceiling is not None else None,
        }
    
    # 轉換為標準字典
    result = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_zipcodes': len(zipcode_data),
            'total_crimes': len(crime_df),
            'total_zillow_records': len(zillow_df),
            'total_census_records': len(census_dict),
            'index_ranges': {
                'crime_range': {'min': int(min_crimes), 'max': int(max_crimes)},
                'price_range': {'min': float(min_price) if min_price else None, 'max': float(max_price) if max_price else None},
                'mom_range': {'min': float(min_mom) if min_mom is not None else None, 'max': float(max_mom) if max_mom is not None else None},
                'yoy_range': {'min': float(min_yoy) if min_yoy is not None else None, 'max': float(max_yoy) if max_yoy is not None else None},
                'crime_rate_range': {'min': float(min_crime_rate) if min_crime_rate is not None else None, 'max': float(max_crime_rate) if max_crime_rate is not None else None},
            },
            'census_summary': get_census_data_summary(census_dict) if census_dict else None
        },
        'data': dict(zipcode_data)
    }
    
    # 清理 NaN 值
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
    
    cleaned_result = clean_for_json(result)
    
    # 儲存為 JSON
    print(f"\n4. 儲存 JSON 檔案: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False, default=str)
    
    # 計算檔案大小
    file_size = os.path.getsize(output_file) / 1024 / 1024
    print(f"   檔案大小: {file_size:.2f} MB")
    
    # 統計資訊
    print(f"\n5. 統計資訊:")
    print(f"   總 ZIP Code 數: {len(zipcode_data)}")
    print(f"   有 Zillow 資料的 ZIP Code: {sum(1 for z in zipcode_data.values() if z['zillow_data'] is not None)}")
    print(f"   有 Census 資料的 ZIP Code: {sum(1 for z in zipcode_data.values() if z['census_data'] is not None)}")
    print(f"   總犯罪記錄數: {len(crime_df)}")
    
    # Index 統計
    quality_scores = [z['indices']['quality_of_life_index'] for z in zipcode_data.values() if z['indices']['quality_of_life_index'] is not None]
    if quality_scores:
        print(f"\n6. Index 統計:")
        print(f"   生活品質指數範圍: {min(quality_scores):.1f} - {max(quality_scores):.1f}")
        print(f"   平均生活品質指數: {np.mean(quality_scores):.1f}")
        print(f"   中位數: {np.median(quality_scores):.1f}")
    
    # HCI 統計
    hci_scores = [z['hci']['default']['hci_score_100'] for z in zipcode_data.values() if z['hci']['default'] and z['hci']['default'].get('hci_score_100') is not None]
    if hci_scores:
        print(f"\n7. HCI 統計（論文公式，預設權重）:")
        print(f"   HCI 分數範圍: {min(hci_scores):.1f} - {max(hci_scores):.1f}")
        print(f"   平均 HCI 分數: {np.mean(hci_scores):.1f}")
        print(f"   中位數: {np.median(hci_scores):.1f}")
    
    print(f"\n✅ JSON 檔案已生成: {output_file}")
    return output_file

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='合併 Crime、Zillow 和 HouseTS Census 資料')
    parser.add_argument('--crime-csv', default='DC_Crime_Incidents_2025_08_09_with_zipcode.csv', help='Crime 資料 CSV 檔案')
    parser.add_argument('--zillow-csv', default='dc_zillow_2025_09_30.csv', help='Zillow 資料 CSV 檔案')
    parser.add_argument('--housets-census-csv', default=None, help='HouseTS Census 資料 CSV 檔案（可選）')
    parser.add_argument('--output', default='dc_crime_zillow_combined.json', help='輸出 JSON 檔案')
    
    args = parser.parse_args()
    
    combine_data_to_json_with_hci(
        crime_csv=args.crime_csv,
        zillow_csv=args.zillow_csv,
        housets_census_csv=args.housets_census_csv,
        output_file=args.output
    )

