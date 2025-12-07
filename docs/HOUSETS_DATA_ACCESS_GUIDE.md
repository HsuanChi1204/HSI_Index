# HouseTS 資料取得指南

## 📋 概述

根據 HouseTS 論文，資料集包含以下組件：
1. **Census Data** - 年度資料（2011-2022）
2. **House Price Data** - 月度資料（2012-2023）
3. **Points-of-Interest (POI) Data** - 月度資料（2012-2023）
4. **Satellite Imagery** - 年度影像（2012-2022，僅 Washington DC 地區）

---

## 🔍 資料來源

### 1. 主要來源

根據論文，HouseTS 資料集：
- **Kaggle**: 資料集主頁
- **GitHub**: 預處理管道和基準代碼
- **資料來源**:
  - **Census Data**: U.S. Census Bureau API (American Community Survey)
  - **House Price**: Zillow Home Value Index (ZHVI) 和 Redfin
  - **POI Data**: OpenHistoricalMap API
  - **Satellite Imagery**: National Agriculture Imagery Program (NAIP) via Google Earth Engine

### 2. Census Data 欄位（我們需要的）

根據論文 Table 5 和 Section 3，Census Data 包含以下欄位：

| 欄位名稱 | 說明 | 更新頻率 |
|---------|------|---------|
| Total Population | 總人口數 | 年度 |
| Median Age | 中位數年齡 | 年度 |
| Per Capita Income | 人均收入 | 年度 |
| Total Families Below Poverty | 貧困家庭數 | 年度 |
| Total Housing Units | 總住房單位數 | 年度 |
| Median Rent | 中位數租金 | 年度 |
| Median Home Value | 中位數房價 | 年度 |
| Total Labor Force | 總勞動力 | 年度 |
| Unemployed Population | 失業人口 | 年度 |
| School-Age Population | 學齡人口 | 年度 |
| School Enrollment | 就學人數 | 年度 |
| Median Commute Time | 中位數通勤時間 | 年度 |

**時間範圍**: 2011-2022（年度更新）

---

## 🚀 取得資料的方式

### 方式 1: 從 Kaggle 下載（推薦）

1. **訪問 Kaggle**
   - 搜尋 "HouseTS" 或 "HouseTS: A Large-Scale, Multimodal Spatiotemporal U.S. Housing Dataset"
   - 或直接訪問論文提到的 Kaggle 連結

2. **下載 Census Data**
   - 在 Kaggle 資料集中找到 Census 相關的 CSV 檔案
   - 下載包含 DC 地區的資料

3. **資料格式**
   - 應該是 ZIP code 級別的年度資料
   - 欄位應包含上述 12 個 Census 欄位

### 方式 2: 從 GitHub 取得

1. **訪問 GitHub Repository**
   - 搜尋 "HouseTS" GitHub repository
   - 論文提到所有預處理管道和基準代碼都在 GitHub 上

2. **下載資料**
   - 檢查 repository 中的 `data/` 資料夾
   - 或查看 README 中的資料下載說明

### 方式 3: 直接從 U.S. Census Bureau API 取得（進階）

如果需要最新資料或特定年份：

1. **訪問 ACS API**
   - URL: https://www.census.gov/programs-surveys/acs
   - 使用 U.S. Census Bureau API

2. **API 使用**
   ```python
   # 範例：使用 Census API 取得資料
   import requests
   
   # API endpoint
   api_url = "https://api.census.gov/data/2022/acs/acs5"
   
   # 參數
   params = {
       "get": "B01001_001E,B19013_001E,B25064_001E",  # Population, Income, Rent
       "for": "zip code tabulation area:*",
       "in": "state:11",  # DC state code
       "key": "YOUR_API_KEY"
   }
   
   response = requests.get(api_url, params=params)
   data = response.json()
   ```

3. **需要的欄位對應**
   - 需要查詢對應的 ACS 變數代碼
   - 例如：B01001_001E = Total Population

---

## 📊 資料處理

### 1. 檢查資料格式

下載後，檢查 CSV 檔案格式：

```python
import pandas as pd

# 讀取 Census Data
census_df = pd.read_csv('housets_census.csv')

# 檢查欄位
print(census_df.columns.tolist())

# 檢查 ZIP Code 欄位名稱
# 可能是：zip_code, ZIPCode, ZIP, zipcode, ZIP_CODE
```

