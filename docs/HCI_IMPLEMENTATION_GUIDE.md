# HCI 實作指南

## 📋 概述

本指南說明如何實作論文中的 HCI (Housing-Crime Index) 計算，支援用戶自定義權重，並整合 HouseTS Census Data。

---

## 🎯 功能需求

### 1. 用戶可調整權重
- 用戶可以自由調整房價成長和犯罪安全性的權重（例如 60%/40%）
- 前端動態計算 HCI 並顯示對應的區域或內容

### 2. 保留現有指數，新增論文中的 HCI
- 保留現有的多個指數（安全指數、可負擔性指數等）
- 新增論文中的 HCI 計算方式（結合 MoM 和 YoY）
- 前端可以選擇不同的指數顯示

### 3. 整合 HouseTS Census Data
- 使用 HouseTS 資料集中的 Census Data
- 計算犯罪率（每 1000 居民）
- 加入社會經濟指標

---

## 📊 HCI 計算公式（論文）

### 主要公式

```
HCI_z = w1 * G_z + w2 * (1 - C_z)
```

其中：
- `w1`: 成長權重（用戶可調整）
- `w2`: 安全權重（用戶可調整）
- `G_z`: 成長指標（結合 MoM 和 YoY）
- `C_z`: 犯罪指標（標準化的犯罪率或犯罪數）

### 子公式

**成長指標**:
```
G_z = α * YoY_z + (1 - α) * MoM_z
```

**犯罪指標**:
```
C_z = 標準化的犯罪率（每 1000 居民）或犯罪總數
```

**標準化**:
```
x̃_z = (x_z - min(x)) / (max(x) - min(x))
```

---

## 🔧 實作步驟

### 步驟 1: 準備 HouseTS Census Data

1. **取得 HouseTS Census Data CSV 檔案**
   - 欄位應包含：Total Population, Median Age, Per Capita Income, 等

2. **將檔案放在專案根目錄**
   ```bash
   # 例如：housets_census.csv
   ```

### 步驟 2: 執行合併腳本

```bash
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
source venv/bin/activate

# 如果有 HouseTS Census Data
python scripts/combine_data_with_hci.py \
  --crime-csv DC_Crime_Incidents_2025_08_09_with_zipcode.csv \
  --zillow-csv dc_zillow_2025_09_30.csv \
  --housets-census-csv housets_census.csv \
  --output dc_crime_zillow_combined.json

# 如果沒有 HouseTS Census Data（使用犯罪總數）
python scripts/combine_data_with_hci.py \
  --crime-csv DC_Crime_Incidents_2025_08_09_with_zipcode.csv \
  --zillow-csv dc_zillow_2025_09_30.csv \
  --output dc_crime_zillow_combined.json
```

### 步驟 3: 上傳到 GCP Storage

```bash
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
BUCKET_NAME=$(cat .bucket_name.txt)
gcloud storage cp dc_crime_zillow_combined.json gs://$BUCKET_NAME/data/
gsutil acl ch -u AllUsers:R gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json
```

---

## 📁 JSON 資料結構

### 更新後的結構

```json
{
  "metadata": {
    "index_ranges": {
      "crime_range": {"min": 2, "max": 496},
      "price_range": {"min": 240203.0, "max": 1346126.0},
      "mom_range": {"min": -1.0967, "max": 0.2729},
      "yoy_range": {"min": -6.3745, "max": 1.9375},
      "crime_rate_range": {"min": 0.5, "max": 50.0}
    },
    "census_summary": {
      "total_zip_codes": 29,
      "zip_codes_with_population": 22
    }
  },
  "data": {
    "20002": {
      "zip_code": "20002",
      "zillow_data": {
        "mom": -0.127,
        "yoy": -5.152,
        "current_price": 618260.87
      },
      "census_data": {
        "total_population": 50000,
        "per_capita_income": 45000,
        "median_rent": 1500,
        ...
      },
      "crime_stats": {
        "total_crimes": 496
      },
      "indices": {
        "safety_index": 75.5,
        "affordability_index": 45.2,
        "quality_of_life_index": 63.4,
        ...
      },
      "hci": {
        "default": {
          "hci_score": 0.634,
          "hci_score_100": 63.4,
          "growth_indicator": 0.45,
          "safety_indicator": 0.82,
          ...
        },
        "ranges": {
          "min_mom": -1.0967,
          "max_mom": 0.2729,
          "min_yoy": -6.3745,
          "max_yoy": 1.9375,
          "min_crime_count": 2,
          "max_crime_count": 496,
          "min_crime_rate": 0.5,
          "max_crime_rate": 50.0
        }
      }
    }
  }
}
```

