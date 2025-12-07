# DC Crime & Zillow Data Processing Project

## 📋 專案簡介

這個專案用於處理和整合 DC 犯罪資料（DC Crime）和房價資料（Zillow），並提供給前端應用和 AI Agent 使用。

## 🏗️ 專案架構

### 資料流程

```
原始 CSV 檔案
    ↓
批次處理 ZIP Code (batch_process_zipcode.py)
    ↓
DC_Crime_Incidents_2025_08_09_with_zipcode.csv
    ↓
合併資料成 JSON (combine_data_to_json.py)
    ↓
dc_crime_zillow_combined.json
    ↓
    ├─→ GCP Cloud Storage (前端使用)
    └─→ Supabase (AI Agent 使用)
```

### 架構方案

- **前端**: 從 GCP Cloud Storage 讀取 JSON 檔案
- **AI Agent**: 從 Supabase PostgreSQL 查詢資料

## 📁 專案結構

```
Adv_Spatial_HCI/
├── docs/              # 文件檔案
├── scripts/           # 處理腳本
├── frontend/          # 前端範例
├── data/             # 資料檔案（建議）
└── venv/             # Python 虛擬環境
```

詳細結構請參考：`docs/PROJECT_STRUCTURE.md`

## 🚀 快速開始

### 1. 環境設定

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 處理資料

```bash
# 加入 ZIP Code 到 Crime 資料
python scripts/batch_process_zipcode.py

# 合併 Crime 和 Zillow 資料成 JSON
python scripts/combine_data_to_json.py
```

### 3. 上傳到 GCP Storage

```bash
# 快速設定（推薦）
./scripts/setup_gcp_quick.sh

# 或手動上傳
python scripts/upload_to_gcp_storage.py dc_crime_zillow_combined.json BUCKET_NAME
```

### 4. 上傳到 Supabase

```bash
python scripts/upload_to_supabase.py
```

## 📊 資料統計

- **Crime 資料**: 3,872 筆記錄
- **成功加入 ZIP Code**: 3,573 筆 (92.3%)
- **Zillow 資料**: 22 筆 ZIP Code
- **JSON 檔案大小**: ~1.5 MB

## 🔗 重要連結

### GCP Storage

- **Bucket**: `gs://dc-crime-data-zhangxuanqi-1762814591`
- **公開 URL**: `https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json`
- **GCP Console**: https://console.cloud.google.com/storage/browser/dc-crime-data-zhangxuanqi-1762814591

### 前端使用

請參考 `frontend/` 資料夾中的範例：
- `angular-example.service.ts` - Angular Service
- `angular-example.component.ts` - Angular Component
- `test-angular.html` - HTML 測試頁面

## 📚 文件

所有文件都在 `docs/` 資料夾中：

- `PROJECT_STRUCTURE.md` - 專案結構說明
- `GCP_STORAGE_GUIDE.md` - GCP Storage 使用指南
- `HYBRID_ARCHITECTURE_PLAN.md` - 架構方案說明
- `STEP_BY_STEP_SETUP.md` - 逐步設定指南

## 💰 成本

- **GCP Storage**: $0/月（免費額度內）
- **Supabase**: $0/月（免費層）

## 🛠️ 主要腳本

- `batch_process_zipcode.py` - 批次處理 ZIP Code
- `combine_data_to_json.py` - 合併資料成 JSON
- `upload_to_gcp_storage.py` - 上傳到 GCP
- `upload_to_supabase.py` - 上傳到 Supabase

## 📝 注意事項

1. 確保已設定 GCP 計費帳戶（免費額度內不會收費）
2. 確保已設定 Supabase 環境變數
3. JSON 檔案已設定為公開讀取
4. CORS 已設定，允許前端跨域讀取

## 🔄 資料更新流程

1. 更新 CSV 資料
2. 執行 `batch_process_zipcode.py`
3. 執行 `combine_data_to_json.py`
4. 執行 `upload_to_gcp_storage.py`
5. 執行 `upload_to_supabase.py`

## 📞 支援

如有問題，請參考 `docs/` 資料夾中的相關文件。

