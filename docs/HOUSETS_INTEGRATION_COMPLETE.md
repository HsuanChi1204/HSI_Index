# HouseTS 資料整合完成報告

## ✅ 整合狀態

### 資料來源
- **檔案**: `HouseTS.csv`
- **大小**: 271.43 MB
- **總記錄數**: 884,092 筆
- **DC 地區記錄**: 3,124 筆
- **DC ZIP Codes**: 22 個

### 整合結果
- ✅ 成功載入 HouseTS Census 資料
- ✅ 成功提取最新的 Census 資料（每個 ZIP Code 最新年度）
- ✅ 成功計算犯罪率（每 1000 居民）
- ✅ 成功整合到 JSON 檔案
- ✅ 已上傳到 GCP Cloud Storage

---

## 📊 HouseTS 資料結構

### 包含的資料類型

1. **房價資料** (Redfin)
   - median_sale_price
   - median_list_price
   - median_ppsf
   - homes_sold
   - pending_sales
   - new_listings
   - inventory
   - median_dom
   - avg_sale_to_list
   - sold_above_list
   - off_market_in_two_weeks

2. **POI 資料** (Points of Interest)
   - bank
   - bus
   - hospital
   - mall
   - park
   - restaurant
   - school
   - station
   - supermarket

3. **Census 資料** (American Community Survey)
   - Total Population
   - Median Age
   - Per Capita Income
   - Total Families Below Poverty
   - Total Housing Units
   - Median Rent
   - Median Home Value
   - Total Labor Force
   - Unemployed Population
   - Total School Age Population
   - Total School Enrollment
   - Median Commute Time

4. **時間資訊**
   - date (月度)
   - year (年度)
   - zipcode
   - city
   - city_full

---

## 🔍 DC 地區資料

### 城市名稱
- **HouseTS 中的名稱**: `DC_Metro`
- **範圍**: Washington DC 都會區

### ZIP Codes
HouseTS 中包含 22 個 DC ZIP Codes：
- 20001, 20002, 20003, 20004, 20005, 20006, 20007, 20008, 20009, 20010
- 20011, 20012, 20015, 20016, 20017, 20018, 20019, 20020, 20024, 20032, 20036, 20037

### 時間範圍
- **Census 資料**: 2011-2022（年度更新）
- **房價資料**: 2012-2023（月度更新）
- **POI 資料**: 2012-2023（月度更新）

---

## 📝 資料處理邏輯

### 1. 載入 HouseTS 資料
```python
# 從 HouseTS.csv 載入 DC 地區的資料
housets_df = load_housets_csv('HouseTS.csv', dc_zip_codes=dc_zip_codes)
```

### 2. 提取最新的 Census 資料
```python
# 根據年份和日期，找出每個 ZIP Code 最新的 Census 資料
census_dict = extract_latest_census_data(housets_df)
```

### 3. 計算衍生指標
- **貧困率**: (貧困家庭數 / 總人口) × 100
- **失業率**: (失業人口 / 總勞動力) × 100
- **就學率**: (就學人數 / 學齡人口) × 100

### 4. 計算犯罪率
```python
# 使用 Census 資料計算犯罪率（每 1000 居民）
crime_rate = (crime_count / population) * 1000
```

### 5. 整合到 JSON
- 將 Census 資料加入每個 ZIP Code 的資料中
- 使用犯罪率計算 HCI（如果有人口資料）
- 更新範圍資訊（包含犯罪率範圍）

---

## 📊 JSON 結構更新

### Census Data 結構