### 2. 篩選 DC 地區

```python
# DC ZIP Code 範圍（大致）
dc_zip_codes = [
    '20001', '20002', '20003', '20004', '20005', '20006', '20007', '20008',
    '20009', '20010', '20011', '20012', '20015', '20016', '20017', '20018',
    '20019', '20020', '20024', '20032', '20036', '20037'
    # ... 更多 DC ZIP codes
]

# 篩選
dc_census = census_df[census_df['ZIPCode'].isin(dc_zip_codes)]
```

### 3. 對齊時間

根據論文：
- Census Data: 2011-2022（年度）
- 我們需要對齊到 2012-2023 的房價資料
- 使用前一年的 Census 資料預測下一年的房價（forward-shift）

---

## 🔧 整合到專案

### 步驟 1: 下載資料

```bash
# 從 Kaggle 下載
# 或從 GitHub repository 下載
# 將 CSV 檔案放在專案根目錄
```

### 步驟 2: 執行整合腳本

```bash
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
source venv/bin/activate

# 執行整合腳本
python scripts/combine_data_with_hci.py \
  --crime-csv DC_Crime_Incidents_2025_08_09_with_zipcode.csv \
  --zillow-csv dc_zillow_2025_09_30.csv \
  --housets-census-csv housets_census.csv \
  --output dc_crime_zillow_combined.json
```

### 步驟 3: 驗證資料

```python
import json

with open('dc_crime_zillow_combined.json', 'r') as f:
    data = json.load(f)

# 檢查 Census 資料
census_count = sum(1 for z in data['data'].values() if z.get('census_data'))
print(f'有 Census 資料的 ZIP Code: {census_count}/{len(data["data"])}')

# 檢查犯罪率計算
if census_count > 0:
    sample_zip = [z for z in data['data'].values() if z.get('census_data')][0]
    if sample_zip['hci']['default']:
        crime_rate = sample_zip['hci']['default'].get('crime_rate_per_1000')
        print(f'範例犯罪率（每 1000 居民）: {crime_rate}')
```

---

## 📝 資料來源引用

根據論文，資料來源應引用：

1. **Census Data**:
   - U.S. Census Bureau. American Community Survey. https://www.census.gov/programs-surveys/acs

2. **HouseTS Dataset**:
   - Wang, S., Sun, Y., Chen, F., et al. (2025). HouseTS: A Large-Scale, Multimodal Spatiotemporal U.S. Housing Dataset. NeurIPS 2025.

3. **Kaggle**:
   - HouseTS dataset on Kaggle (論文提到的連結)

---

## 🔍 尋找資料的具體步驟

### 步驟 1: 搜尋 Kaggle

1. 訪問 https://www.kaggle.com
2. 搜尋 "HouseTS" 或 "HouseTS dataset"
3. 找到資料集後下載 Census 相關的 CSV 檔案

### 步驟 2: 搜尋 GitHub

1. 訪問 https://github.com
2. 搜尋 "HouseTS" repository
3. 檢查 README 中的資料下載說明
4. 查看 `data/` 或 `datasets/` 資料夾

### 步驟 3: 檢查論文補充材料

1. 論文可能提供直接下載連結
2. 檢查論文的 GitHub repository
3. 查看是否有資料下載腳本

---

## ⚠️ 注意事項

1. **資料授權**: 確保遵守資料使用條款
2. **資料格式**: 確認 ZIP Code 格式與我們的資料一致
3. **時間對齊**: Census 資料是年度，需要對齊到月度房價資料
4. **缺失值**: 論文提到使用三階段插值策略處理缺失值

---

## 🆘 如果找不到資料

如果無法從 Kaggle 或 GitHub 取得：

1. **聯繫作者**: 透過論文中的聯繫方式詢問資料取得方式
2. **使用 Census API**: 直接從 U.S. Census Bureau API 取得原始資料
3. **使用替代資料源**: 尋找其他包含類似 Census 資料的公開資料集

---

## 📚 相關資源

- **論文**: HouseTS: A Large-Scale, Multimodal Spatiotemporal U.S. Housing Dataset
- **U.S. Census Bureau**: https://www.census.gov/programs-surveys/acs
- **ACS API 文件**: https://www.census.gov/data/developers/data-sets/acs-5year.html
- **Kaggle**: https://www.kaggle.com

---

需要協助搜尋或處理資料嗎？