---

## 💻 前端使用方式

### 1. 使用 HCI Calculator Service

```typescript
import { HCICalculatorService, HCIParams } from './hci-calculator.service';

// 建立服務實例
const hciCalculator = new HCICalculatorService();

// 用戶調整權重
const params: HCIParams = {
  w1: 0.6,    // 成長權重 60%
  w2: 0.4,    // 安全權重 40%
  alpha: 0.5  // YoY 權重 50%
};

// 計算特定 ZIP Code 的 HCI
const zipData = data.data['20002'];
const hciResult = hciCalculator.calculateHCI(zipData, params);

console.log('HCI 分數:', hciResult.hci_score_100);  // 0-100
console.log('成長指標:', hciResult.growth_indicator_100);
console.log('安全指標:', hciResult.safety_indicator_100);
```

### 2. 動態計算所有 ZIP Code

```typescript
// 計算所有 ZIP Code 的 HCI
const allHCI = hciCalculator.calculateAllHCI(data.data, params);

// 排序並顯示
const sortedZIPs = Object.entries(allHCI)
  .sort((a, b) => b[1].hci_score_100 - a[1].hci_score_100)
  .slice(0, 10);

console.log('前 10 名 ZIP Code:');
sortedZIPs.forEach(([zip, hci]) => {
  console.log(`${zip}: HCI = ${hci.hci_score_100}`);
});
```

### 3. 在 Angular Component 中使用

```typescript
import { Component } from '@angular/core';
import { HCICalculatorService, HCIParams } from './hci-calculator.service';

@Component({
  selector: 'app-hci-calculator',
  template: `
    <div>
      <h2>調整 HCI 權重</h2>
      
      <label>成長權重 (w1): {{ w1 }}</label>
      <input type="range" [(ngModel)]="w1" min="0" max="1" step="0.1" 
             (input)="updateHCI()">
      
      <label>安全權重 (w2): {{ w2 }}</label>
      <input type="range" [(ngModel)]="w2" min="0" max="1" step="0.1" 
             (input)="updateHCI()">
      
      <div *ngFor="let zip of sortedZIPs">
        ZIP {{ zip.code }}: HCI = {{ zip.hci }}
      </div>
    </div>
  `
})
export class HCICalculatorComponent {
  w1 = 0.6;
  w2 = 0.4;
  alpha = 0.5;
  sortedZIPs: any[] = [];
  
  constructor(private hciCalculator: HCICalculatorService) {}
  
  updateHCI() {
    // 確保 w1 + w2 = 1
    const total = this.w1 + this.w2;
    if (total !== 1) {
      this.w2 = 1 - this.w1;
    }
    
    const params: HCIParams = {
      w1: this.w1,
      w2: this.w2,
      alpha: this.alpha
    };
    
    // 計算所有 ZIP Code 的 HCI
    const allHCI = this.hciCalculator.calculateAllHCI(this.data.data, params);
    
    // 排序
    this.sortedZIPs = Object.entries(allHCI)
      .map(([zip, hci]) => ({
        code: zip,
        hci: hci.hci_score_100
      }))
      .sort((a, b) => b.hci - a.hci);
  }
}
```

---

## 📝 HouseTS Census Data 欄位說明

### 必需欄位

- `Total Population`: 總人口數（用於計算犯罪率）
- `Per Capita Income`: 人均收入
- `Median Rent`: 中位數租金
- `Median Home Value`: 中位數房價

