# 修正 GCP 計費帳戶問題

## ❌ 錯誤訊息

```
ERROR: (gcloud.storage.buckets.create) HTTPError 403: 
The billing account for the owning project is disabled in state absent.
```

## 🔍 問題原因

GCP 需要啟用計費帳戶才能建立 Storage bucket，**即使使用免費額度也需要啟用**。

這是因為：
- GCP 需要信用卡來驗證身份
- 免費額度內不會收費
- 但必須先啟用計費帳戶

## ✅ 解決方法

### 方法 1: 在 GCP Console 啟用計費（推薦）

#### 步驟 1: 前往計費設定

1. 開啟瀏覽器，前往：
   ```
   https://console.cloud.google.com/billing
   ```

2. 或直接前往您的專案計費設定：
   ```
   https://console.cloud.google.com/billing?project=YOUR-PROJECT-ID
   ```

#### 步驟 2: 連結計費帳戶

1. 如果沒有計費帳戶：
   - 點擊「建立帳單帳戶」
   - 輸入帳單資訊（需要信用卡）
   - **重要**: 免費額度內不會收費

2. 如果有計費帳戶但未連結：
   - 點擊「連結帳單帳戶」
   - 選擇您的計費帳戶
   - 連結到當前專案

#### 步驟 3: 確認連結成功

在專案頁面應該會看到：
- ✅ 計費帳戶狀態：已啟用
- ✅ 免費試用：可用（如果符合資格）

### 方法 2: 使用 gcloud CLI 連結計費帳戶

```bash
# 1. 列出可用的計費帳戶
gcloud billing accounts list

# 2. 取得專案 ID
PROJECT_ID=$(gcloud config get-value project)

# 3. 連結計費帳戶（替換 BILLING_ACCOUNT_ID）
gcloud billing projects link $PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

### 方法 3: 建立新專案並啟用計費

如果當前專案有問題，可以建立新專案：

```bash
# 1. 建立新專案
gcloud projects create dc-crime-data-$(date +%s) \
  --name="DC Crime Data"

# 2. 設定為當前專案
gcloud config set project dc-crime-data-$(date +%s)

# 3. 在 GCP Console 啟用計費（必須在網頁上操作）
# 前往: https://console.cloud.google.com/billing
```

## 🔒 免費額度說明

### GCP Cloud Storage 免費額度

- **儲存**: 5 GB/月（Standard Storage）
- **操作**: 
  - Class A 操作（寫入、列出）: 5,000 次/月
  - Class B 操作（讀取）: 50,000 次/月
- **網路輸出**: 1 GB/月（到同一區域）

### 您的使用量預估

- **JSON 檔案**: ~1.5 MB
- **讀取次數**: 少量（前端讀取）
- **預估成本**: **$0/月**（完全在免費額度內）✅

### 如何避免意外收費

1. **設定預算提醒**:
   ```bash
   # 在 GCP Console 設定預算提醒
   # 前往: https://console.cloud.google.com/billing/budgets
   ```

2. **監控使用量**:
   ```bash
   # 查看當前使用量
   gcloud billing accounts list
   ```

3. **設定使用限制**（可選）:
   - 在 GCP Console 設定配額限制
   - 當接近免費額度時會收到通知

## 📝 快速檢查清單

完成計費設定後，確認：

- [ ] 計費帳戶已建立
- [ ] 計費帳戶已連結到專案
- [ ] 專案狀態顯示「已啟用計費」
- [ ] 可以重新嘗試建立 bucket

## 🚀 完成計費設定後

重新執行建立 bucket 的命令：

```bash
# 設定環境變數（如果還沒設定）
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
export CLOUDSDK_PYTHON="/opt/homebrew/bin/python3"

# 建立 bucket
BUCKET_NAME="dc-crime-data-$(date +%s)"
gcloud storage buckets create gs://$BUCKET_NAME \
  --location=us-east1
```

或執行快速設定腳本：

```bash
./setup_gcp_quick.sh
```

## ⚠️ 重要提醒

1. **免費額度很充足**: 您的使用量遠低於免費額度
2. **不會自動收費**: 必須明確啟用付費服務才會收費
3. **可以隨時取消**: 如果不再使用，可以取消計費帳戶
4. **設定預算提醒**: 建議設定 $1 的預算提醒，避免意外

## 🆘 如果不想啟用計費

如果因為某些原因無法啟用計費，可以考慮：

1. **使用 Supabase Storage**（免費，不需要信用卡）
2. **使用其他免費儲存服務**（如 GitHub Releases、GitLab Packages）
3. **使用 Firebase Storage**（有免費額度，但需要信用卡）

但 GCP Cloud Storage 的免費額度是最充足的，建議還是啟用計費帳戶。

---

需要協助執行任何步驟嗎？

