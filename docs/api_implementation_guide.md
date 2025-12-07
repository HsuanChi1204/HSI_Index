# API 實作指南

## 快速開始：建立 GCP API 服務

### 步驟 1: 準備資料庫 Schema

建立 `schema.sql`:

```sql
-- 啟用 PostGIS 擴展（地理空間查詢）
CREATE EXTENSION IF NOT EXISTS postgis;

-- Crimes 表
CREATE TABLE IF NOT EXISTS crimes (
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
    x_coord DECIMAL(12, 6),
    y_coord DECIMAL(12, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Zillow 表
CREATE TABLE IF NOT EXISTS zillow_data (
    id SERIAL PRIMARY KEY,
    zip_code VARCHAR(5) UNIQUE NOT NULL,
    region_name VARCHAR(50),
    state VARCHAR(2),
    metro TEXT,
    county_name VARCHAR(100),
    mom DECIMAL(10, 6),
    yoy DECIMAL(10, 6),
    current_price DECIMAL(12, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_crimes_zip_code ON crimes(zip_code);
CREATE INDEX IF NOT EXISTS idx_crimes_offense ON crimes(offense);
CREATE INDEX IF NOT EXISTS idx_crimes_date ON crimes(report_dat);
CREATE INDEX IF NOT EXISTS idx_crimes_location ON crimes USING GIST(
    ST_MakePoint(longitude, latitude)
);
CREATE INDEX IF NOT EXISTS idx_zillow_zip_code ON zillow_data(zip_code);
```

### 步驟 2: 建立 FastAPI 專案結構

```
api/
├── main.py              # FastAPI 應用入口
├── config.py            # 設定檔
├── database.py          # 資料庫連線
├── models/
│   ├── __init__.py
│   ├── crime.py         # Crime 資料模型
│   └── zillow.py        # Zillow 資料模型
├── routers/
│   ├── __init__.py
│   ├── crimes.py        # Crime API 路由
│   ├── zillow.py        # Zillow API 路由
│   └── zipcode.py      # 整合 API 路由
├── services/
│   ├── __init__.py
│   └── data_service.py # 資料查詢服務
├── requirements.txt
└── Dockerfile
```

### 步驟 3: 建立 requirements.txt

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

### 步驟 4: 建立基礎 API 程式碼

#### main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import crimes, zillow, zipcode

app = FastAPI(
    title="DC Crime & Zillow API",
    description="API for DC Crime and Zillow housing data",
    version="1.0.0"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制特定網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(crimes.router, prefix="/api/v1/crimes", tags=["crimes"])
app.include_router(zillow.router, prefix="/api/v1/zillow", tags=["zillow"])
app.include_router(zipcode.router, prefix="/api/v1/zipcode", tags=["zipcode"])

@app.get("/")
async def root():
    return {"message": "DC Crime & Zillow API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 步驟 5: 資料匯入腳本

建立 `scripts/import_data.py`:

```python
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os

# 資料庫連線
DATABASE_URL = os.getenv("DATABASE_URL")

def import_crimes():
    """匯入 Crime 資料"""
    df = pd.read_csv('DC_Crime_Incidents_2025_08_09_with_zipcode.csv')
    
    # 清理資料
    df = df[df['ZIP_CODE'].notna()]  # 只匯入有 ZIP_CODE 的
    
    # 選擇需要的欄位
    columns = [
        'CCN', 'REPORT_DAT', 'SHIFT', 'METHOD', 'OFFENSE', 'BLOCK',
        'WARD', 'ANC', 'DISTRICT', 'LATITUDE', 'LONGITUDE', 'ZIP_CODE',
        'NEIGHBORHOOD_CLUSTER', 'X', 'Y'
    ]
    df = df[columns]
    
    # 重新命名欄位
    df.columns = [
        'ccn', 'report_dat', 'shift', 'method', 'offense', 'block',
        'ward', 'anc', 'district', 'latitude', 'longitude', 'zip_code',
        'neighborhood_cluster', 'x_coord', 'y_coord'
    ]
    
    # 匯入資料庫
    engine = create_engine(DATABASE_URL)
    df.to_sql('crimes', engine, if_exists='append', index=False)
    print(f"匯入 {len(df)} 筆 Crime 資料")

def import_zillow():
    """匯入 Zillow 資料"""
    df = pd.read_csv('dc_zillow_2025_09_30.csv')
    
    # 重新命名欄位
    df.columns = [
        'zip_code', 'region_name', 'state', 'metro', 
        'county_name', 'mom', 'yoy', 'current_price'
    ]
    
    # 匯入資料庫
    engine = create_engine(DATABASE_URL)
    df.to_sql('zillow_data', engine, if_exists='replace', index=False)
    print(f"匯入 {len(df)} 筆 Zillow 資料")

if __name__ == "__main__":
    import_crimes()
    import_zillow()
```

---

## 部署到 GCP

### 1. 建立 Cloud SQL 資料庫

```bash
# 建立資料庫實例
gcloud sql instances create dc-data-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_PASSWORD

# 建立資料庫
gcloud sql databases create dc_data --instance=dc-data-db
```

### 2. 建立 Cloud Run 服務

```bash
# 建立 Dockerfile
# 建立 .env 檔案（包含資料庫連線資訊）

# 部署到 Cloud Run
gcloud run deploy dc-crime-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://user:pass@/db?host=/cloudsql/PROJECT:REGION:INSTANCE"
```

---

## API 使用範例

### 1. 取得所有 Crime 資料（分頁）

```javascript
fetch('https://your-api.run.app/api/v1/crimes?limit=100&offset=0')
  .then(res => res.json())
  .then(data => console.log(data));
```

### 2. 取得特定 ZIP Code 的 Crime 資料

```javascript
fetch('https://your-api.run.app/api/v1/crimes?zip_code=20002')
  .then(res => res.json())
  .then(data => console.log(data));
```

### 3. 取得 ZIP Code 的完整資料（整合）

```javascript
fetch('https://your-api.run.app/api/v1/zipcode/20002')
  .then(res => res.json())
  .then(data => {
    console.log('Crime stats:', data.crime_stats);
    console.log('Zillow data:', data.zillow_data);
  });
```

### 4. 地理查詢（附近 1km 的犯罪記錄）

```javascript
fetch('https://your-api.run.app/api/v1/crimes/nearby', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    lat: 38.9,
    lon: -77.0,
    radius: 1000  // 公尺
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 下一步建議

1. **建立基礎 API**: 先實作基本的 CRUD 操作
2. **資料匯入**: 將 CSV 資料匯入 Cloud SQL
3. **測試 API**: 使用 Postman 或 curl 測試
4. **前端整合**: 建立簡單的前端頁面測試
5. **優化**: 根據使用情況優化查詢和索引