### 可選欄位

- `Median Age`: 中位數年齡
- `Total Families Below Poverty`: 貧困家庭數
- `Total Housing Units`: 總住房單位數
- `Total Labor Force`: 總勞動力
- `Unemployed Population`: 失業人口
- `School-Age Population`: 學齡人口
- `School Enrollment`: 就學人數
- `Median Commute Time`: 中位數通勤時間

### CSV 檔案格式

```csv
ZIPCode,Total Population,Median Age,Per Capita Income,Median Rent,Median Home Value,...
20002,50000,35.5,45000,1500,600000,...
20011,45000,32.0,42000,1400,580000,...
...
```

---

## 🔄 資料流程

```
1. 載入 Crime 資料
2. 載入 Zillow 資料
3. 載入 HouseTS Census 資料（可選）
4. 計算統計範圍（MoM, YoY, 犯罪數, 犯罪率）
5. 計算現有的多個指數
6. 計算論文中的 HCI（預設權重）
7. 儲存範圍資訊（供前端動態計算）
8. 生成 JSON 檔案
9. 上傳到 GCP Storage
```

---

## 🎨 前端顯示建議

### 1. 權重調整滑桿

```html
<div class="weight-controls">
  <label>成長權重 (w1): {{ w1 * 100 }}%</label>
  <input type="range" [(ngModel)]="w1" min="0" max="1" step="0.1">
  
  <label>安全權重 (w2): {{ w2 * 100 }}%</label>
  <input type="range" [(ngModel)]="w2" min="0" max="1" step="0.1">
</div>
```

### 2. 指數選擇器

```html
<select [(ngModel)]="selectedIndex">
  <option value="hci">HCI (論文公式)</option>
  <option value="quality_of_life">生活品質指數</option>
  <option value="safety">安全指數</option>
  <option value="affordability">可負擔性指數</option>
  <option value="investment">投資價值指數</option>
</select>
```

### 3. 地圖視覺化

```typescript
// 根據選擇的指數和權重顯示地圖
updateMap() {
  let scores: { [zip: string]: number } = {};
  
  if (this.selectedIndex === 'hci') {
    // 使用動態計算的 HCI
    const hciResults = this.hciCalculator.calculateAllHCI(
      this.data.data,
      { w1: this.w1, w2: this.w2, alpha: this.alpha }
    );
    scores = Object.fromEntries(
      Object.entries(hciResults).map(([zip, hci]) => [zip, hci.hci_score_100])
    );
  } else {
    // 使用預計算的指數
    scores = Object.fromEntries(
      Object.entries(this.data.data).map(([zip, data]) => [
        zip,
        data.indices[this.selectedIndex] || 0
      ])
    );
  }
  
  // 更新地圖顏色
  this.updateMapColors(scores);
}
```

---

## ✅ 檢查清單

### 資料準備
- [ ] HouseTS Census Data CSV 檔案已準備
- [ ] CSV 檔案包含必要的欄位
- [ ] ZIP Code 欄位名稱正確

### 腳本執行
- [ ] 執行 `combine_data_with_hci.py`
- [ ] 檢查 JSON 檔案是否包含 HCI 資料
- [ ] 檢查範圍資訊是否正確

### 前端整合
- [ ] 加入 HCI Calculator Service
- [ ] 實作權重調整 UI
- [ ] 實作指數選擇器
- [ ] 測試動態計算功能

### 測試
- [ ] 測試不同權重組合
- [ ] 測試有/沒有 Census 資料的情況
- [ ] 測試前端動態計算
- [ ] 測試地圖視覺化

---

## 📚 相關文件

- `scripts/calculate_hci_paper.py`: HCI 計算模組
- `scripts/load_housets_census.py`: HouseTS Census Data 載入模組
- `scripts/combine_data_with_hci.py`: 資料合併腳本
- `frontend/hci-calculator.service.ts`: 前端 HCI 計算服務

---

需要協助測試或調整嗎？

