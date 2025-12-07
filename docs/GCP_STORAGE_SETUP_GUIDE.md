# GCP Cloud Storage 設定指南

## 📋 前置準備

### 1. 確認 GCP 專案

如果您還沒有 GCP 專案：

```bash
# 登入 GCP
gcloud auth login

# 建立新專案（或使用現有專案）
gcloud projects create dc-crime-data --name="DC Crime Data"

# 設定預設專案
gcloud config set project dc-crime-data

# 啟用計費（需要信用卡，但免費額度內不會收費）
# 前往 https://console.cloud.google.com/billing 連結帳單
```

### 2. 啟用 Cloud Storage API

```bash
# 啟用 Cloud Storage API
gcloud services enable storage-component.googleapis.com
```

或者前往 [GCP Console](https://console.cloud.google.com/apis/library/storage-component.googleapis.com) 啟用。

---

## 🪣 步驟 1: 建立 Storage Bucket

### 方法 A: 使用 gcloud CLI（推薦）

```bash
# 建立 bucket（選擇一個唯一的 bucket 名稱）
BUCKET_NAME="dc-crime-data-$(date +%s)"  # 使用時間戳記確保唯一性
# 或直接指定名稱
BUCKET_NAME="dc-crime-data-your-name"

# 建立 bucket（選擇離您最近的區域）
gcloud storage buckets create gs://$BUCKET_NAME \
  --location=us-central1 \
  --project=dc-crime-data

# 確認 bucket 已建立
gcloud storage buckets list
```

### 方法 B: 使用 GCP Console

1. 前往 [Cloud Storage Console](https://console.cloud.google.com/storage)
2. 點擊「建立儲存區」
3. 設定：
   - **名稱**: `dc-crime-data-your-name`（必須全球唯一）
   - **位置類型**: 區域
   - **位置**: 選擇離您最近的區域（如 `us-central1`）
   - **儲存類別**: Standard
   - **存取控制**: Uniform
4. 點擊「建立」

---

## 🔐 步驟 2: 設定認證

### 選項 A: 使用 gcloud（最簡單，適合開發）

```bash
# 設定應用程式預設憑證
gcloud auth application-default login

# 這會開啟瀏覽器讓您登入
# 完成後，腳本會自動使用這個認證
```

**優點**: 
- ✅ 最簡單
- ✅ 不需要管理憑證檔案
- ✅ 適合本地開發

**缺點**:
- ⚠️ 不適合生產環境
- ⚠️ 需要每次登入

### 選項 B: 使用服務帳號（適合生產環境）

```bash
# 建立服務帳號
gcloud iam service-accounts create storage-uploader \
  --display-name="Storage Uploader" \
  --description="Service account for uploading JSON files"

# 取得專案 ID
PROJECT_ID=$(gcloud config get-value project)

# 授予 Storage 權限
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:storage-uploader@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# 建立並下載憑證
gcloud iam service-accounts keys create credentials.json \
  --iam-account=storage-uploader@$PROJECT_ID.iam.gserviceaccount.com

# 設定環境變數
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
```

**優點**:
- ✅ 適合生產環境
- ✅ 可以設定精細權限
- ✅ 不需要每次登入

**缺點**:
- ⚠️ 需要管理憑證檔案
- ⚠️ 需要保護憑證安全

---

## 📦 步驟 3: 安裝 Python 套件

```bash
# 確保在虛擬環境中
source venv/bin/activate

# 安裝 Google Cloud Storage 套件
pip install google-cloud-storage
```

---

## ⚙️ 步驟 4: 設定公開存取（讓前端可以讀取）

### 方法 A: 設定 bucket 為公開讀取

```bash
# 設定 bucket 的公開存取
gcloud storage buckets update gs://$BUCKET_NAME \
  --cors-file=cors.json

# 建立 cors.json 檔案（允許前端跨域存取）
cat > cors.json << EOF
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
EOF

# 設定 bucket 的 IAM 政策（允許公開讀取）
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
```

### 方法 B: 只設定特定檔案為公開（更安全）

```bash
# 上傳檔案後，設定特定檔案為公開
# 這會在步驟 5 中自動處理
```

---

## 🚀 步驟 5: 上傳 JSON 檔案

### 方法 A: 使用我們提供的腳本

```bash
# 確認 JSON 檔案存在
ls -lh dc_crime_zillow_combined.json

# 執行上傳腳本
python upload_to_gcp_storage.py dc_crime_zillow_combined.json $BUCKET_NAME

# 如果使用服務帳號，加上憑證路徑
python upload_to_gcp_storage.py dc_crime_zillow_combined.json $BUCKET_NAME credentials.json
```

### 方法 B: 使用 gcloud CLI 直接上傳

```bash
# 上傳檔案
gcloud storage cp dc_crime_zillow_combined.json gs://$BUCKET_NAME/data/

# 設定檔案為公開讀取
gcloud storage objects update gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json \
  --acl-public
```

---

## ✅ 步驟 6: 驗證上傳

### 檢查檔案是否上傳成功

```bash
# 列出 bucket 中的檔案
gcloud storage ls gs://$BUCKET_NAME/data/

# 檢查檔案詳情
gcloud storage objects describe gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json
```

### 取得公開 URL

```bash
# 取得公開 URL
PUBLIC_URL="https://storage.googleapis.com/$BUCKET_NAME/data/dc_crime_zillow_combined.json"
echo "公開 URL: $PUBLIC_URL"

# 測試是否可以存取
curl -I $PUBLIC_URL
```

---

## 🧪 步驟 7: 測試前端讀取

### 建立測試 HTML 檔案

```html
<!DOCTYPE html>
<html>
<head>
    <title>測試 JSON 讀取</title>
</head>
<body>
    <h1>測試 GCP Storage JSON 讀取</h1>
    <button onclick="loadData()">載入資料</button>
    <pre id="output"></pre>

    <script>
        async function loadData() {
            const url = 'https://storage.googleapis.com/YOUR-BUCKET-NAME/data/dc_crime_zillow_combined.json';
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                
                document.getElementById('output').textContent = JSON.stringify(data, null, 2);
                console.log('資料載入成功:', data);
            } catch (error) {
                console.error('載入失敗:', error);
                document.getElementById('output').textContent = '錯誤: ' + error.message;
            }
        }
    </script>
</body>
</html>
```

### 使用 curl 測試

```bash
# 測試 JSON 是否可以讀取
curl https://storage.googleapis.com/$BUCKET_NAME/data/dc_crime_zillow_combined.json | head -20
```

---

## 🔒 安全性建議

### 1. 使用 CORS 限制來源（生產環境）

```json
// cors.json
[
  {
    "origin": ["https://your-frontend-domain.com"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```

### 2. 使用簽名 URL（更安全，但需要後端）

如果需要更安全的存取控制，可以使用簽名 URL：

```python
from google.cloud import storage
from datetime import timedelta

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob('data/dc_crime_zillow_combined.json')

# 產生簽名 URL（24 小時有效）
url = blob.generate_signed_url(
    expiration=timedelta(hours=24),
    method='GET'
)
```

---

## 📊 成本估算

### 免費額度
- **儲存**: 5 GB/月
- **操作**: 5,000 次 Class A 操作/月
- **網路**: 1 GB 輸出/月

### 您的使用量
- **JSON 檔案**: ~1.5 MB
- **預估**: 完全在免費額度內 ✅

---

## 🐛 常見問題

### 1. 權限錯誤

```bash
# 錯誤: AccessDeniedException
# 解決: 確認服務帳號有正確權限
gcloud projects get-iam-policy $PROJECT_ID
```

### 2. CORS 錯誤（前端無法讀取）

```bash
# 設定 CORS
gcloud storage buckets update gs://$BUCKET_NAME --cors-file=cors.json
```

### 3. 找不到 bucket

```bash
# 確認 bucket 名稱正確
gcloud storage buckets list

# 確認專案設定
gcloud config get-value project
```

---

## 📝 快速檢查清單

- [ ] GCP 專案已建立
- [ ] Cloud Storage API 已啟用
- [ ] Storage Bucket 已建立
- [ ] 認證已設定（gcloud 或服務帳號）
- [ ] Python 套件已安裝（google-cloud-storage）
- [ ] JSON 檔案已上傳
- [ ] 檔案已設定為公開讀取
- [ ] CORS 已設定（如果需要）
- [ ] 前端可以成功讀取

---

## 🎯 下一步

完成上述步驟後，您就可以：

1. ✅ 在前端使用公開 URL 讀取 JSON
2. ✅ 定期更新 JSON 檔案（重新上傳）
3. ✅ 設定自動化腳本（可選）

需要協助執行任何步驟嗎？

