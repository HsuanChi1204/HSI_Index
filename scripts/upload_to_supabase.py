#!/usr/bin/env python3
"""
上傳 DC Crime 資料到 Supabase
對應任務: Upload DC crime data to Supabase
"""
import pandas as pd
import numpy as np
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def upload_to_supabase():
    """
    上傳 Crime 資料到 Supabase
    """
    print("=" * 70)
    print("上傳 DC Crime 資料到 Supabase")
    print("=" * 70)
    
    # 取得 Supabase 連線資訊
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ 錯誤: 需要設定 Supabase 環境變數")
        print("\n請在 .env 檔案中設定:")
        print("  SUPABASE_URL=your-project-url")
        print("  SUPABASE_KEY=your-anon-key")
        print("\n或設定環境變數:")
        print("  export SUPABASE_URL='your-project-url'")
        print("  export SUPABASE_KEY='your-anon-key'")
        return False
    
    try:
        # 建立 Supabase 客戶端
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ 已連線到 Supabase")
        
        # 讀取 Crime 資料
        print("\n1. 讀取 Crime 資料...")
        df = pd.read_csv('DC_Crime_Incidents_in_2025_with_zipcode_nominatim.csv')
        
        # 只保留有 ZIP_CODE 的記錄
        df = df[df['ZIP_CODE'].notna()].copy()
        print(f"   總記錄數: {len(df)}")
        
        # 選擇要上傳的欄位
        columns_to_upload = [
            'CCN', 'REPORT_DAT', 'SHIFT', 'METHOD', 'OFFENSE', 'BLOCK',
            'WARD', 'ANC', 'DISTRICT', 'PSA', 'NEIGHBORHOOD_CLUSTER',
            'LATITUDE', 'LONGITUDE', 'ZIP_CODE', 'X', 'Y'
        ]
        
        df_upload = df[columns_to_upload].copy()
        
        # 重新命名欄位（符合資料庫命名慣例）
        df_upload.columns = [
            'ccn', 'report_dat', 'shift', 'method', 'offense', 'block',
            'ward', 'anc', 'district', 'psa', 'neighborhood_cluster',
            'latitude', 'longitude', 'zip_code', 'x_coord', 'y_coord'
        ]
        
        # Deduplicate based on 'ccn' to avoid upsert errors
        df_upload = df_upload.drop_duplicates(subset=['ccn'], keep='first')
        
        # 轉換資料類型
        df_upload['zip_code'] = df_upload['zip_code'].astype(int).astype(str)

        df_upload['report_dat'] = pd.to_datetime(df_upload['report_dat'], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        # Replace NaT with None
        df_upload['report_dat'] = df_upload['report_dat'].replace({np.nan: None})
        
        # 處理 NaN 值
        df_upload = df_upload.fillna('')
        
        # 轉換為字典列表
        records = df_upload.to_dict('records')
        
        print(f"\n2. 上傳資料到 Supabase...")
        print(f"   準備上傳 {len(records)} 筆記錄")
        
        # 批次上傳（Supabase 建議每次最多 1000 筆）
        batch_size = 1000
        total_uploaded = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                # 使用 upsert 避免重複
                result = supabase.table('crimes').upsert(
                    batch,
                    on_conflict='ccn'  # 如果 CCN 已存在則更新
                ).execute()
                
                total_uploaded += len(batch)
                print(f"   已上傳: {total_uploaded}/{len(records)} ({total_uploaded/len(records)*100:.1f}%)")
                
            except Exception as e:
                print(f"   ⚠️  批次 {i//batch_size + 1} 上傳失敗: {e}")
                # 嘗試逐筆上傳
                for record in batch:
                    try:
                        supabase.table('crimes').upsert(record, on_conflict='ccn').execute()
                        total_uploaded += 1
                    except Exception as e2:
                        print(f"      ⚠️  記錄 {record.get('ccn', 'unknown')} 上傳失敗: {e2}")
        
        print(f"\n✅ 上傳完成！")
        print(f"   總共上傳: {total_uploaded} 筆記錄")
        
        return True
        
    except Exception as e:
        print(f"❌ 上傳失敗: {e}")
        print(f"\n請確認:")
        print(f"  1. 已安裝 supabase-py: pip install supabase")
        print(f"  2. Supabase 專案已建立")
        print(f"  3. 已建立 'crimes' 表")
        print(f"  4. 已設定正確的環境變數")
        return False

def upload_zillow_to_supabase():
    """
    Upload Zillow data to Supabase
    """
    print("=" * 70)
    print("Upload Zillow Data to Supabase")
    print("=" * 70)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        return False
        
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("\n1. Reading Zillow Data...")
        # Assuming the file name, should be configurable or found dynamically
        zillow_file = 'dc_zillow_2025_09_30.csv'
        if not os.path.exists(zillow_file):
            print(f"❌ Zillow file not found: {zillow_file}")
            return False
            
        df = pd.read_csv(zillow_file)
        print(f"   Total records: {len(df)}")
        
        # Rename columns to match database schema (snake_case)
        # Assuming table 'zillow_data' exists with columns:
        # region_id, size_rank, region_name, region_type, state_name, state, city, metro, county_name,
        # zip_code, mom, yoy, current_price, created_at
        
        df_upload = df.rename(columns={
            'RegionName': 'region_name',
            'State': 'state',
            'Metro': 'metro',
            'CountyName': 'county_name',
            'ZIPCode': 'zip_code',
            'MOM': 'mom',
            'YOY': 'yoy',
            'CurrentPrice': 'current_price'
        })
        
        # Use ZIPCode as region_id since it's unique in this dataset
        df_upload['region_id'] = df_upload['zip_code']
        
        # Add missing columns with None
        for col in ['size_rank', 'region_type', 'state_name', 'city']:
            df_upload[col] = None
            
        # Drop rows where region_id is missing (Primary Key)
        df_upload = df_upload.dropna(subset=['region_id'])
        
        # Clean data
        df_upload = df_upload.where(pd.notnull(df_upload), None)
        df_upload['zip_code'] = df_upload['zip_code'].astype(str)
        
        records = df_upload.to_dict('records')
        
        print(f"\n2. Uploading {len(records)} records to Supabase...")
        
        batch_size = 1000
        total_uploaded = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                supabase.table('zillow_data').upsert(batch, on_conflict='region_id').execute()
                total_uploaded += len(batch)
                print(f"   Uploaded: {total_uploaded}/{len(records)}")
            except Exception as e:
                print(f"   ⚠️ Batch failed: {e}")
                
        print(f"\n✅ Zillow upload complete!")
        return True
        
    except Exception as e:
        print(f"❌ Zillow upload failed: {e}")
        return False

def setup_supabase_instructions():
    """顯示 Supabase 設定說明"""
    print("\n" + "=" * 70)
    print("Supabase 設定說明")
    print("=" * 70)
    print("""
1. 建立 Supabase 專案:
   - 前往 https://supabase.com
   - 建立新專案
   - 取得 Project URL 和 anon key

2. 建立 crimes 表（在 Supabase SQL Editor 執行）:
   
   CREATE TABLE crimes (
       id BIGSERIAL PRIMARY KEY,
       ccn VARCHAR(50) UNIQUE NOT NULL,
       report_dat TIMESTAMPTZ,
       shift VARCHAR(20),
       method VARCHAR(50),
       offense VARCHAR(100),
       block TEXT,
       ward VARCHAR(10),
       anc VARCHAR(10),
       district VARCHAR(10),
       psa VARCHAR(10),
       neighborhood_cluster VARCHAR(50),
       latitude DECIMAL(10, 8),
       longitude DECIMAL(11, 8),
       zip_code VARCHAR(5),
       x_coord DECIMAL(12, 6),
       y_coord DECIMAL(12, 6),
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- 建立索引
   CREATE INDEX idx_crimes_zip_code ON crimes(zip_code);
   CREATE INDEX idx_crimes_offense ON crimes(offense);
   CREATE INDEX idx_crimes_date ON crimes(report_dat);
   CREATE INDEX idx_crimes_ccn ON crimes(ccn);

   -- Create zillow_data table
   CREATE TABLE zillow_data (
       region_id BIGINT PRIMARY KEY,
       size_rank INT,
       region_name VARCHAR(100),
       region_type VARCHAR(50),
       state_name VARCHAR(50),
       state VARCHAR(10),
       city VARCHAR(100),
       metro VARCHAR(100),
       county_name VARCHAR(100),
       zip_code VARCHAR(10),
       mom DECIMAL(10, 4),
       yoy DECIMAL(10, 4),
       current_price DECIMAL(15, 2),
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   CREATE INDEX idx_zillow_zip_code ON zillow_data(zip_code);

3. 設定環境變數:
   在 .env 檔案中:
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key

4. 安裝套件:
   pip install supabase python-dotenv

5. 執行上傳:
   python upload_to_supabase.py
    """)

if __name__ == "__main__":
    if not os.path.exists('DC_Crime_Incidents_2025_08_09_with_zipcode.csv'):
        print("❌ 找不到 Crime 資料檔案")
        print("請確認 DC_Crime_Incidents_2025_08_09_with_zipcode.csv 存在")
        sys.exit(1)
    
    # Try to load .env from root or backend
    load_dotenv()
    if not os.getenv('SUPABASE_URL'):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))

    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        setup_supabase_instructions()
        print("\n請先設定環境變數後再執行")
    else:
        print("\n--- Uploading Crime Data ---")
        upload_to_supabase()
        print("\n--- Uploading Zillow Data ---")
        upload_zillow_to_supabase()

