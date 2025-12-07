# HouseTS Census Data 整合指南

## 📋 概述

本指南說明如何整合 HouseTS Census Data 到專案中，用於計算犯罪率（每 1000 居民）和加入社會經濟指標。

---

## 📊 HouseTS Census Data 欄位

### 必需欄位

根據論文描述，HouseTS Census Data 包含以下欄位：

1. **Total Population** - 總人口數
2. **Median Age** - 中位數年齡
3. **Per Capita Income** - 人均收入
4. **Total Families Below Poverty** - 貧困家庭數
5. **Total Housing Units** - 總住房單位數
6. **Median Rent** - 中位數租金
7. **Median Home Value** - 中位數房價
8. **Total Labor Force** - 總勞動力
9. **Unemployed Population** - 失業人口
10. **School-Age Population** - 學齡人口
11. **School Enrollment** - 就學人數
12. **Median Commute Time** - 中位數通勤時間

---

## 📁 CSV 檔案格式

### 預期的 CSV 格式

```csv
ZIPCode,Total Population,Median Age,Per Capita Income,Total Families Below Poverty,Total Housing Units,Median Rent,Median Home Value,Total Labor Force,Unemployed Population,School-Age Population,School Enrollment,Median Commute Time
20002,50000,35.5,45000,5000,20000,1500,600000,30000,1500,8000,7500,25.5
20011,45000,32.0,42000,4500,18000,1400,580000,27000,1350,7200,6800,24.0
...
```

### ZIP Code 欄位名稱

腳本會自動偵測以下可能的 ZIP Code 欄位名稱：
- `zip_code`
- `ZIPCode`
- `ZIP`
- `zipcode`
- `ZIP_CODE`

---

## 🔧 使用方式

### 步驟 1: 準備 CSV 檔案

1. **取得 HouseTS Census Data**
   - 從 HouseTS 資料集取得 DC 地區的 Census Data
   - 確保包含所有必要的欄位

2. **將檔案放在專案根目錄**
   ```bash
   # 例如：housets_census.csv
   cp /path/to/housets_census.csv /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI/
   ```

### 步驟 2: 執行合併腳本

```bash
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
source venv/bin/activate

# 執行合併腳本（包含 HouseTS Census Data）
python scripts/combine_data_with_hci.py \
  --crime-csv DC_Crime_Incidents_2025_08_09_with_zipcode.csv \
  --zillow-csv dc_zillow_2025_09_30.csv \
  --housets-census-csv housets_census.csv \
  --output dc_crime_zillow_combined.json
```

### 步驟 3: 檢查結果

```bash
# 檢查 JSON 檔案
python3 -c "
import json
with open('dc_crime_zillow_combined.json', 'r') as f:
    data = json.load(f)

# 檢查 Census 資料
census_count = sum(1 for z in data['data'].values() if z.get('census_data'))
print(f'有 Census 資料的 ZIP Code: {census_count}/{len(data[\"data\"])}')

# 檢查犯罪率
if census_count > 0:
    sample_zip = [z for z in data['data'].values() if z.get('census_data')][0]
    if sample_zip['hci']['default']:
        crime_rate = sample_zip['hci']['default'].get('crime_rate_per_1000')
        print(f'範例犯罪率（每 1000 居民）: {crime_rate}')
"
```

---

## 📊 資料處理流程

### 1. 載入 Census Data

```python
from load_housets_census import load_housets_census_data

census_df = load_housets_census_data('housets_census.csv')
```

### 2. 處理 DC ZIP Code

```python
from load_housets_census import process_housets_census_for_dc

dc_zip_codes = ['20002', '20011', '20019', ...]  # DC ZIP Code 列表
census_dict = process_housets_census_for_dc(census_df, dc_zip_codes)
```

### 3. 計算犯罪率

```python
# 計算每 1000 居民的犯罪率
crime_rate = (crime_count / population) * 1000
```

### 4. 計算衍生指標

腳本會自動計算以下衍生指標：
- **貧困率**: (貧困家庭數 / 總人口) × 100
- **失業率**: (失業人口 / 總勞動力) × 100
- **就學率**: (就學人數 / 學齡人口) × 100

---

## 📝 JSON 結構更新

### Census Data 結構

