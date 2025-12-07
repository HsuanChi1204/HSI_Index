#!/usr/bin/env python3
"""
嘗試從不同來源下載 HouseTS Census Data
"""
import os
import sys
import requests
import pandas as pd
from typing import Optional

def check_kaggle_available():
    """檢查是否可以使用 Kaggle API"""
    try:
        import kaggle
        return True
    except ImportError:
        return False

def download_from_kaggle(dataset_name: str, output_dir: str = ".") -> Optional[str]:
    """
    從 Kaggle 下載資料集
    
    Args:
        dataset_name: Kaggle 資料集名稱（例如：username/dataset-name）
        output_dir: 輸出目錄
    
    Returns:
        下載的檔案路徑，如果失敗則返回 None
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        print(f"正在從 Kaggle 下載: {dataset_name}")
        api.dataset_download_files(dataset_name, path=output_dir, unzip=True)
        
        # 尋找下載的 CSV 檔案
        for file in os.listdir(output_dir):
            if 'census' in file.lower() and file.endswith('.csv'):
                return os.path.join(output_dir, file)
        
        return None
    except Exception as e:
        print(f"❌ Kaggle 下載失敗: {e}")
        return None

def download_from_url(url: str, output_file: str) -> bool:
    """
    從 URL 下載檔案
    
    Args:
        url: 檔案 URL
        output_file: 輸出檔案路徑
    
    Returns:
        是否成功
    """
    try:
        print(f"正在從 URL 下載: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 下載成功: {output_file}")
        return True
    except Exception as e:
        print(f"❌ URL 下載失敗: {e}")
        return False

def check_local_files() -> Optional[str]:
    """
    檢查本地是否已有 Census 資料檔案
    
    Returns:
        檔案路徑，如果不存在則返回 None
    """
    possible_names = [
        'housets_census.csv',
        'HouseTS_Census.csv',
        'census_data.csv',
        'data/housets_census.csv',
        'data/census_data.csv'
    ]
    
    for name in possible_names:
        if os.path.exists(name):
            print(f"✅ 找到本地檔案: {name}")
            return name
    
    return None

def validate_census_data(file_path: str) -> bool:
    """
    驗證 Census 資料格式
    
    Args:
        file_path: CSV 檔案路徑
    
    Returns:
        是否有效
    """
    try:
        df = pd.read_csv(file_path, nrows=5)  # 只讀取前 5 行檢查
        
        # 檢查必要的欄位
        required_fields = [
            'Total Population', 'Per Capita Income', 'Median Rent',
            'Median Home Value', 'Total Housing Units'
        ]
        
        # 檢查 ZIP Code 欄位
        zip_fields = ['zip_code', 'ZIPCode', 'ZIP', 'zipcode', 'ZIP_CODE']
        has_zip = any(field in df.columns for field in zip_fields)
        
        if not has_zip:
            print("❌ 找不到 ZIP Code 欄位")
            return False
        
        # 檢查是否有至少一個必要欄位
        has_required = any(field in df.columns for field in required_fields)
        
        if not has_required:
            print("⚠️  找不到常見的 Census 欄位，但檔案格式可能正確")
        
        print(f"✅ 檔案格式驗證通過")
        print(f"   欄位: {list(df.columns)[:10]}...")  # 顯示前 10 個欄位
        
        return True
    except Exception as e:
        print(f"❌ 檔案驗證失敗: {e}")
        return False

def main():
    """主函數"""
    print("=" * 70)
    print("HouseTS Census Data 下載工具")
    print("=" * 70)
    
    # 步驟 1: 檢查本地檔案
    print("\n1. 檢查本地檔案...")
    local_file = check_local_files()
    if local_file:
        if validate_census_data(local_file):
            print(f"\n✅ 使用本地檔案: {local_file}")
            return local_file
    
    # 步驟 2: 嘗試從 Kaggle 下載
    print("\n2. 嘗試從 Kaggle 下載...")
    if check_kaggle_available():
        # 常見的 HouseTS 資料集名稱（需要根據實際情況調整）
        possible_datasets = [
            "shengkunwang/housets",
            "housets/census-data",
            "housets/dataset"
        ]
        
        for dataset in possible_datasets:
            result = download_from_kaggle(dataset, ".")
            if result and validate_census_data(result):
                return result
    else:
        print("⚠️  Kaggle API 未安裝")
        print("   安裝方式: pip install kaggle")
        print("   然後設定 Kaggle API credentials")
    
    # 步驟 3: 提供手動下載說明
    print("\n3. 手動下載說明")
    print("=" * 70)
    print("如果自動下載失敗，請手動下載 HouseTS Census Data:")
    print("")
    print("方式 1: 從 Kaggle")
    print("  1. 訪問 https://www.kaggle.com")
    print("  2. 搜尋 'HouseTS' 或 'HouseTS dataset'")
    print("  3. 下載 Census 相關的 CSV 檔案")
    print("  4. 將檔案放在專案根目錄，命名為 'housets_census.csv'")
    print("")
    print("方式 2: 從 GitHub")
    print("  1. 搜尋 'HouseTS' GitHub repository")
    print("  2. 檢查 data/ 或 datasets/ 資料夾")
    print("  3. 下載 Census 相關的 CSV 檔案")
    print("")
    print("方式 3: 從 U.S. Census Bureau API")
    print("  1. 訪問 https://www.census.gov/programs-surveys/acs")
    print("  2. 使用 API 取得 DC 地區的 Census 資料")
    print("  3. 轉換為 CSV 格式")
    print("")
    print("詳細說明請參考: docs/HOUSETS_DATA_ACCESS_GUIDE.md")
    print("=" * 70)
    
    return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n✅ 成功取得 Census 資料: {result}")
        print(f"\n下一步: 執行整合腳本")
        print(f"python scripts/combine_data_with_hci.py --housets-census-csv {result}")
    else:
        print(f"\n⚠️  無法自動下載，請參考上述手動下載說明")

