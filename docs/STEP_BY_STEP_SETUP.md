# GCP Cloud Storage 逐步設定指南

## 📋 前置檢查清單

在開始之前，請確認：

- [ ] 有 GCP 帳號（如果沒有，前往 https://console.cloud.google.com 註冊）
- [ ] 已啟用計費帳戶（免費額度內不會收費）
- [ ] 已安裝 Python 和虛擬環境

---

## 🔧 步驟 1: 安裝 gcloud CLI

### macOS 安裝

```bash
# 方法 A: 使用 Homebrew（推薦）
brew install --cask google-cloud-sdk

# 方法 B: 手動安裝
# 1. 下載安裝腳本
curl https://sdk.cloud.google.com | bash

# 2. 重新載入 shell
exec -l $SHELL

# 3. 初始化
gcloud init
```

### 驗證安裝

```bash
gcloud --version
```

應該會看到類似：
```
Google Cloud SDK 450.0.0
```

---

## 🔐 步驟 2: 登入 GCP

```bash
# 登入 GCP（會開啟瀏覽器）
gcloud auth login

# 列出已登入的帳號
gcloud auth list
```

---

## 📦 步驟 3: 建立或選擇 GCP 專案

### 選項 A: 建立新專案

```bash
# 建立新專案
gcloud projects create dc-crime-data-project \
  --name="DC Crime Data Project"

# 設定為預設專案
gcloud config set project dc-crime-data-project
```

### 選項 B: 使用現有專案

```bash
# 列出所有專案
gcloud projects list

# 設定預設專案
gcloud config set project YOUR-PROJECT-ID
```

### 確認專案設定

```bash
# 查看當前專案
gcloud config get-value project
```

---

## 🚀 步驟 4: 啟用 Cloud Storage API

```bash
# 啟用 Cloud Storage API
gcloud services enable storage-component.googleapis.com

# 確認已啟用
gcloud services list --enabled | grep storage
```

---

## 🪣 步驟 5: 建立 Storage Bucket

### 選擇唯一的 bucket 名稱

Bucket 名稱必須全球唯一，建議格式：
- `dc-crime-data-yourname`
- `dc-crime-data-2025`
- `dc-crime-data-$(date +%s)` （使用時間戳記）

```bash
# 設定 bucket 名稱（請替換為您的唯一名稱）
BUCKET_NAME="dc-crime-data-$(whoami)-$(date +%s)"

# 或直接指定
BUCKET_NAME="dc-crime-data-your-unique-name"

# 建立 bucket（選擇離您最近的區域）
gcloud storage buckets create gs://$BUCKET_NAME \
  --location=us-central1

# 確認 bucket 已建立
gcloud storage buckets list
```

**區域選擇建議**:
- `us-central1` (Iowa) - 美國中部
- `us-east1` (South Carolina) - 美國東部
- `asia-east1` (Taiwan) - 亞洲東部
- `europe-west1` (Belgium) - 歐洲西部

---

## 🔑 步驟 6: 設定認證

### 方法 A: 使用 gcloud（最簡單，推薦用於開發）

```bash
# 設定應用程式預設憑證
gcloud auth application-default login

# 這會開啟瀏覽器讓您登入
# 完成後，Python 腳本會自動使用這個認證
```

### 方法 B: 使用服務帳號（適合生產環境）

```bash
# 建立服務帳號
gcloud iam service-accounts create storage-uploader \
  --display-name="Storage Uploader"

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

---

## 📦 步驟 7: 安裝 Python 套件

```bash
# 確保在虛擬環境中
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
source venv/bin/activate

# 安裝 Google Cloud Storage 套件
pip install google-cloud-storage
```

---

## ⚙️ 步驟 8: 設定 CORS（讓前端可以跨域讀取）

```bash
# 建立 CORS 設定檔案
cat > cors.json << 'EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
EOF

# 套用 CORS 設定
gcloud storage buckets update gs://$BUCKET_NAME --cors-file=cors.json
```

---

## 📤 步驟 9: 上傳 JSON 檔案

### 方法 A: 使用我們提供的腳本

```bash
# 確認 JSON 檔案存在
ls -lh dc_crime_zillow_combined.json

# 執行上傳腳本
python upload_to_gcp_storage.py dc_crime_zillow_combined.json $BUCKET_NAME
```

### 方法 B: 使用 gcloud CLI 直接上傳

```bash
# 上傳檔案到 data/ 目錄
gcloud storage cp dc_crime_zillow_combined.json gs://$BUCKET_NAME/data/