```json
{
  "data": {
    "20002": {
      "census_data": {
        "total_population": 50000,
        "median_age": 35.5,
        "per_capita_income": 45000,
        "total_families_below_poverty": 5000,
        "total_housing_units": 20000,
        "median_rent": 1500,
        "median_home_value": 600000,
        "total_labor_force": 30000,
        "unemployed_population": 1500,
        "school_age_population": 8000,
        "school_enrollment": 7500,
        "median_commute_time": 25.5,
        "poverty_rate": 10.0,
        "unemployment_rate": 5.0,
        "school_enrollment_rate": 93.75
      }
    }
  }
}
```

---

## 🔍 驗證資料

### 檢查 Census 資料完整性

```python
from load_housets_census import get_census_data_summary

summary = get_census_data_summary(census_dict)
print(f"總 ZIP Code 數: {summary['total_zip_codes']}")
print(f"有人口資料的 ZIP Code: {summary['zip_codes_with_population']}")
print(f"有收入資料的 ZIP Code: {summary['zip_codes_with_income']}")
```

### 檢查犯罪率計算

```python
# 檢查犯罪率範圍
crime_rates = []
for zip_code, data in zipcode_data.items():
    if data.get('census_data') and data.get('crime_stats'):
        population = data['census_data']['total_population']
        crime_count = data['crime_stats']['total_crimes']
        if population and population > 0:
            crime_rate = (crime_count / population) * 1000
            crime_rates.append(crime_rate)

print(f"犯罪率範圍（每 1000 居民）: {min(crime_rates):.2f} - {max(crime_rates):.2f}")
```

---

## ⚠️ 注意事項

### 1. 資料對齊

- 確保 HouseTS Census Data 的 ZIP Code 與 Crime/Zillow 資料對齊
- 如果某些 ZIP Code 沒有 Census 資料，系統會使用犯罪總數而非犯罪率

### 2. 資料品質

- 檢查人口資料是否為 0 或負數
- 檢查缺失值處理
- 驗證資料範圍是否合理

### 3. 時間對齊

- HouseTS Census Data 可能是年度資料
- 確保 Census Data 的時間與 Crime/Zillow 資料對齊
- 如果時間不一致，需要在論文中說明

---

## 🚀 整合到現有系統

### 1. 更新資料處理流程

```python
# 在 combine_data_with_hci.py 中
if housets_census_csv and os.path.exists(housets_census_csv):
    census_dict = process_housets_census_for_dc(census_df, dc_zip_codes)
    # 使用 Census 資料計算犯罪率
else:
    # 使用犯罪總數
    pass
```

### 2. 更新 HCI 計算

```python
# 在 calculate_hci_paper.py 中
if population is not None:
    # 使用犯罪率（每 1000 居民）
    crime_rate = (crime_count / population) * 1000
else:
    # 使用犯罪總數
    pass
```

### 3. 更新前端顯示

```typescript
// 在前端顯示 Census 資料
if (zipData.census_data) {
  console.log('人口:', zipData.census_data.total_population);
  console.log('人均收入:', zipData.census_data.per_capita_income);
  console.log('犯罪率（每 1000 居民）:', hciResult.crime_rate_per_1000);
}
```

---

## 📚 相關文件

- `scripts/load_housets_census.py`: Census Data 載入模組
- `scripts/combine_data_with_hci.py`: 資料合併腳本
- `scripts/calculate_hci_paper.py`: HCI 計算模組（支援犯罪率）
- `docs/HCI_IMPLEMENTATION_GUIDE.md`: HCI 實作指南

---

## 🆘 疑難排解

### 問題 1: 找不到 ZIP Code 欄位

**錯誤訊息**: `❌ 找不到 ZIP Code 欄位`

**解決方法**:
1. 檢查 CSV 檔案的第一行（欄位名稱）
2. 確認 ZIP Code 欄位名稱是否為以下之一：
   - `zip_code`, `ZIPCode`, `ZIP`, `zipcode`, `ZIP_CODE`
3. 如果欄位名稱不同，修改 `load_housets_census.py` 中的欄位名稱列表

### 問題 2: 沒有匹配的 ZIP Code

**錯誤訊息**: `✅ 找到 0 筆 DC Census 資料`

**解決方法**:
1. 檢查 HouseTS Census Data 中的 ZIP Code 格式
2. 確保 ZIP Code 與 Crime/Zillow 資料一致
3. 檢查是否有前導零（例如 `02002` vs `20002`）

### 問題 3: 人口資料為 0 或缺失

**解決方法**:
1. 檢查原始資料
2. 過濾掉人口為 0 或缺失的記錄
3. 在計算犯罪率時檢查人口是否有效

---

需要協助測試或調整嗎？

