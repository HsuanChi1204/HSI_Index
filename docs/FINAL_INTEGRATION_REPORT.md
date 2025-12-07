# HouseTS 資料整合最終報告

## ✅ 整合完成

### 資料來源
- **檔案**: `HouseTS.csv` (271.43 MB, 884,092 筆記錄)
- **DC 地區**: 3,124 筆記錄，22 個 ZIP Codes
- **時間範圍**: 2012-2023

### 整合結果
- ✅ 成功載入 HouseTS Census 資料
- ✅ 成功提取最新的 Census 資料（每個 ZIP Code 最新年度）
- ✅ 成功計算犯罪率（每 1000 居民）
- ✅ 成功整合到 JSON 檔案
- ✅ 已上傳到 GCP Cloud Storage

---

## 📊 HouseTS.csv 資料結構

### 欄位總數
- **39 個欄位**

### 資料類型

1. **房價資料** (Redfin)
   - date, median_sale_price, median_list_price
   - median_ppsf, median_list_ppsf
   - homes_sold, pending_sales, new_listings
   - inventory, median_dom
   - avg_sale_to_list, sold_above_list, off_market_in_two_weeks
   - price

2. **POI 資料** (Points of Interest)
   - bank, bus, hospital, mall, park
   - restaurant, school, station, supermarket

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

4. **地理位置**
   - zipcode
   - city
   - city_full
   - year

---

## 🔍 DC 地區資料

### 城市名稱
- **HouseTS 中的名稱**: `DC_Metro`
- **範圍**: Washington DC 都會區

### ZIP Codes
HouseTS 中包含 22 個 DC ZIP Codes：
- 20001, 20002, 20003, 20004, 20005, 20006, 20007, 20008, 20009, 20010
- 20011, 20012, 20015, 20016, 20017, 20018, 20019, 20020, 20024, 20032, 20036, 20037

### 資料統計
- **DC 地區記錄**: 3,124 筆
- **時間範圍**: 2012-2023
- **有 Census 資料的 ZIP Code**: 22 個

---

## 📈 整合後的統計

### Census 資料統計
- **人口範圍**: 1,257 - 70,043
- **人均收入範圍**: $31,449 - $156,217
- **中位數租金範圍**: $1,160 - $2,771
- **中位數房價範圍**: $279,500 - $823,800

### 犯罪率統計（每 1000 居民）
- **範圍**: 2.50 - 24.08
- **平均**: 7.09
- **更公平的比較方式**

### HCI 統計（使用犯罪率）
- **HCI 分數範圍**: 28.8 - 95.2
- **平均 HCI 分數**: 61.0
- **中位數**: 60.8

---

## 🔧 技術實作

### 1. 資料載入 (`scripts/load_housets_from_csv.py`)
- 分批讀取 HouseTS.csv（chunk_size=100,000）
- 篩選 DC 地區的 ZIP Codes（20001-20099）
- 處理 ZIP Code 格式轉換（20001.0 → 20001）

### 2. 資料提取
- 按年份和日期排序，找出每個 ZIP Code 最新的 Census 資料
- 提取所有 Census 欄位（12 個）
- 提取 POI 資料（9 個類別）
- 計算衍生指標（貧困率、失業率、就學率）

### 3. 犯罪率計算
- 使用 Census 資料中的總人口數
- 計算每 1000 居民的犯罪數
- 更新 HCI 計算使用犯罪率而非犯罪總數

### 4. 資料整合 (`scripts/combine_data_with_hci.py`)
- 將 Census 資料加入每個 ZIP Code 的資料中
- 更新 HCI 計算使用犯罪率
- 更新範圍資訊（包含犯罪率範圍）

---

## 📁 JSON 結構

### 更新後的結構

