# 專案結構說明

## 📁 目錄結構

```
Adv_Spatial_HCI/
├── data/                          # 資料檔案（建議建立）
│   ├── DC_Crime_Incidents_2025_08_09.csv
│   ├── DC_Crime_Incidents_2025_08_09_with_zipcode.csv
│   ├── dc_zillow_2025_09_30.csv
│   └── dc_crime_zillow_combined.json
│
├── docs/                          # 文件檔案
│   ├── API_ARCHITECTURE_PLAN.md          # API 架構設計方案
│   ├── api_implementation_guide.md        # API 實作指南
│   ├── FIX_BILLING_ISSUE.md              # 計費問題修正指南
│   ├── GCP_STORAGE_GUIDE.md              # GCP Storage 使用指南
│   ├── GCP_STORAGE_SETUP_GUIDE.md        # GCP Storage 設定指南
│   ├── HYBRID_ARCHITECTURE_PLAN.md       # 混合架構方案
│   ├── NEXT_STEPS.md                     # 下一步指南
│   ├── PROJECT_STRUCTURE.md              # 本檔案
│   ├── SETUP_COMPLETE.md                 # 設定完成報告
│   └── STEP_BY_STEP_SETUP.md             # 逐步設定指南
│
├── scripts/                       # 腳本檔案
│   ├── add_zipcode_to_crime_data.py      # 加入 ZIP Code（舊版，不完整）
│   ├── batch_process_zipcode.py          # 批次處理 ZIP Code（主要使用）
│   ├── combine_data_to_json.py           # 合併資料成 JSON
│   ├── complete_setup.sh                  # 完成 GCP 設定腳本
│   ├── fix_gcloud_setup.sh               # 修正 gcloud 設定
│   ├── link_billing_and_setup.sh         # 連結計費並設定
│   ├── monitor_processing.py              # 監控處理進度
│   ├── setup_gcp_quick.sh                # GCP 快速設定腳本
│   └── upload_to_gcp_storage.py          # 上傳到 GCP Storage
│   └── upload_to_supabase.py             # 上傳到 Supabase
│
├── frontend/                      # 前端範例
│   ├── angular-example.service.ts        # Angular Service 範例
│   ├── angular-example.component.ts      # Angular Component 範例
│   └── test-angular.html                  # HTML 測試頁面
│
├── venv/                          # Python 虛擬環境
├── .bucket_name.txt              # Bucket 名稱（自動生成）
├── .public_url.txt               # 公開 URL（自動生成）
├── cors.json                     # CORS 設定（自動生成）
├── processing_progress.json      # 處理進度（自動生成）
└── requirements.txt              # Python 依賴（建議建立）
```

---

## 📂 各目錄說明

### `docs/` - 文件檔案

包含所有說明文件：
- **架構設計**: API 和混合架構方案
- **設定指南**: GCP、Supabase 設定步驟
- **問題排除**: 常見問題解決方案
- **使用指南**: 如何使用各項功能

### `scripts/` - 腳本檔案

包含所有 Python 和 Shell 腳本：
- **資料處理**: 處理 CSV、生成 JSON
- **上傳腳本**: 上傳到 GCP、Supabase
- **設定腳本**: 自動化設定流程
- **監控腳本**: 監控處理進度

### `frontend/` - 前端範例

包含前端整合範例：
- **Angular**: Service 和 Component 範例
- **HTML**: 簡單的測試頁面

---

## 🔧 主要腳本說明

### 資料處理

1. **`batch_process_zipcode.py`** ⭐
   - 主要使用的腳本
   - 批次處理 Crime 資料，加入 ZIP Code
   - 支援從現有檔案繼續處理

2. **`combine_data_to_json.py`**
   - 合併 Crime 和 Zillow 資料成 JSON
   - 按 ZIP Code 組織資料
   - 生成前端可用的 JSON 檔案

### 上傳腳本

3. **`upload_to_gcp_storage.py`**
   - 上傳 JSON 檔案到 GCP Cloud Storage
   - 設定公開讀取權限

4. **`upload_to_supabase.py`**
   - 上傳 Crime 資料到 Supabase
   - 供 AI Agent 使用

### 設定腳本

5. **`setup_gcp_quick.sh`**
   - 一鍵完成 GCP Storage 設定
   - 自動建立 bucket、設定 CORS、上傳檔案

6. **`link_billing_and_setup.sh`**
   - 連結計費帳戶並完成設定

---

## 📊 資料流程

```
原始 CSV 檔案
    ↓
batch_process_zipcode.py (加入 ZIP Code)
    ↓
DC_Crime_Incidents_2025_08_09_with_zipcode.csv
    ↓
combine_data_to_json.py (合併資料)
    ↓
dc_crime_zillow_combined.json
    ↓
    ├─→ upload_to_gcp_storage.py → GCP Storage (前端使用)
    └─→ upload_to_supabase.py → Supabase (AI Agent 使用)
```

---

## 🚀 快速開始

### 1. 處理資料

```bash
# 加入 ZIP Code
python scripts/batch_process_zipcode.py

# 合併成 JSON
python scripts/combine_data_to_json.py
```

### 2. 上傳到 GCP

```bash
# 快速設定（推薦）
./scripts/setup_gcp_quick.sh

# 或手動上傳
python scripts/upload_to_gcp_storage.py dc_crime_zillow_combined.json BUCKET_NAME
```

### 3. 上傳到 Supabase

```bash
python scripts/upload_to_supabase.py
```

---

## 📝 建議的改進

1. **建立 `data/` 資料夾**
   - 將所有 CSV 和 JSON 檔案移到 `data/` 資料夾
   - 保持根目錄整潔

2. **建立 `requirements.txt`**
   ```txt
   pandas>=2.0.0
   requests>=2.31.0
   google-cloud-storage>=2.10.0
   supabase>=2.0.0
   python-dotenv>=1.0.0
   ```

3. **建立 `.gitignore`**
   ```
   venv/
   __pycache__/
   *.pyc
   .env
   credentials.json
   *.log
   .bucket_name.txt
   .public_url.txt
   processing_progress.json
   ```

4. **建立 `README.md`**
   - 專案說明
   - 快速開始指南
   - 資料流程說明

---

## 🔗 相關文件

- **GCP Storage 使用**: `docs/GCP_STORAGE_GUIDE.md`
- **設定完成報告**: `docs/SETUP_COMPLETE.md`
- **架構方案**: `docs/HYBRID_ARCHITECTURE_PLAN.md`

