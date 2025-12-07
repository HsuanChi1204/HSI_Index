import pandas as pd
import requests
import time
import json
from datetime import datetime

def process_crime_data_with_api(input_file=None, output_file=None, batch_size=200, resume=True):
    """
    處理犯罪資料，加上 ZIP Code
    
    Args:
        input_file: 輸入檔案路徑
        output_file: 輸出檔案路徑
        batch_size: 每批處理的記錄數（預設 200，可調整）
        resume: 是否從現有檔案繼續處理（預設 True，保留已處理的記錄）
    """
    
    # 設定檔案路徑
    if input_file is None:
        input_file = "DC_Crime_Incidents_2025_08_09.csv"
    if output_file is None:
        output_file = "DC_Crime_Incidents_2025_08_09_with_zipcode.csv"
    
    # 如果輸出檔案存在，先讀取它（保留已處理的記錄）
    import os
    if resume and os.path.exists(output_file):
        print(f"讀取現有輸出檔案: {output_file}")
        df = pd.read_csv(output_file)
        print(f"現有記錄數: {len(df)}")
        
        # 將 ZIP_CODE 轉換為字串類型（處理 float 和 string 混合的情況）
        df['ZIP_CODE'] = df['ZIP_CODE'].astype('object')
        # 將 NaN 和空字串統一處理
        df['ZIP_CODE'] = df['ZIP_CODE'].replace([None, '', 'nan', 'NaN'], None)
        
        # 檢查是否有已處理的記錄
        already_processed = df['ZIP_CODE'].notna().sum()
        print(f"已有 ZIP_CODE 的記錄: {already_processed} ({already_processed/len(df)*100:.1f}%)")
    else:
        # 從原始檔案讀取
        print("Loading Crime Data from original file...")
        df = pd.read_csv(input_file)
        print(f"Total records: {len(df)}")
        
        # Add new columns if not exist
        if 'ZIP_CODE' not in df.columns:
            df['ZIP_CODE'] = None
        if 'PROCESSING_STATUS' not in df.columns:
            df['PROCESSING_STATUS'] = 'pending'  # pending, success, failed
        if 'PROCESSING_ERROR' not in df.columns:
            df['PROCESSING_ERROR'] = None
        if 'CITY' not in df.columns:
            df['CITY'] = None
        if 'STATE' not in df.columns:
            df['STATE'] = None
    
    # 確保所有必要的欄位都存在，並設定正確的資料類型
    if 'ZIP_CODE' not in df.columns:
        df['ZIP_CODE'] = None
    # 將 ZIP_CODE 轉換為字串類型（避免類型警告）
    df['ZIP_CODE'] = df['ZIP_CODE'].astype('object')
    
    if 'PROCESSING_STATUS' not in df.columns:
        df['PROCESSING_STATUS'] = 'pending'
    if 'PROCESSING_ERROR' not in df.columns:
        df['PROCESSING_ERROR'] = None
    if 'CITY' not in df.columns:
        df['CITY'] = None
    if 'STATE' not in df.columns:
        df['STATE'] = None
    
    # 取得需要處理的記錄（有經緯度但還沒有 ZIP_CODE 的）
    # 檢查 ZIP_CODE 是否為空（處理 float64 類型的 NaN 值）
    mask = (df['LATITUDE'].notna()) & (df['LONGITUDE'].notna())
    # 對於 float64 類型，使用 isna() 來檢查 NaN
    if df['ZIP_CODE'].dtype == 'float64':
        mask = mask & df['ZIP_CODE'].isna()
    else:
        mask = mask & (df['ZIP_CODE'].isna() | (df['ZIP_CODE'] == ''))
    
    valid_records = df[mask]
    
    print(f"需要處理的記錄: {len(valid_records)}")
    
    if len(valid_records) == 0:
        print("所有記錄都已處理完成！")
        return df
    
    # Load progress file to get statistics
    progress_file = "processing_progress.json"
    progress = load_progress(progress_file)
    total_success = progress.get('total_success', 0)
    total_failed = progress.get('total_failed', 0)
    
    # 處理所有需要處理的記錄
    total_remaining = len(valid_records)
    
    print(f"將處理 {total_remaining} 筆記錄，每批 {batch_size} 筆")
    
    # 批次處理
    processed_count = 0
    batch_num = 0
    for batch_start in range(0, total_remaining, batch_size):
        batch_end = min(batch_start + batch_size, total_remaining)
        batch_records = valid_records.iloc[batch_start:batch_end]
        batch_indices = batch_records.index.tolist()
        
        batch_num += 1
        print(f"\n處理批次 {batch_num}: 記錄 {batch_start + 1} 到 {batch_end} (共 {len(batch_indices)} 筆)")
        
        # Process this batch of records
        batch_success, batch_failed = process_batch(df, batch_indices)
        
        total_success += batch_success
        total_failed += batch_failed
        processed_count += len(batch_indices)
        
        # 儲存進度
        total_processed = df['ZIP_CODE'].notna().sum()
        save_progress(df, progress_file, total_processed, total_success, total_failed)
        
        # 每批處理後儲存結果（避免資料遺失）
        df.to_csv(output_file, index=False)
        print(f"✅ 已儲存進度至: {output_file}")
        print(f"   目前進度: {processed_count}/{total_remaining} ({processed_count/total_remaining*100:.1f}%)")
        print(f"   本批成功: {batch_success}, 失敗: {batch_failed}")
        print(f"   累計成功: {total_success}, 累計失敗: {total_failed}")
    
    print(f"\n=== 處理完成 ===")
    print(f"本次處理記錄: {processed_count}")
    print(f"累計成功: {total_success}")
    print(f"累計失敗: {total_failed}")
    if processed_count > 0:
        print(f"本次成功率: {total_success/processed_count*100:.1f}%")
    
    # 最終統計
    final_with_zip = df['ZIP_CODE'].notna().sum()
    print(f"\n最終統計:")
    print(f"總記錄數: {len(df)}")
    print(f"已有 ZIP_CODE: {final_with_zip} ({final_with_zip/len(df)*100:.1f}%)")
    print(f"結果已儲存至: {output_file}")
    
    return df

