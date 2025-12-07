#!/usr/bin/env python3
"""
按照論文公式計算 HCI (Housing-Crime Index)
支援用戶自定義權重
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple

def normalize_to_0_1(value: float, min_val: float, max_val: float) -> float:
    """
    標準化到 [0, 1] 範圍（論文公式）
    
    Args:
        value: 要標準化的值
        min_val: 最小值
        max_val: 最大值
    
    Returns:
        標準化後的分數 (0-1)
    """
    if max_val == min_val:
        return 0.5  # 如果範圍為 0，返回中間值
    
    normalized = (value - min_val) / (max_val - min_val)
    
    # 確保在 0-1 範圍內
    return max(0.0, min(1.0, normalized))

def calculate_growth_indicator(
    mom_rate: float,
    yoy_rate: float,
    min_mom: float,
    max_mom: float,
    min_yoy: float,
    max_yoy: float,
    alpha: float = 0.5
) -> float:
    """
    計算成長指標 G_z（論文公式 3）
    
    G_z = α * YoY_z + (1 - α) * MoM_z
    
    Args:
        mom_rate: Month-over-Month 成長率
        yoy_rate: Year-over-Year 成長率
        min_mom, max_mom: MoM 範圍
        min_yoy, max_yoy: YoY 範圍
        alpha: YoY 權重（預設 0.5）
    
    Returns:
        標準化的成長指標 (0-1)
    """
    # 標準化 MoM 和 YoY
    normalized_mom = normalize_to_0_1(mom_rate, min_mom, max_mom)
    normalized_yoy = normalize_to_0_1(yoy_rate, min_yoy, max_yoy)
    
    # 結合 MoM 和 YoY
    growth_indicator = alpha * normalized_yoy + (1 - alpha) * normalized_mom
    
    return growth_indicator

def calculate_crime_rate_per_1000(
    crime_count: int,
    population: Optional[int]
) -> Optional[float]:
    """
    計算每 1000 居民的犯罪率（論文要求）
    
    Args:
        crime_count: 犯罪數量
        population: 人口數（如果為 None，返回 None）
    
    Returns:
        每 1000 居民的犯罪率，如果沒有人口資料則返回 None
    """
    if population is None or population == 0:
        return None
    
    crime_rate = (crime_count / population) * 1000
    return crime_rate

def calculate_crime_indicator(
    crime_rate: Optional[float],
    crime_count: int,
    min_crime_rate: Optional[float],
    max_crime_rate: Optional[float],
    min_crime_count: int,
    max_crime_count: int,
    use_population: bool = True,
    crime_ceiling: Optional[float] = None  # New parameter for clipped score
) -> float:
    """
    計算犯罪指標 C_z（論文公式 4 + Clipped Score 改良）
    
    如果有人口資料，使用犯罪率（每 1000 居民）
    如果沒有人口資料，使用犯罪總數
    
    Args:
        crime_rate: 每 1000 居民的犯罪率（可選）
        crime_count: 犯罪總數
        min_crime_rate, max_crime_rate: 犯罪率範圍（可選）
        min_crime_count, max_crime_count: 犯罪數範圍
        use_population: 是否使用人口資料（預設 True）
        crime_ceiling: 犯罪率天花板（90th percentile），超過此值視為最危險 (1.0)
    
    Returns:
        標準化的犯罪指標 (0-1)
    """
    if use_population and crime_rate is not None:
        # 使用犯罪率（每 1000 居民）
        if crime_ceiling is not None:
            # Clipped Score Method
            # 如果犯罪率 > 天花板，指標 = 1.0 (最危險)
            # 否則，指標 = crime_rate / crime_ceiling
            if crime_rate >= crime_ceiling:
                return 1.0
            else:
                return crime_rate / crime_ceiling
        elif min_crime_rate is not None and max_crime_rate is not None:
            # 傳統 Min-Max Normalization
            return normalize_to_0_1(crime_rate, min_crime_rate, max_crime_rate)
            
    # Fallback: 使用犯罪總數 (如果沒有人口資料或參數不足)
    return normalize_to_0_1(crime_count, min_crime_count, max_crime_count)

def calculate_hci_paper_formula(
    mom_rate: Optional[float],
    yoy_rate: Optional[float],
    crime_count: int,
    population: Optional[int] = None,
    # 範圍參數
    min_mom: Optional[float] = None,
    max_mom: Optional[float] = None,
    min_yoy: Optional[float] = None,
    max_yoy: Optional[float] = None,
    min_crime_count: Optional[int] = None,
    max_crime_count: Optional[int] = None,
    min_crime_rate: Optional[float] = None,
    max_crime_rate: Optional[float] = None,
    # 權重參數
    alpha: float = 0.5,  # MoM 和 YoY 的權重
    w1: float = 0.5,     # 成長權重
    w2: float = 0.5,     # 安全權重
    use_population: bool = True,
    crime_ceiling: Optional[float] = None # New parameter
) -> Dict[str, float]:
    """
    按照論文公式計算 HCI（Housing-Crime Index）
    
    HCI_z = w1 * G_z + w2 * (1 - C_z)
    
    其中：
    - G_z = α * YoY_z + (1 - α) * MoM_z
    - C_z = 標準化的犯罪指標 (支援 Clipped Score)
    
    Args:
        mom_rate: Month-over-Month 成長率（可選）
        yoy_rate: Year-over-Year 成長率（可選）
        crime_count: 犯罪數量
        population: 人口數（可選，用於計算犯罪率）
        min_mom, max_mom: MoM 範圍
        min_yoy, max_yoy: YoY 範圍
        min_crime_count, max_crime_count: 犯罪數範圍
        min_crime_rate, max_crime_rate: 犯罪率範圍（可選）
        alpha: YoY 權重（預設 0.5）
        w1: 成長權重（預設 0.5）
        w2: 安全權重（預設 0.5）
        use_population: 是否使用人口資料（預設 True）
        crime_ceiling: 犯罪率天花板（90th percentile），用於 Clipped Score
    
    Returns:
        包含 HCI 和相關指標的字典
    """
    # 計算犯罪率
    crime_rate = calculate_crime_rate_per_1000(crime_count, population) if use_population else None
    
    # 計算成長指標 G_z
    if mom_rate is not None and yoy_rate is not None and min_mom is not None and max_mom is not None and min_yoy is not None and max_yoy is not None:
        growth_indicator = calculate_growth_indicator(
            mom_rate=mom_rate,
            yoy_rate=yoy_rate,
            min_mom=min_mom,
            max_mom=max_mom,
            min_yoy=min_yoy,
            max_yoy=max_yoy,
            alpha=alpha
        )
        has_growth_data = True
    else:
        growth_indicator = 0.0  # 如果沒有成長資料，設為 0
        has_growth_data = False
    
    # 計算犯罪指標 C_z
    if min_crime_count is not None and max_crime_count is not None:
        crime_indicator = calculate_crime_indicator(
            crime_rate=crime_rate,
            crime_count=crime_count,
            min_crime_rate=min_crime_rate,
            max_crime_rate=max_crime_rate,
            min_crime_count=min_crime_count,
            max_crime_count=max_crime_count,
            use_population=use_population and crime_rate is not None,
            crime_ceiling=crime_ceiling
        )
        has_crime_data = True
    else:
        crime_indicator = 0.0
        has_crime_data = False
    
    # 計算 HCI（論文公式 2）
    # HCI_z = w1 * G_z + w2 * (1 - C_z)
    if has_growth_data and has_crime_data:
        hci_score = w1 * growth_indicator + w2 * (1 - crime_indicator)
    elif has_crime_data:
        # 如果只有犯罪資料，只使用安全部分
        hci_score = w2 * (1 - crime_indicator)
    elif has_growth_data:
        # 如果只有成長資料，只使用成長部分
        hci_score = w1 * growth_indicator
    else:
        hci_score = 0.0
    
    # 轉換為 0-100 範圍（用於顯示）
    hci_score_100 = hci_score * 100
    growth_indicator_100 = growth_indicator * 100
    crime_indicator_100 = crime_indicator * 100
    safety_indicator_100 = (1 - crime_indicator) * 100  # 安全指標（越高越安全）
    
    return {
        'hci_score': round(hci_score, 4),  # HCI 分數 (0-1)
        'hci_score_100': round(hci_score_100, 2),  # HCI 分數 (0-100，用於顯示)
        'growth_indicator': round(growth_indicator, 4),  # 成長指標 (0-1)
        'growth_indicator_100': round(growth_indicator_100, 2),  # 成長指標 (0-100)
        'crime_indicator': round(crime_indicator, 4),  # 犯罪指標 (0-1，越高越危險)
        'crime_indicator_100': round(crime_indicator_100, 2),  # 犯罪指標 (0-100)
        'safety_indicator': round(1 - crime_indicator, 4),  # 安全指標 (0-1，越高越安全)
        'safety_indicator_100': round(safety_indicator_100, 2),  # 安全指標 (0-100)
        'crime_rate_per_1000': round(crime_rate, 2) if crime_rate is not None else None,  # 每 1000 居民犯罪率
        'weights': {
            'w1_growth': w1,
            'w2_safety': w2,
            'alpha_yoy': alpha
        },
        'has_growth_data': has_growth_data,
        'has_crime_data': has_crime_data,
        'has_population_data': population is not None
    }

def calculate_hci_with_custom_weights(
    zip_data: Dict,
    ranges: Dict,
    w1: float = 0.5,
    w2: float = 0.5,
    alpha: float = 0.5
) -> Dict[str, float]:
    """
    使用自定義權重計算 HCI（前端呼叫）
    
    Args:
        zip_data: ZIP Code 的資料字典，包含：
            - mom: MoM 成長率
            - yoy: YoY 成長率
            - crime_count: 犯罪數量
            - population: 人口數（可選）
        ranges: 範圍字典，包含：
            - min_mom, max_mom
            - min_yoy, max_yoy
            - min_crime_count, max_crime_count
            - min_crime_rate, max_crime_rate（可選）
        w1: 成長權重
        w2: 安全權重
        alpha: YoY 權重
    
    Returns:
        HCI 計算結果
    """
    return calculate_hci_paper_formula(
        mom_rate=zip_data.get('mom'),
        yoy_rate=zip_data.get('yoy'),
        crime_count=zip_data.get('crime_count', 0),
        population=zip_data.get('population'),
        min_mom=ranges.get('min_mom'),
        max_mom=ranges.get('max_mom'),
        min_yoy=ranges.get('min_yoy'),
        max_yoy=ranges.get('max_yoy'),
        min_crime_count=ranges.get('min_crime_count'),
        max_crime_count=ranges.get('max_crime_count'),
        min_crime_rate=ranges.get('min_crime_rate'),
        max_crime_rate=ranges.get('max_crime_rate'),
        alpha=alpha,
        w1=w1,
        w2=w2,
        use_population=zip_data.get('population') is not None
    )

if __name__ == "__main__":
    # 測試
    print("測試 HCI 計算...")
    
    # 範例資料
    result = calculate_hci_paper_formula(
        mom_rate=0.05,  # 5% MoM 成長
        yoy_rate=0.10,  # 10% YoY 成長
        crime_count=100,
        population=10000,  # 10,000 居民
        min_mom=-0.1,
        max_mom=0.3,
        min_yoy=-0.2,
        max_yoy=0.5,
        min_crime_count=0,
        max_crime_count=500,
        min_crime_rate=0.0,
        max_crime_rate=50.0,
        alpha=0.5,
        w1=0.6,  # 成長權重 60%
        w2=0.4   # 安全權重 40%
    )
    
    print("\n計算結果:")
    for key, value in result.items():
        print(f"  {key}: {value}")

