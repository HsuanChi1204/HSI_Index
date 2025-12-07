# GCP API 架構設計方案

## 📊 資料分析

### 現有資料
- **DC_Crime**: 3,872 筆記錄，30 個欄位，約 3.92 MB
- **dc_zillow**: 22 筆記錄，8 個欄位，約 5.56 KB
- **HouseTS Social** (未來): 待確認

### 資料關聯
- Crime 和 Zillow 透過 ZIP Code 關聯
- 共同的 ZIP Code: 22 個

---

## 🏗️ 推薦架構方案

### 方案 A: Cloud SQL + Cloud Run (推薦) ⭐

**適用場景**: 需要複雜查詢、關聯查詢、未來擴展性高

#### 架構組成
```
前端 → Cloud Load Balancer → Cloud Run (FastAPI) → Cloud SQL (PostgreSQL)
                                    ↓
                            Cloud Storage (備份)
```

#### 優點
- ✅ 支援複雜 SQL 查詢（JOIN、聚合、篩選）
- ✅ 資料關聯容易（Crime ↔ Zillow）
- ✅ 擴展性好（未來 HouseTS 資料容易整合）
- ✅ 成本可控（小型專案每月約 $20-50）
- ✅ 支援地理空間查詢（PostGIS）

#### 缺點
- ⚠️ 需要管理資料庫
- ⚠️ 需要處理連線池

---

### 方案 B: Firestore + Cloud Functions

**適用場景**: 簡單查詢、快速開發、無伺服器架構

#### 架構組成
```
前端 → API Gateway → Cloud Functions → Firestore
```

#### 優點
- ✅ 無伺服器，自動擴展
- ✅ 開發快速
- ✅ 免費額度較高

#### 缺點
- ⚠️ 複雜查詢較困難
- ⚠️ 成本隨使用量增長
- ⚠️ 關聯查詢需要多次請求

---

### 方案 C: BigQuery + Cloud Run

**適用場景**: 大量資料分析、需要複雜分析查詢

#### 優點
- ✅ 適合大資料分析
- ✅ SQL 查詢強大

#### 缺點
- ⚠️ 成本較高（查詢計費）
- ⚠️ 延遲較高（不適合即時 API）

---

## 🎯 推薦方案：方案 A (Cloud SQL + Cloud Run)

### 技術棧
- **資料庫**: Cloud SQL (PostgreSQL 14+)
- **API 框架**: FastAPI (Python)
- **部署**: Cloud Run
- **儲存**: Cloud Storage (CSV 備份)
- **認證**: API Key 或 OAuth 2.0

---

## 📐 API 設計

### RESTful API 端點設計

#### 1. Crime 資料 API

```
GET /api/v1/crimes
  Query Parameters:
    - zip_code: 篩選特定 ZIP Code
    - offense: 篩選犯罪類型
    - date_from: 開始日期
    - date_to: 結束日期
    - limit: 限制筆數 (default: 100)
    - offset: 分頁偏移
    - bbox: 地理邊界框 (lat1,lon1,lat2,lon2)

GET /api/v1/crimes/{crime_id}
  取得單一犯罪記錄

GET /api/v1/crimes/stats
  統計資料（按 ZIP Code、犯罪類型等）
```

#### 2. Zillow 資料 API

```
GET /api/v1/zillow
  取得所有 Zillow 資料

GET /api/v1/zillow/{zip_code}
  取得特定 ZIP Code 的房價資料

GET /api/v1/zillow/stats
  房價統計資料
```

#### 3. 整合 API

```
GET /api/v1/zipcode/{zip_code}
  取得特定 ZIP Code 的完整資料
  - Crime 統計
  - Zillow 房價資料
  - 未來: HouseTS social 資料

GET /api/v1/zipcode/{zip_code}/summary
  取得 ZIP Code 摘要（用於地圖顯示）
```

#### 4. 地理查詢 API

```
POST /api/v1/crimes/nearby
  Body: { "lat": 38.9, "lon": -77.0, "radius": 1000 }
  查詢附近 1km 內的犯罪記錄
```

---

## 📦 資料庫 Schema 設計

### 1. crimes 表
```sql
CREATE TABLE crimes (
    id SERIAL PRIMARY KEY,
    ccn VARCHAR(50) UNIQUE,
    report_dat TIMESTAMP,
    shift VARCHAR(20),
    method VARCHAR(50),
    offense VARCHAR(100),
    block TEXT,
    ward VARCHAR(10),
    anc VARCHAR(10),
    district VARCHAR(10),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    zip_code VARCHAR(5),
    neighborhood_cluster VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crimes_zip_code ON crimes(zip_code);
CREATE INDEX idx_crimes_offense ON crimes(offense);
CREATE INDEX idx_crimes_date ON crimes(report_dat);
CREATE INDEX idx_crimes_location ON crimes USING GIST(
    ST_MakePoint(longitude, latitude)
);
```