```json
{
  "data": {
    "20001": {
      "census_data": {
        "total_population": 44056,
        "median_age": 33.1,
        "per_capita_income": 88836.0,
        "total_families_below_poverty": 41993,
        "total_housing_units": 26270,
        "median_rent": 2458.0,
        "median_home_value": 823800.0,
        "total_labor_force": 32375,
        "unemployed_population": 1411,
        "school_age_population": 43185,
        "school_enrollment": 43185,
        "median_commute_time": 2492.0,
        "poverty_rate": 95.3,
        "unemployment_rate": 4.4,
        "school_enrollment_rate": 100.0,
        "bank": 12,
        "bus": 2,
        "hospital": 4,
        "mall": 1,
        "park": 60,
        "restaurant": 45,
        "school_poi": 57,
        "station": 4,
        "supermarket": 7
      }
    }
  }
}
```

### HCI 更新

現在 HCI 計算使用犯罪率（每 1000 居民）而不是犯罪總數：

```json
{
  "hci": {
    "default": {
      "hci_score": 0.634,
      "hci_score_100": 63.4,
      "crime_rate_per_1000": 11.26,  // 每 1000 居民的犯罪數
      "safety_indicator": 0.82,
      ...
    },
    "ranges": {
      "min_crime_rate": 0.5,  // 每 1000 居民
      "max_crime_rate": 50.0,
      ...
    }
  }
}
```

---

## 🔧 使用的腳本

### 1. `scripts/load_housets_from_csv.py`
- 載入 HouseTS.csv
- 篩選 DC 地區的資料
- 提取最新的 Census 資料

### 2. `scripts/combine_data_with_hci.py`
- 整合 Crime、Zillow 和 HouseTS 資料
- 計算 HCI（使用犯罪率）
- 生成 JSON 檔案

---

## 📈 統計結果

### Census 資料覆蓋
- **有 Census 資料的 ZIP Code**: 22 個
- **有人口資料的 ZIP Code**: 22 個
- **有收入資料的 ZIP Code**: 22 個
- **有租金資料的 ZIP Code**: 22 個

### 犯罪率計算
- **使用犯罪率計算 HCI**: ✅ 是
- **犯罪率範圍**: 根據實際資料計算
- **更準確的 HCI 計算**: ✅ 是

---

## 🚀 使用方式

### 執行整合腳本

```bash
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
source venv/bin/activate

python scripts/combine_data_with_hci.py \
  --crime-csv DC_Crime_Incidents_2025_08_09_with_zipcode.csv \
  --zillow-csv dc_zillow_2025_09_30.csv \
  --housets-census-csv HouseTS.csv \
  --output dc_crime_zillow_combined.json
```

### 上傳到 GCP

```bash
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
BUCKET_NAME=$(cat .bucket_name.txt)
gcloud storage cp dc_crime_zillow_combined.json gs://$BUCKET_NAME/data/
gsutil acl ch -u AllUsers:R gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json
```

---

## ✅ 驗證結果

### 檢查 JSON 檔案

```python
import json

with open('dc_crime_zillow_combined.json', 'r') as f:
    data = json.load(f)

# 檢查 Census 資料
census_count = sum(1 for z in data['data'].values() if z.get('census_data'))
print(f'有 Census 資料的 ZIP Code: {census_count}')

# 檢查犯罪率
sample_zip = [z for z in data['data'].values() if z.get('census_data')][0]
crime_rate = sample_zip['hci']['default']['crime_rate_per_1000']
print(f'範例犯罪率: {crime_rate} 每 1000 居民')
```

---

## 📚 相關文件

- `docs/HOUSETS_DATA_ACCESS_GUIDE.md` - 資料取得指南
- `docs/HOUSETS_INTEGRATION_GUIDE.md` - 整合指南
- `scripts/load_housets_from_csv.py` - HouseTS CSV 載入模組
- `scripts/combine_data_with_hci.py` - 資料合併腳本

---

## 🎉 完成！

HouseTS Census 資料已成功整合到 JSON 檔案中，現在可以：
1. ✅ 使用犯罪率（每 1000 居民）計算 HCI
2. ✅ 顯示社會經濟指標（收入、租金、人口等）
3. ✅ 更準確地比較不同 ZIP Code 的安全性
4. ✅ 前端可以使用完整的 Census 資料