def process_batch(df, batch_indices):
    """
    Process a batch of records (max 500 records)
    """
    success_count = 0
    failed_count = 0
    
    for i, idx in enumerate(batch_indices):
        row = df.loc[idx]
        lat = row['LATITUDE']
        lon = row['LONGITUDE']
        
        print(f"  處理 {i+1}/{len(batch_indices)}: 記錄 {idx}")
        
        try:
            # 呼叫 API
            result = get_zipcode_from_api(lat, lon)
            
            if result and result['success']:
                df.at[idx, 'ZIP_CODE'] = result['zipcode']
                df.at[idx, 'CITY'] = result['city']
                df.at[idx, 'STATE'] = result['state']
                df.at[idx, 'PROCESSING_STATUS'] = 'success'
                df.at[idx, 'PROCESSING_ERROR'] = None
                success_count += 1
                print(f"    ✅ 成功: {result['zipcode']}")
            else:
                df.at[idx, 'PROCESSING_STATUS'] = 'failed'
                df.at[idx, 'PROCESSING_ERROR'] = result['error'] if result else 'API 無回應'
                failed_count += 1
                print(f"    ❌ 失敗: {result['error'] if result else 'API 無回應'}")
                
        except Exception as e:
            df.at[idx, 'PROCESSING_STATUS'] = 'failed'
            df.at[idx, 'PROCESSING_ERROR'] = str(e)
            failed_count += 1
            print(f"    ❌ 錯誤: {e}")
        
        # API 請求間隔（減少到 0.05 秒以加快處理，但要注意 API 限制）
        time.sleep(0.05)
    
    return success_count, failed_count

def get_zipcode_from_api(lat, lon):
    """
    使用 Nominatim API 獲取 ZIP Code
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {'User-Agent': 'DC_Crime_Analysis_Tool/1.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            postcode = address.get('postcode')
            
            if postcode and postcode.startswith('200') and len(postcode) == 5:
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
                    'error': f'非 DC ZIP Code: {postcode}'
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

def load_progress(progress_file):
    """
    載入進度檔案
    """
    try:
        with open(progress_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'last_updated': None
        }

def save_progress(df, progress_file, total_processed, total_success, total_failed):
    """
    Save progress to progress file
    """
    # 轉換為 Python 原生類型（避免 JSON 序列化錯誤）
    progress = {
        'total_processed': int(total_processed) if total_processed is not None else 0,
        'total_success': int(total_success) if total_success is not None else 0,
        'total_failed': int(total_failed) if total_failed is not None else 0,
        'last_updated': datetime.now().isoformat(),
        'success_rate': float(total_success / total_processed * 100) if total_processed and total_processed > 0 else 0.0
    }
    
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)
    
    print(f"進度已儲存: {progress_file}")

# def show_status():
#     """
#     顯示當前處理狀態
#     """
#     try:
#         df = pd.read_csv("data/processed/DC_Crime_Incidents_2025_08_09_with_zipcode.csv")
        
#         if 'PROCESSING_STATUS' in df.columns:
#             status_counts = df['PROCESSING_STATUS'].value_counts()
#             print("=== 當前處理狀態 ===")
#             print(status_counts)
            
#             if 'ZIP_CODE' in df.columns:
#                 success_records = df[df['PROCESSING_STATUS'] == 'success']
#                 if len(success_records) > 0:
#                     zipcode_counts = success_records['ZIP_CODE'].value_counts()
#                     print(f"\n=== ZIP Code 分布 (前 10 名) ===")
#                     print(zipcode_counts.head(10))
        
#         # 載入進度檔案
#         try:
#             with open("processing_progress.json", 'r') as f:
#                 progress = json.load(f)
#             print(f"\n=== 進度統計 ===")
#             print(f"總處理: {progress['total_processed']}")
#             print(f"成功: {progress['total_success']}")
#             print(f"失敗: {progress['total_failed']}")
#             print(f"成功率: {progress['success_rate']:.1f}%")
#             print(f"最後更新: {progress['last_updated']}")
#         except FileNotFoundError:
#             print("進度檔案不存在")
            
#     except FileNotFoundError:
#         print("資料檔案不存在")

if __name__ == "__main__":
    import sys
    
    # 檢查是否要從上次進度繼續
    resume = '--resume' in sys.argv
    
    # 處理所有記錄
    result_df = process_crime_data_with_api(
        input_file="DC_Crime_Incidents_2025_08_09.csv",
        output_file="DC_Crime_Incidents_2025_08_09_with_zipcode.csv",
        batch_size=200,  # 每批處理 200 筆（加快處理速度）
        resume=True  # 預設從現有檔案繼續，保留已處理的記錄
    )