# 設定檔案為公開讀取（讓前端可以存取）
gcloud storage objects update gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json \
  --acl-public
```

---

## ✅ 步驟 10: 驗證上傳

```bash
# 列出 bucket 中的檔案
gcloud storage ls gs://$BUCKET_NAME/data/

# 檢查檔案詳情
gcloud storage objects describe gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json

# 取得公開 URL
PUBLIC_URL="https://storage.googleapis.com/$BUCKET_NAME/data/dc_crime_zillow_combined.json"
echo "公開 URL: $PUBLIC_URL"

# 測試是否可以存取
curl -I $PUBLIC_URL
```

應該會看到 `HTTP/1.1 200 OK`

---

## 🧪 步驟 11: 測試前端讀取

### 建立測試檔案

```bash
# 建立測試 HTML
cat > test_frontend.html << EOF
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
        const PUBLIC_URL = '$PUBLIC_URL';
        
        async function loadData() {
            try {
                const response = await fetch(PUBLIC_URL);
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }
                const data = await response.json();
                
                document.getElementById('output').textContent = 
                    '✅ 成功載入！\\n\\n' +
                    '總 ZIP Code 數: ' + data.metadata.total_zipcodes + '\\n' +
                    '總犯罪記錄數: ' + data.metadata.total_crimes + '\\n\\n' +
                    '範例資料 (ZIP 20002):\\n' +
                    JSON.stringify(data.data['20002'], null, 2);
                
                console.log('資料載入成功:', data);
            } catch (error) {
                document.getElementById('output').textContent = 
                    '❌ 錯誤: ' + error.message;
                console.error('載入失敗:', error);
            }
        }
    </script>
</body>
</html>
EOF

echo "測試檔案已建立: test_frontend.html"
echo "請在瀏覽器中開啟並點擊「載入資料」按鈕"
```

### 使用 curl 測試

```bash
# 測試 JSON 是否可以讀取
curl $PUBLIC_URL | python3 -m json.tool | head -30
```

---

## 📝 快速設定腳本（一鍵完成）

如果您想要快速完成所有設定，可以使用我們提供的腳本：

```bash
# 執行快速設定腳本
./setup_gcp_quick.sh
```

這個腳本會自動完成：
1. ✅ 檢查 gcloud 安裝
2. ✅ 登入 GCP
3. ✅ 建立/選擇專案
4. ✅ 啟用 API
5. ✅ 建立 bucket
6. ✅ 設定認證
7. ✅ 設定 CORS
8. ✅ 上傳檔案
9. ✅ 設定公開讀取

---

## 🎯 完成後的資訊

完成所有步驟後，您會得到：

1. **Bucket 名稱**: `gs://dc-crime-data-xxx`
2. **公開 URL**: `https://storage.googleapis.com/dc-crime-data-xxx/data/dc_crime_zillow_combined.json`
3. **前端使用方式**:
   ```javascript
   fetch('https://storage.googleapis.com/YOUR-BUCKET/data/dc_crime_zillow_combined.json')
     .then(res => res.json())
     .then(data => {
       // 使用資料
       console.log(data.data['20002']);
     });
   ```

---

## 🐛 常見問題排除

### 問題 1: gcloud 命令找不到

```bash
# macOS 使用 Homebrew 安裝後，需要重新載入 shell
exec -l $SHELL

# 或手動加入 PATH
export PATH="$PATH:/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/bin"
```

### 問題 2: 權限錯誤

```bash
# 確認已登入
gcloud auth list

# 重新登入
gcloud auth login
gcloud auth application-default login
```

### 問題 3: Bucket 名稱已存在

```bash
# 使用時間戳記確保唯一性
BUCKET_NAME="dc-crime-data-$(date +%s)"
```

### 問題 4: CORS 錯誤（前端無法讀取）

```bash
# 重新設定 CORS
gcloud storage buckets update gs://$BUCKET_NAME --cors-file=cors.json

# 確認檔案是公開的
gcloud storage objects update gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json --acl-public
```

---

## 📊 成本確認

您的使用量：
- **儲存**: ~1.5 MB（免費額度 5 GB）✅
- **操作**: 少量（免費額度 5,000 次/月）✅
- **網路**: 少量（免費額度 1 GB/月）✅

**預估成本**: $0/月（完全在免費額度內）

---

## 🎉 下一步

完成設定後，您可以：

1. ✅ 在前端使用公開 URL 讀取 JSON
2. ✅ 測試前端讀取功能
3. ✅ 繼續設定 Supabase（下一步）

需要協助執行任何步驟嗎？

