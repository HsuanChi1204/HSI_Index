# ✅ gcloud 安裝完成 - 下一步

## 🎉 問題已解決

gcloud CLI 已經可以正常使用了！

## 📝 重要設定

設定已經自動加入您的 `~/.zshrc` 檔案中：
- ✅ gcloud 已加入 PATH
- ✅ Python 路徑已設定

## 🚀 接下來的步驟

### 步驟 1: 重新載入 shell 設定（或重新開啟終端機）

```bash
source ~/.zshrc
```

### 步驟 2: 登入 GCP

```bash
gcloud auth login
```

這會開啟瀏覽器讓您登入 GCP 帳號。

### 步驟 3: 建立或選擇 GCP 專案

```bash
# 列出所有專案
gcloud projects list

# 建立新專案（如果需要）
gcloud projects create dc-crime-data-project \
  --name="DC Crime Data Project"

# 設定為預設專案
gcloud config set project dc-crime-data-project
```

### 步驟 4: 啟用 Cloud Storage API

```bash
gcloud services enable storage-component.googleapis.com
```

### 步驟 5: 執行快速設定腳本

```bash
# 確保在正確的目錄
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI

# 執行快速設定腳本
./setup_gcp_quick.sh
```

或者手動執行：

```bash
# 建立 bucket（請替換為您的唯一名稱）
BUCKET_NAME="dc-crime-data-$(whoami)-$(date +%s)"
gcloud storage buckets create gs://$BUCKET_NAME --location=us-central1

# 設定認證
gcloud auth application-default login

# 安裝 Python 套件
source venv/bin/activate
pip install google-cloud-storage

# 上傳檔案
python upload_to_gcp_storage.py dc_crime_zillow_combined.json $BUCKET_NAME
```

## 🔍 驗證 gcloud 是否正常

```bash
# 檢查版本
gcloud --version

# 檢查登入狀態
gcloud auth list

# 檢查當前專案
gcloud config get-value project
```

## 💡 提示

如果在新開啟的終端機中 gcloud 無法使用，請確認：

1. 已執行 `source ~/.zshrc`
2. 或重新開啟終端機
3. 環境變數已正確設定：
   ```bash
   echo $PATH | grep google-cloud-sdk
   echo $CLOUDSDK_PYTHON
   ```

## 🎯 完成後

完成上述步驟後，您就可以：
- ✅ 上傳 JSON 檔案到 GCP Storage
- ✅ 取得公開 URL 供前端使用
- ✅ 繼續設定 Supabase（下一步）

需要協助執行任何步驟嗎？

