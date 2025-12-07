#!/usr/bin/env python3
"""
上傳 JSON 檔案到 GCP Cloud Storage
對應任務: AS-6 - Store json file into GCP cloud storage
"""
import os
from google.cloud import storage
from google.oauth2 import service_account
import json

def upload_to_gcp_storage(
    json_file_path='frontend_data.json',
    bucket_name='dc-crime-data-zhangxuanqi-1762814591',
    credentials_path=None
):
    """
    上傳 JSON 檔案到 GCP Cloud Storage
    
    Args:
        json_file_path: 要上傳的 JSON 檔案路徑
        bucket_name: GCP Storage bucket 名稱
        credentials_path: GCP 服務帳號憑證檔案路徑（JSON）
    """
    print("=" * 70)
    print("上傳 JSON 檔案到 GCP Cloud Storage")
    print("=" * 70)
    
    # 檢查檔案是否存在
    if not os.path.exists(json_file_path):
        print(f"❌ 錯誤: 找不到檔案 {json_file_path}")
        return False
    
    # 設定 bucket 名稱（如果未提供，使用環境變數或提示）
    if not bucket_name:
        bucket_name = os.getenv('GCP_BUCKET_NAME')
        if not bucket_name:
            bucket_name = input("請輸入 GCP Storage bucket 名稱: ").strip()
    
    if not bucket_name:
        print("❌ 錯誤: 需要提供 bucket 名稱")
        return False
    
    try:
        # 初始化 Storage 客戶端
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            storage_client = storage.Client(credentials=credentials)
        else:
            # 使用預設憑證（從環境變數或 gcloud 設定）
            storage_client = storage.Client()
        
        # 取得 bucket
        bucket = storage_client.bucket(bucket_name)
        
        # 上傳檔案
        blob_name = f"data/{os.path.basename(json_file_path)}"
        blob = bucket.blob(blob_name)
        
        print(f"\n上傳檔案...")
        print(f"  檔案: {json_file_path}")
        print(f"  Bucket: {bucket_name}")
        print(f"  Blob: {blob_name}")
        
        blob.upload_from_filename(json_file_path)
        
        # 設定公開讀取權限（如果需要）
        # blob.make_public()
        
        # 取得公開 URL
        public_url = blob.public_url
        gs_url = f"gs://{bucket_name}/{blob_name}"
        
        print(f"\n✅ 上傳成功！")
        print(f"   GS URL: {gs_url}")
        print(f"   公開 URL: {public_url}")
        print(f"\n前端可以使用以下方式存取:")
        print(f"   fetch('{public_url}')")
        
        return True
        
    except Exception as e:
        print(f"❌ 上傳失敗: {e}")
        print(f"\n請確認:")
        print(f"  1. 已安裝 google-cloud-storage: pip install google-cloud-storage")
        print(f"  2. 已設定 GCP 憑證（環境變數 GOOGLE_APPLICATION_CREDENTIALS 或提供 credentials_path）")
        print(f"  3. 有 bucket 的寫入權限")
        return False

def setup_gcp_instructions():
    """顯示 GCP 設定說明"""
    print("\n" + "=" * 70)
    print("GCP Cloud Storage 設定說明")
    print("=" * 70)
    print("""
1. 建立 Storage Bucket:
   gcloud storage buckets create gs://your-bucket-name --location=us-central1

2. 設定服務帳號（選項 A - 使用服務帳號）:
   - 在 GCP Console 建立服務帳號
   - 下載 JSON 憑證檔案
   - 設定環境變數: export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

3. 設定服務帳號（選項 B - 使用 gcloud）:
   gcloud auth application-default login

4. 安裝 Python 套件:
   pip install google-cloud-storage

5. 執行上傳:
   python upload_to_gcp_storage.py
    """)

if __name__ == "__main__":
    import sys
    
    # 檢查參數
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'frontend_data.json'
    bucket_name = sys.argv[2] if len(sys.argv) > 2 else 'dc-crime-data-zhangxuanqi-1762814591'
    credentials_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(json_file):
        print(f"❌ 找不到檔案: {json_file}")
        print("\n請先執行 combine_data_to_json.py 生成 JSON 檔案")
        setup_gcp_instructions()
        sys.exit(1)
    
    upload_to_gcp_storage(json_file, bucket_name, credentials_path)