### 2. zillow_data 表
```sql
CREATE TABLE zillow_data (
    id SERIAL PRIMARY KEY,
    zip_code VARCHAR(5) UNIQUE,
    region_name VARCHAR(50),
    state VARCHAR(2),
    metro TEXT,
    county_name VARCHAR(100),
    mom DECIMAL(10, 6),  -- Month-over-Month
    yoy DECIMAL(10, 6),  -- Year-over-Year
    current_price DECIMAL(12, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_zillow_zip_code ON zillow_data(zip_code);
```

### 3. 未來: house_ts_social 表
```sql
CREATE TABLE house_ts_social (
    id SERIAL PRIMARY KEY,
    zip_code VARCHAR(5),
    date DATE,
    social_metric VARCHAR(50),
    value DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (zip_code) REFERENCES zillow_data(zip_code)
);

CREATE INDEX idx_social_zip_date ON house_ts_social(zip_code, date);
```

---

## 🚀 實作步驟

### Phase 1: 基礎架構設置 (1-2 天)

1. **建立 Cloud SQL 資料庫**
   ```bash
   gcloud sql instances create dc-data-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

2. **建立資料庫和表**
   - 執行 schema.sql
   - 匯入資料

3. **建立 Cloud Run 服務**
   - 設定 FastAPI 應用
   - 設定環境變數（資料庫連線）

### Phase 2: API 開發 (2-3 天)

1. **建立 FastAPI 專案結構**
   ```
   api/
   ├── main.py
   ├── models/
   │   ├── crime.py
   │   └── zillow.py
   ├── database.py
   ├── routers/
   │   ├── crimes.py
   │   ├── zillow.py
   │   └── zipcode.py
   └── requirements.txt
   ```

2. **實作 API 端點**
   - Crime CRUD
   - Zillow 查詢
   - 整合查詢

3. **加入認證和限流**
   - API Key 認證
   - Rate limiting

### Phase 3: 資料匯入 (1 天)

1. **建立資料匯入腳本**
   - CSV → PostgreSQL
   - 資料驗證和清理

2. **設定定期更新機制**
   - Cloud Scheduler
   - Cloud Functions (觸發資料更新)

### Phase 4: 測試和優化 (1-2 天)

1. **效能測試**
   - 查詢優化
   - 索引調整

2. **API 文件**
   - Swagger/OpenAPI
   - 使用範例

---

## 💰 成本估算

### Cloud SQL (db-f1-micro)
- 每月: ~$7-10
- 適合小型專案

### Cloud Run
- 免費額度: 每月 200 萬請求
- 超出後: $0.40/百萬請求
- 預估: 免費額度內

### Cloud Storage
- 儲存: $0.020/GB/月
- 預估: < $0.10/月

### 總計
- **預估每月**: $10-20 (小型專案)
- **預估每年**: $120-240

---

## 🔒 安全性建議

1. **API 認證**
   - API Key (簡單專案)
   - OAuth 2.0 (生產環境)

2. **資料庫安全**
   - 私有 IP
   - SSL 連線
   - 最小權限原則

3. **CORS 設定**
   - 限制允許的來源

4. **Rate Limiting**
   - 防止濫用

---

## 📈 未來擴展

### HouseTS Social 資料整合
1. 建立 `house_ts_social` 表
2. 新增 API 端點 `/api/v1/social`
3. 整合到 `/api/v1/zipcode/{zip_code}` 端點

### 效能優化
1. Redis 快取（熱門查詢）
2. CDN (靜態資料)
3. 讀寫分離（大量查詢時）

### 監控和日誌
1. Cloud Monitoring
2. Cloud Logging
3. Error tracking

---

## 🎯 建議的下一步

1. **立即開始**: 建立 Cloud SQL 資料庫
2. **開發 API**: 使用 FastAPI 建立基礎架構
3. **資料匯入**: 將 CSV 匯入資料庫
4. **測試**: 建立簡單的前端測試頁面
5. **部署**: 部署到 Cloud Run

---

## 📝 替代方案考量

如果預算有限或想快速原型：
- **Firebase Firestore**: 免費額度較高，適合快速開發
- **Supabase**: 開源的 Firebase 替代方案，有免費層
- **Railway/Render**: 更簡單的部署選項

但考慮到未來擴展和複雜查詢需求，**Cloud SQL + Cloud Run** 仍是最佳選擇。

