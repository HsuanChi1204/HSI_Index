#!/usr/bin/env python3
"""
計算 Index 分數
包含標準化和綜合指數計算
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple

def normalize_min_max(value: float, min_val: float, max_val: float, reverse: bool = False) -> float:
    """
    Min-Max 標準化到 0-100
    
    Args:
        value: 要標準化的值
        min_val: 最小值
        max_val: 最大值
        reverse: 是否反向（True 表示值越大分數越小）
    
    Returns:
        標準化後的分數 (0-100)
    """
    if max_val == min_val:
        return 50.0  # 如果範圍為 0，返回中間值
    
    normalized = (value - min_val) / (max_val - min_val) * 100
    
    if reverse:
        normalized = 100 - normalized
    
    # 確保在 0-100 範圍內
    return max(0, min(100, normalized))

def calculate_crime_safety_index(crime_count: int, min_crimes: int, max_crimes: int) -> float:
    """
    計算犯罪安全指數 (0-100)
    分數越高表示越安全（犯罪數越少）
    """
    return normalize_min_max(crime_count, min_crimes, max_crimes, reverse=True)

def calculate_price_affordability_index(price: float, min_price: float, max_price: float) -> float:
    """
    計算房價可負擔性指數 (0-100)
    分數越高表示越可負擔（房價越低）
    """
    return normalize_min_max(price, min_price, max_price, reverse=True)

def calculate_price_premium_index(price: float, min_price: float, max_price: float) -> float:
    """
    計算房價高級指數 (0-100)
    分數越高表示房價越高
    """
    return normalize_min_max(price, min_price, max_price, reverse=False)

def calculate_composite_index(
    crime_count: int,
    price: float,
    min_crimes: int,
    max_crimes: int,
    min_price: float,
    max_price: float,
    crime_weight: float = 0.5,
    price_weight: float = 0.5
) -> Dict[str, float]:
    """
    計算綜合指數
    
    Args:
        crime_count: 犯罪數量
        price: 房價（可以是 None）
        min_crimes, max_crimes: 犯罪數範圍
        min_price, max_price: 房價範圍
        crime_weight: 犯罪權重（預設 0.5）
        price_weight: 房價權重（預設 0.5）
    
    Returns:
        包含各種指數的字典
    """
    # 安全指數（越高越安全）
    safety_index = calculate_crime_safety_index(crime_count, min_crimes, max_crimes)
    
    # 檢查是否有房價資料
    has_price = price is not None and not pd.isna(price) and min_price is not None and max_price is not None
    
    # 可負擔性指數（越高越可負擔）
    if has_price:
        affordability_index = calculate_price_affordability_index(price, min_price, max_price)
        premium_index = calculate_price_premium_index(price, min_price, max_price)
    else:
        affordability_index = None
        premium_index = None
    
    # 綜合生活品質指數（結合安全和可負擔性）
    # 如果沒有房價資料，只使用安全指數
    if not has_price:
        quality_of_life_index = safety_index
        investment_index = safety_index  # 只有安全指數
    else:
        # 可調整權重：安全 crime_weight%，可負擔性 price_weight%
        quality_of_life_index = safety_index * crime_weight + affordability_index * price_weight
        
        # 投資價值指數（高房價 + 低犯罪 = 高投資價值）
        # 標準化房價（越高越好）和標準化安全（越高越好）
        normalized_price = normalize_min_max(price, min_price, max_price, reverse=False)
        investment_index = (normalized_price * 0.6 + safety_index * 0.4)
    
    return {
        'safety_index': round(safety_index, 2),  # 安全指數（0-100，越高越安全）
        'affordability_index': round(affordability_index, 2) if has_price else None,  # 可負擔性指數（0-100，越高越可負擔）
        'premium_index': round(premium_index, 2) if has_price else None,  # 房價高級指數（0-100，越高越貴）
        'quality_of_life_index': round(quality_of_life_index, 2),  # 生活品質指數（0-100，越高越好）
        'investment_index': round(investment_index, 2),  # 投資價值指數（0-100，越高越好）
        'crime_index': round(100 - safety_index, 2),  # 犯罪風險指數（0-100，越高越危險，與安全指數相反）
    }

def calculate_all_indices(
    crime_df: pd.DataFrame,
    zillow_df: pd.DataFrame
) -> Dict[str, Dict[str, float]]:
    """
    計算所有 ZIP Code 的指數
    
    Returns:
        字典，key 為 ZIP Code，value 為指數字典
    """
    # 清理資料
    crime_df = crime_df[crime_df['ZIP_CODE'].notna()].copy()
    crime_df['ZIP_CODE'] = crime_df['ZIP_CODE'].astype(int).astype(str)
    zillow_df['ZIPCode'] = zillow_df['ZIPCode'].astype(str)
    
    # 計算統計量
    crime_by_zip = crime_df.groupby('ZIP_CODE').size()
    min_crimes = crime_by_zip.min()
    max_crimes = crime_by_zip.max()
    
    min_price = zillow_df['CurrentPrice'].min()
    max_price = zillow_df['CurrentPrice'].max()
    
    print(f"\n指數計算範圍:")
    print(f"  犯罪數範圍: {min_crimes} - {max_crimes}")
    print(f"  房價範圍: ${min_price:,.0f} - ${max_price:,.0f}")
    
    # 計算每個 ZIP Code 的指數
    indices = {}
    
    for zip_code in crime_by_zip.index:
        zip_code_str = str(zip_code)
        crime_count = crime_by_zip[zip_code]
        
        # 取得房價
        zillow_row = zillow_df[zillow_df['ZIPCode'] == zip_code_str]
        price = zillow_row['CurrentPrice'].iloc[0] if len(zillow_row) > 0 else None
        
        # 計算指數
        indices[zip_code_str] = calculate_composite_index(
            crime_count=crime_count,
            price=price,
            min_crimes=min_crimes,
            max_crimes=max_crimes,
            min_price=min_price,
            max_price=max_price,
            crime_weight=0.6,  # 安全權重 60%
            price_weight=0.4   # 可負擔性權重 40%
        )
    
    return indices

if __name__ == "__main__":
    # 測試
    crime_df = pd.read_csv('DC_Crime_Incidents_2025_08_09_with_zipcode.csv')
    zillow_df = pd.read_csv('dc_zillow_2025_09_30.csv')
    
    indices = calculate_all_indices(crime_df, zillow_df)
    
    # 顯示前幾個 ZIP Code 的指數
    print("\n範例指數（前 5 個 ZIP Code）:")
    for i, (zip_code, index_data) in enumerate(list(indices.items())[:5]):
        print(f"\nZIP {zip_code}:")
        for key, value in index_data.items():
            print(f"  {key}: {value}")

