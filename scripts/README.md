# Scripts 資料夾說明

## 📋 腳本分類

### 資料處理腳本

1. **batch_process_zipcode.py** ⭐
   - 主要使用的腳本
   - 批次處理 Crime 資料，加入 ZIP Code
   - 使用方式: `python scripts/batch_process_zipcode.py`

2. **combine_data_to_json.py**
   - 合併 Crime 和 Zillow 資料成 JSON
   - 使用方式: `python scripts/combine_data_to_json.py`

### 上傳腳本

3. **upload_to_gcp_storage.py**
   - 上傳 JSON 檔案到 GCP Cloud Storage
   - 使用方式: `python scripts/upload_to_gcp_storage.py <json_file> <bucket_name>`

4. **upload_to_supabase.py**
   - 上傳 Crime 資料到 Supabase
   - 使用方式: `python scripts/upload_to_supabase.py`

### 設定腳本

5. **setup_gcp_quick.sh** ⭐
   - 一鍵完成 GCP Storage 設定
   - 使用方式: `./scripts/setup_gcp_quick.sh`

6. **link_billing_and_setup.sh**
   - 連結計費帳戶並完成設定
   - 使用方式: `./scripts/link_billing_and_setup.sh`

7. **complete_setup.sh**
   - 完成 GCP Storage 設定的剩餘步驟
   - 使用方式: `./scripts/complete_setup.sh`

8. **fix_gcloud_setup.sh**
   - 修正 gcloud 設定問題
   - 使用方式: `./scripts/fix_gcloud_setup.sh`

### 監控腳本

9. **monitor_processing.py**
   - 監控資料處理進度
   - 使用方式: `python scripts/monitor_processing.py`

10. **check_progress.sh**
    - 檢查處理進度
    - 使用方式: `./scripts/check_progress.sh`

## ⚠️ 注意事項

所有腳本都假設從專案根目錄執行，例如：

```bash
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
python scripts/batch_process_zipcode.py
./scripts/setup_gcp_quick.sh
```

如果從其他目錄執行，請調整相對路徑。