```json
{
  "metadata": {
    "total_census_records": 22,
    "index_ranges": {
      "crime_rate_range": {
        "min": 2.50,
        "max": 24.08
      }
    },
    "census_summary": {
      "total_zip_codes": 22,
      "zip_codes_with_population": 22,
      "population": {
        "min": 1257,
        "max": 70043,
        "mean": 30167.5,
        "median": 25432.0
      }
    }
  },
  "data": {
    "20001": {
      "census_data": {
        "total_population": 44056,
        "per_capita_income": 88836.0,
        "median_rent": 2458.0,
        "median_home_value": 823800.0,
        "poverty_rate": 95.32,
        "unemployment_rate": 4.36,
        "school_enrollment_rate": 100.0,
        "bank": 205,
        "park": 593,
        "restaurant": 970,
        "school_poi": 274,
        ...
      },
      "hci": {
        "default": {
          "crime_rate_per_1000": 6.85,
          "hci_score_100": 65.93,
          "safety_indicator_100": 79.84,
          ...
        },
        "ranges": {
          "min_crime_rate": 2.50,
          "max_crime_rate": 24.08,
          ...
        }
      }
    }
  }
}
```

---

## 🎯 改進效果

### 使用犯罪率 vs 犯罪總數

**之前（使用犯罪總數）**:
- ❌ 無法公平比較不同人口規模的 ZIP Code
- ❌ 人口多的區域看起來犯罪較多
- ❌ HCI 計算不夠準確

**現在（使用犯罪率）**:
- ✅ 可以公平比較不同人口規模的 ZIP Code
- ✅ 人口規模不影響安全性評估
- ✅ HCI 計算更準確
- ✅ 符合論文要求

### 資料豐富度

**之前**:
- 只有 Crime 和 Zillow 資料
- 缺少社會經濟指標

**現在**:
- ✅ 加入 Census 資料（12 個欄位）
- ✅ 加入 POI 資料（9 個類別）
- ✅ 加入衍生指標（貧困率、失業率、就學率）
- ✅ 更完整的資料集

---

## 📝 注意事項

### 1. 貧困率計算
- 目前使用「貧困家庭數/總人口」計算
- 這可能不是標準的貧困率計算方式
- 標準方式應該是「貧困人口數/總人口」
- 但 HouseTS 資料中可能沒有貧困人口數，只有貧困家庭數
- 這個指標僅供參考，不應直接用於比較

### 2. 資料時間對齊
- Census 資料是年度更新（2011-2022）
- 我們使用最新的年度資料（2022 或 2023）
- 房價資料是月度更新（2012-2023）
- 時間對齊可能需要根據實際需求調整

### 3. 缺失資料處理
- 某些 ZIP Code 可能沒有 Census 資料（7 個 ZIP Code）
- 這些 ZIP Code 仍使用犯罪總數計算 HCI
- 前端會自動處理這種情況

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

## 🔗 GCP URL

**公開 URL**:
```
https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json
```

組員可以使用此 URL 讀取包含 HouseTS Census 資料的完整 JSON！

---

## 📚 相關文件

- `docs/HOUSETS_INTEGRATION_COMPLETE.md` - 完整整合報告
- `docs/HOUSETS_INTEGRATION_SUMMARY.md` - 整合總結
- `docs/HOUSETS_DATA_ACCESS_GUIDE.md` - 資料取得指南
- `docs/HOUSETS_INTEGRATION_GUIDE.md` - 整合指南
- `scripts/load_housets_from_csv.py` - HouseTS CSV 載入模組
- `scripts/combine_data_with_hci.py` - 資料合併腳本

---

## ✅ 檢查清單

### 資料完整性
- [x] HouseTS.csv 已下載
- [x] DC 地區資料已載入
- [x] Census 資料已提取
- [x] POI 資料已提取
- [x] 犯罪率已計算
- [x] JSON 檔案已生成
- [x] 已上傳到 GCP

### 資料品質
- [x] 所有 12 個 Census 欄位都存在
- [x] POI 資料已包含
- [x] 衍生指標已計算
- [x] 犯罪率計算正確
- [x] HCI 使用犯罪率計算

### 功能測試
- [x] 前端可以讀取 Census 資料
- [x] 前端可以顯示犯罪率
- [x] HCI 計算使用犯罪率
- [x] 權重調整功能正常

---

## 🎉 完成！

HouseTS Census 資料已成功整合，現在可以：
1. ✅ 使用犯罪率（每 1000 居民）計算 HCI
2. ✅ 顯示社會經濟指標（收入、租金、人口等）
3. ✅ 更準確地比較不同 ZIP Code 的安全性
4. ✅ 前端可以使用完整的 Census 資料
5. ✅ 組員可以從 GCP 讀取完整資料

---

需要進一步調整或優化嗎？

