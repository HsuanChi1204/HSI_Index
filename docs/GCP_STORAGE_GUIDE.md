# 如何在 GCP Console 找到儲存的資料

## 📍 快速連結

### 直接連結到您的 Storage Bucket

```
https://console.cloud.google.com/storage/browser/dc-crime-data-zhangxuanqi-1762814591
```

### 直接連結到 JSON 檔案

```
https://console.cloud.google.com/storage/browser/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json
```

---

## 🗺️ 導航步驟

### 方法 1: 從 Storage 瀏覽器進入

1. **前往 GCP Console**
   ```
   https://console.cloud.google.com
   ```

2. **選擇專案**
   - 在頂部專案選擇器中，選擇 `dc-crime-data-project`

3. **開啟 Storage 瀏覽器**
   - 在左側選單中，點擊「**Cloud Storage**」→「**Buckets**」
   - 或直接前往：https://console.cloud.google.com/storage/browser

4. **選擇 Bucket**
   - 點擊 bucket 名稱：`dc-crime-data-zhangxuanqi-1762814591`

5. **查看檔案**
   - 進入 `data/` 資料夾
   - 您會看到 `dc_crime_zillow_combined.json`

### 方法 2: 使用搜尋功能

1. **在 GCP Console 頂部搜尋框**
   - 輸入：`dc-crime-data-zhangxuanqi-1762814591`
   - 選擇「Storage bucket」

2. **直接進入 bucket 頁面**

---

## 📋 在 GCP Console 中可以執行的操作

### 1. 查看檔案詳情

- 點擊檔案名稱
- 可以查看：
  - 檔案大小
  - 建立時間
  - 最後修改時間
  - 公開 URL
  - 權限設定

### 2. 下載檔案

- 點擊檔案名稱
- 點擊「下載」按鈕

### 3. 設定權限

- 點擊檔案名稱
- 點擊「權限」標籤
- 可以新增/移除存取權限

### 4. 查看使用量

- 在 bucket 頁面
- 可以看到儲存使用量
- 可以查看操作統計

### 5. 設定 CORS

- 在 bucket 頁面
- 點擊「設定」標籤
- 在「CORS 設定」中查看/編輯

---

## 🔍 快速檢查清單

在 GCP Console 中確認：

- [ ] Bucket 存在：`dc-crime-data-zhangxuanqi-1762814591`
- [ ] 檔案存在：`data/dc_crime_zillow_combined.json`
- [ ] 檔案大小：約 1.5 MB
- [ ] 公開存取：已設定（allUsers 有 Storage Object Viewer 權限）
- [ ] CORS 已設定：允許所有來源讀取

---

## 📊 監控和管理

### 查看使用量

1. 前往 Storage 瀏覽器
2. 點擊 bucket 名稱
3. 在「概覽」標籤中查看：
   - 儲存使用量
   - 操作次數
   - 網路輸出

### 設定預算提醒

1. 前往「計費」→「預算與提醒」
2. 建立新預算
3. 設定提醒（例如：$1）

### 查看日誌

1. 前往「Logging」→「Logs Explorer」
2. 篩選條件：`resource.type="gcs_bucket"`

---

## 🔗 有用的連結

- **Storage 瀏覽器**: https://console.cloud.google.com/storage/browser
- **您的 Bucket**: https://console.cloud.google.com/storage/browser/dc-crime-data-zhangxuanqi-1762814591
- **專案設定**: https://console.cloud.google.com/home/dashboard?project=dc-crime-data-project
- **計費設定**: https://console.cloud.google.com/billing?project=dc-crime-data-project

---

## 💡 提示

1. **書籤**: 將 bucket 頁面加入書籤，方便快速存取
2. **通知**: 設定使用量通知，避免超出免費額度
3. **備份**: 定期下載 JSON 檔案作為備份
4. **版本控制**: 如果需要，可以啟用版本控制功能

