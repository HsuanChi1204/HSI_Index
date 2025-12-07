# 前端 API 使用說明

## 📋 概述

本文檔說明如何使用 DC Crime & Housing Data JSON API，包含 Crime、Zillow、HouseTS Census 資料以及各種指數計算。

**API URL**: 
```
https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json
```

---

## 🚀 快速開始

### 1. 讀取資料（JavaScript/TypeScript）

```typescript
// 使用 fetch API
async function loadData() {
  const response = await fetch(
    'https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json'
  );
  const data = await response.json();
  return data;
}

// 使用 axios
import axios from 'axios';

async function loadData() {
  const response = await axios.get(
    'https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json'
  );
  return response.data;
}
```

### 2. Angular Service 範例

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CrimeZillowDataService {
  private readonly DATA_URL = 
    'https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json';

  constructor(private http: HttpClient) { }

  getAllData(): Observable<CombinedData> {
    return this.http.get<CombinedData>(this.DATA_URL);
  }

  getZipCodeData(zipCode: string): Observable<ZipCodeData | null> {
    return this.http.get<CombinedData>(this.DATA_URL).pipe(
      map(data => data.data[zipCode] || null)
    );
  }
}
```

---

## 📊 資料結構

### Metadata

```typescript
interface Metadata {
  generated_at: string;           // 資料生成時間 (ISO 8601)
  total_zipcodes: number;         // 總 ZIP Code 數
  total_crimes: number;           // 總犯罪記錄數
  total_zillow_records: number;   // Zillow 資料記錄數
  total_census_records: number;   // Census 資料記錄數
  index_ranges: {
    crime_range: {
      min: number;
      max: number;
    };
    price_range: {
      min: number | null;
      max: number | null;
    };
    crime_rate_range: {
      min: number | null;         // 每 1000 居民的犯罪數
      max: number | null;
    };
  };
  census_summary?: {
    total_zip_codes: number;
    zip_codes_with_population: number;
    population?: {
      min: number;
      max: number;
      mean: number;
      median: number;
    };
    // ... 其他統計資訊
  };
}
```

### ZIP Code 資料

```typescript
interface ZipCodeData {
  zip_code: string;
  
  // Zillow 房價資料
  zillow_data: {
    region_name: string;          // 區域名稱
    state: string;                // 州
    metro: string;                // 都會區
    county_name: string;          // 郡名
    mom: number | null;           // 月對月成長率
    yoy: number | null;           // 年對年成長率
    current_price: number | null; // 當前房價
  } | null;
  
  // HouseTS Census 資料
  census_data: {
    // 人口統計
    total_population: number | null;              // 總人口
    median_age: number | null;                    // 中位數年齡
    
    // 經濟指標
    per_capita_income: number | null;             // 人均收入
    total_families_below_poverty: number | null;  // 貧困家庭數
    poverty_rate: number | null;                  // 貧困率 (%)
    
    // 住房指標
    total_housing_units: number | null;           // 總住房單位數
    median_rent: number | null;                   // 中位數租金
    median_home_value: number | null;             // 中位數房價
    
    // 勞動力指標
    total_labor_force: number | null;             // 總勞動力
    unemployed_population: number | null;         // 失業人口
    unemployment_rate: number | null;             // 失業率 (%)
    
    // 教育指標
    school_age_population: number | null;         // 學齡人口
    school_enrollment: number | null;             // 就學人數
    school_enrollment_rate: number | null;        // 就學率 (%)
    
    // 其他指標
    median_commute_time: number | null;           // 中位數通勤時間（分鐘）
    
    // POI 資料（Points of Interest）
    bank: number;                                 // 銀行數量
    bus: number;                                  // 公車站數量
    hospital: number;                             // 醫院數量
    mall: number;                                 // 購物中心數量
    park: number;                                 // 公園數量
    restaurant: number;                           // 餐廳數量
    school_poi: number;                           // 學校數量（POI）
    station: number;                              // 車站數量
    supermarket: number;                          // 超市數量
  } | null;
  
  // Crime 統計
  crime_stats: {
    total_crimes: number;                         // 總犯罪數
    by_offense: { [offense: string]: number };    // 按犯罪類型統計
    by_shift: { [shift: string]: number };        // 按時段統計 (DAY, EVENING, MIDNIGHT)
    by_ward: { [ward: string]: number };          // 按 WARD 統計
    recent_crimes: Array<{                        // 最近的犯罪記錄
      CCN: string;
      REPORT_DAT: string;
      SHIFT: string;
      METHOD: string;
      OFFENSE: string;
      BLOCK: string;
      WARD: number | null;
      DISTRICT: number | null;
      LATITUDE: number | null;
      LONGITUDE: number | null;
      ZIP_CODE: string;
    }>;
  };
  
  // 現有指數（已計算好的）
  indices: {
    safety_index: number | null;                  // 安全指數 (0-100)
    affordability_index: number | null;           // 可負擔性指數 (0-100)
    premium_index: number | null;                 // 高級指數 (0-100)
    quality_of_life_index: number | null;         // 生活品質指數 (0-100)
    investment_index: number | null;              // 投資價值指數 (0-100)
    crime_index: number | null;                   // 犯罪風險指數 (0-100)
  };
  
  // HCI (Housing-Crime Index) - 論文公式
  hci: {
    // 預設權重計算結果
    default: {
      hci_score: number;                          // HCI 分數 (0-1)
      hci_score_100: number;                      // HCI 分數 (0-100)
      growth_indicator: number;                   // 成長指標 (0-1)
      growth_indicator_100: number;               // 成長指標 (0-100)
      crime_indicator: number;                    // 犯罪指標 (0-1)
      crime_indicator_100: number;                // 犯罪指標 (0-100)
      safety_indicator: number;                   // 安全指標 (0-1) = 1 - crime_indicator
      safety_indicator_100: number;               // 安全指標 (0-100)
      crime_rate_per_1000: number | null;         // 犯罪率（每 1000 居民）
    };
    
    // 用於前端動態計算的範圍資訊
    ranges: {
      min_mom: number | null;                     // MoM 最小值
      max_mom: number | null;                     // MoM 最大值
      min_yoy: number | null;                     // YoY 最小值
      max_yoy: number | null;                     // YoY 最大值
      min_crime_count: number;                    // 犯罪總數最小值
      max_crime_count: number;                    // 犯罪總數最大值
      min_population: number | null;              // 人口最小值
      max_population: number | null;              // 人口最大值
      min_crime_rate: number | null;              // 犯罪率最小值（每 1000 居民）
      max_crime_rate: number | null;              // 犯罪率最大值（每 1000 居民）
    };
  };
  
  // 所有犯罪記錄（詳細資料）
  crimes: Array<{
    CCN: string;
    REPORT_DAT: string;
    SHIFT: string;
    METHOD: string;
    OFFENSE: string;
    BLOCK: string;
    WARD: number | null;
    DISTRICT: number | null;
    LATITUDE: number | null;
    LONGITUDE: number | null;
    ZIP_CODE: string;
  }>;
}

interface CombinedData {
  metadata: Metadata;
  data: { [zipCode: string]: ZipCodeData };
}
```

---

## 💡 使用範例

### 1. 取得所有 ZIP Code 列表

```typescript
async function getAllZipCodes(): Promise<string[]> {
  const data = await loadData();
  return Object.keys(data.data).sort();
}
```

### 2. 取得特定 ZIP Code 的資料

```typescript
async function getZipCodeData(zipCode: string): Promise<ZipCodeData | null> {
  const data = await loadData();
  return data.data[zipCode] || null;
}
```

### 3. 顯示 Zillow 房價資料

```typescript
function displayZillowData(zipData: ZipCodeData) {
  if (!zipData.zillow_data) {
    console.log('沒有 Zillow 資料');
    return;
  }
  
  const zillow = zipData.zillow_data;
  console.log(`區域: ${zillow.region_name}`);
  console.log(`當前房價: $${zillow.current_price?.toLocaleString()}`);
  console.log(`月對月成長: ${(zillow.mom * 100).toFixed(2)}%`);
  console.log(`年對年成長: ${(zillow.yoy * 100).toFixed(2)}%`);
}
```

### 4. 顯示 Census 資料

```typescript
function displayCensusData(zipData: ZipCodeData) {
  if (!zipData.census_data) {
    console.log('沒有 Census 資料');
    return;
  }
  
  const census = zipData.census_data;
  console.log(`總人口: ${census.total_population?.toLocaleString()}`);
  console.log(`人均收入: $${census.per_capita_income?.toLocaleString()}`);
  console.log(`中位數租金: $${census.median_rent?.toLocaleString()}`);
  console.log(`中位數房價: $${census.median_home_value?.toLocaleString()}`);
  console.log(`失業率: ${census.unemployment_rate?.toFixed(2)}%`);
  console.log(`貧困率: ${census.poverty_rate?.toFixed(2)}%`);
}
```

### 5. 顯示 Crime 統計

```typescript
function displayCrimeStats(zipData: ZipCodeData) {
  const crime = zipData.crime_stats;
  console.log(`總犯罪數: ${crime.total_crimes}`);
  
  // 按犯罪類型統計
  console.log('按犯罪類型:');
  Object.entries(crime.by_offense)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .forEach(([offense, count]) => {
      console.log(`  ${offense}: ${count}`);
    });
  
  // 按時段統計
  console.log('按時段:');
  Object.entries(crime.by_shift).forEach(([shift, count]) => {
    console.log(`  ${shift}: ${count}`);
  });
}
```

### 6. 顯示指數

```typescript
function displayIndices(zipData: ZipCodeData) {
  const indices = zipData.indices;
  console.log(`安全指數: ${indices.safety_index?.toFixed(1)}`);
  console.log(`可負擔性指數: ${indices.affordability_index?.toFixed(1)}`);
  console.log(`生活品質指數: ${indices.quality_of_life_index?.toFixed(1)}`);
  console.log(`投資價值指數: ${indices.investment_index?.toFixed(1)}`);
  console.log(`犯罪風險指數: ${indices.crime_index?.toFixed(1)}`);
}
```

### 7. 顯示 HCI（預設權重）

```typescript
function displayHCI(zipData: ZipCodeData) {
  if (!zipData.hci) {
    console.log('沒有 HCI 資料');
    return;
  }
  
  const hci = zipData.hci.default;
  console.log(`HCI 分數: ${hci.hci_score_100.toFixed(1)}`);
  console.log(`成長指標: ${hci.growth_indicator_100.toFixed(1)}`);
  console.log(`安全指標: ${hci.safety_indicator_100.toFixed(1)}`);
  
  if (hci.crime_rate_per_1000 !== null) {
    console.log(`犯罪率（每 1000 居民）: ${hci.crime_rate_per_1000.toFixed(2)}`);
  }
}
```

---

## 🎚️ HCI 動態權重調整

### HCI 公式

```
HCI_z = w1 * G_z + w2 * (1 - C_z)

其中：
- G_z = α * YoY_z + (1 - α) * MoM_z  (成長指標)
- C_z = 犯罪指標（標準化後的犯罪率或犯罪總數）
- w1 = 成長權重（0-1，通常與 w2 相加為 1）
- w2 = 安全權重（0-1，通常與 w1 相加為 1）
- α = YoY 權重（0-1，0 = 只使用 MoM, 1 = 只使用 YoY）
```

### 前端計算 HCI（TypeScript）

```typescript
interface HCIWeights {
  w1: number;    // 成長權重 (0-1)
  w2: number;    // 安全權重 (0-1)
  alpha: number; // YoY 權重 (0-1)
}

function calculateHCI(
  zipData: ZipCodeData,
  weights: HCIWeights
): {
  hci_score: number;
  hci_score_100: number;
  growth_indicator: number;
  growth_indicator_100: number;
  safety_indicator: number;
  safety_indicator_100: number;
  crime_rate_per_1000: number | null;
} {
  const { w1, w2, alpha } = weights;
  const ranges = zipData.hci.ranges;
  
  // 1. 計算成長指標 G_z
  const momRate = zipData.zillow_data?.mom ?? null;
  const yoyRate = zipData.zillow_data?.yoy ?? null;
  
  let growthIndicator = 0;
  if (momRate !== null && yoyRate !== null &&
      ranges.min_mom !== null && ranges.max_mom !== null &&
      ranges.min_yoy !== null && ranges.max_yoy !== null) {
    // 標準化 MoM 和 YoY 到 [0, 1]
    const normalizedMom = (momRate - ranges.min_mom) / (ranges.max_mom - ranges.min_mom);
    const normalizedYoy = (yoyRate - ranges.min_yoy) / (ranges.max_yoy - ranges.min_yoy);
    
    // 計算成長指標
    growthIndicator = alpha * normalizedYoy + (1 - alpha) * normalizedMom;
  }
  
  // 2. 計算犯罪指標 C_z
  const crimeCount = zipData.crime_stats.total_crimes;
  const population = zipData.census_data?.total_population ?? null;
  
  let crimeIndicator = 0;
  let crimeRatePer1000: number | null = null;
  
  // 優先使用犯罪率（如果有人口資料）
  if (population !== null && population > 0 &&
      ranges.min_crime_rate !== null && ranges.max_crime_rate !== null) {
    crimeRatePer1000 = (crimeCount / population) * 1000;
    crimeIndicator = (crimeRatePer1000 - ranges.min_crime_rate) / 
                     (ranges.max_crime_rate - ranges.min_crime_rate);
  } else {
    // 使用犯罪總數
    crimeIndicator = (crimeCount - ranges.min_crime_count) / 
                     (ranges.max_crime_count - ranges.min_crime_count);
  }
  
  // 確保在 [0, 1] 範圍內
  crimeIndicator = Math.max(0, Math.min(1, crimeIndicator));
  
  // 3. 計算安全指標 (1 - C_z)
  const safetyIndicator = 1 - crimeIndicator;
  
  // 4. 計算 HCI
  let hciScore: number;
  if (momRate !== null && yoyRate !== null) {
    hciScore = w1 * growthIndicator + w2 * safetyIndicator;
  } else if (crimeCount > 0) {
    // 如果沒有房價成長資料，HCI 只考慮安全指標
    hciScore = safetyIndicator;
  } else {
    hciScore = 0;
  }
  
  return {
    hci_score: hciScore,
    hci_score_100: Math.round(hciScore * 100 * 100) / 100,
    growth_indicator: growthIndicator,
    growth_indicator_100: Math.round(growthIndicator * 100 * 100) / 100,
    safety_indicator: safetyIndicator,
    safety_indicator_100: Math.round(safetyIndicator * 100 * 100) / 100,
    crime_rate_per_1000: crimeRatePer1000
  };
}
```

### Angular Service 範例（HCI Calculator）

```typescript
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class HciCalculatorService {
  
  private normalizeTo01(value: number, minVal: number, maxVal: number): number {
    if (maxVal === minVal) return 0.5;
    return (value - minVal) / (maxVal - minVal);
  }
  
  calculateGrowthIndicator(
    momRate: number | null,
    yoyRate: number | null,
    ranges: any,
    alpha: number
  ): number {
    if (momRate === null || yoyRate === null ||
        ranges.min_mom === null || ranges.max_mom === null ||
        ranges.min_yoy === null || ranges.max_yoy === null) {
      return 0.0;
    }
    
    const normalizedMom = this.normalizeTo01(momRate, ranges.min_mom, ranges.max_mom);
    const normalizedYoy = this.normalizeTo01(yoyRate, ranges.min_yoy, ranges.max_yoy);
    
    return alpha * normalizedYoy + (1 - alpha) * normalizedMom;
  }
  
  calculateCrimeIndicator(
    crimeCount: number,
    population: number | null,
    ranges: any
  ): number {
    let crimeRate = null;
    
    if (population !== null && population > 0 &&
        ranges.min_crime_rate !== null && ranges.max_crime_rate !== null) {
      crimeRate = (crimeCount / population) * 1000;
      return this.normalizeTo01(crimeRate, ranges.min_crime_rate, ranges.max_crime_rate);
    } else {
      return this.normalizeTo01(crimeCount, ranges.min_crime_count, ranges.max_crime_count);
    }
  }
  
  calculateHCI(
    zipData: ZipCodeData,
    params: { w1: number, w2: number, alpha: number }
  ): any {
    const { w1, w2, alpha } = params;
    const ranges = zipData.hci.ranges;
    const momRate = zipData.zillow_data?.mom ?? null;
    const yoyRate = zipData.zillow_data?.yoy ?? null;
    const crimeCount = zipData.crime_stats.total_crimes;
    const population = zipData.census_data?.total_population ?? null;
    
    const growthIndicator = this.calculateGrowthIndicator(momRate, yoyRate, ranges, alpha);
    const crimeIndicator = this.calculateCrimeIndicator(crimeCount, population, ranges);
    const safetyIndicator = 1 - crimeIndicator;
    
    let hciScore: number;
    if (momRate !== null && yoyRate !== null) {
      hciScore = w1 * growthIndicator + w2 * safetyIndicator;
    } else if (crimeCount > 0) {
      hciScore = safetyIndicator;
    } else {
      hciScore = 0.0;
    }
    
    let crimeRatePer1000: number | null = null;
    if (population !== null && population > 0) {
      crimeRatePer1000 = (crimeCount / population) * 1000;
    }
    
    return {
      hci_score: hciScore,
      hci_score_100: Math.round(hciScore * 100 * 100) / 100,
      growth_indicator: growthIndicator,
      growth_indicator_100: Math.round(growthIndicator * 100 * 100) / 100,
      crime_indicator: crimeIndicator,
      crime_indicator_100: Math.round(crimeIndicator * 100 * 100) / 100,
      safety_indicator: safetyIndicator,
      safety_indicator_100: Math.round(safetyIndicator * 100 * 100) / 100,
      crime_rate_per_1000: crimeRatePer1000 ? Math.round(crimeRatePer1000 * 100) / 100 : null
    };
  }
  
  calculateAllHCI(
    data: { [zipCode: string]: ZipCodeData },
    params: { w1: number, w2: number, alpha: number }
  ): { [zipCode: string]: any } {
    const results: { [zipCode: string]: any } = {};
    for (const zipCode in data) {
      results[zipCode] = this.calculateHCI(data[zipCode], params);
    }
    return results;
  }
}
```

### React 範例（HCI 權重調整）

```typescript
import React, { useState, useEffect } from 'react';

function HCIWeightAdjustment({ zipData }: { zipData: ZipCodeData }) {
  const [weights, setWeights] = useState({
    w1: 0.5,    // 成長權重
    w2: 0.5,    // 安全權重
    alpha: 0.5  // YoY 權重
  });
  
  const [hciResult, setHciResult] = useState<any>(null);
  
  useEffect(() => {
    // 計算 HCI
    const result = calculateHCI(zipData, weights);
    setHciResult(result);
  }, [zipData, weights]);
  
  return (
    <div>
      <h3>HCI 權重調整</h3>
      
      <div>
        <label>
          成長權重 (w1): {Math.round(weights.w1 * 100)}%
          <input
            type="range"
            min="0"
            max="100"
            value={weights.w1 * 100}
            onChange={(e) => {
              const w1 = parseInt(e.target.value) / 100;
              setWeights({
                w1,
                w2: 1 - w1,
                alpha: weights.alpha
              });
            }}
          />
        </label>
      </div>
      
      <div>
        <label>
          安全權重 (w2): {Math.round(weights.w2 * 100)}%
          <input
            type="range"
            min="0"
            max="100"
            value={weights.w2 * 100}
            onChange={(e) => {
              const w2 = parseInt(e.target.value) / 100;
              setWeights({
                w1: 1 - w2,
                w2,
                alpha: weights.alpha
              });
            }}
          />
        </label>
      </div>
      
      <div>
        <label>
          YoY 權重 (α): {Math.round(weights.alpha * 100)}%
          <input
            type="range"
            min="0"
            max="100"
            value={weights.alpha * 100}
            onChange={(e) => {
              setWeights({
                ...weights,
                alpha: parseInt(e.target.value) / 100
              });
            }}
          />
        </label>
      </div>
      
      {hciResult && (
        <div>
          <p>HCI 分數: {hciResult.hci_score_100.toFixed(1)}</p>
          <p>成長指標: {hciResult.growth_indicator_100.toFixed(1)}</p>
          <p>安全指標: {hciResult.safety_indicator_100.toFixed(1)}</p>
          {hciResult.crime_rate_per_1000 && (
            <p>犯罪率（每 1000 居民）: {hciResult.crime_rate_per_1000.toFixed(2)}</p>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## 📊 資料視覺化範例

### 1. 顯示所有 ZIP Code 的 HCI 排名

```typescript
async function getHCIRanking(weights: HCIWeights): Promise<Array<{
  zipCode: string;
  hciScore: number;
  regionName: string;
}>> {
  const data = await loadData();
  const results: Array<{ zipCode: string; hciScore: number; regionName: string }> = [];
  
  for (const [zipCode, zipData] of Object.entries(data.data)) {
    const hciResult = calculateHCI(zipData, weights);
    results.push({
      zipCode,
      hciScore: hciResult.hci_score_100,
      regionName: zipData.zillow_data?.region_name || zipCode
    });
  }
  
  return results.sort((a, b) => b.hciScore - a.hciScore);
}
```

### 2. 篩選 ZIP Code

```typescript
interface FilterCriteria {
  minHCI?: number;
  maxHCI?: number;
  minPrice?: number;
  maxPrice?: number;
  minSafetyIndex?: number;
  hasCensusData?: boolean;
}

function filterZipCodes(
  data: CombinedData,
  criteria: FilterCriteria,
  weights: HCIWeights
): ZipCodeData[] {
  const results: ZipCodeData[] = [];
  
  for (const zipData of Object.values(data.data)) {
    // 計算 HCI
    const hciResult = calculateHCI(zipData, weights);
    
    // 檢查條件
    if (criteria.minHCI && hciResult.hci_score_100 < criteria.minHCI) continue;
    if (criteria.maxHCI && hciResult.hci_score_100 > criteria.maxHCI) continue;
    if (criteria.minPrice && (zipData.zillow_data?.current_price || 0) < criteria.minPrice) continue;
    if (criteria.maxPrice && (zipData.zillow_data?.current_price || Infinity) > criteria.maxPrice) continue;
    if (criteria.minSafetyIndex && (zipData.indices.safety_index || 0) < criteria.minSafetyIndex) continue;
    if (criteria.hasCensusData && !zipData.census_data) continue;
    
    results.push(zipData);
  }
  
  return results;
}
```

---

## ⚠️ 注意事項

### 1. 資料更新
- JSON 檔案會定期更新
- 建議前端實作快取機制
- 檢查 `metadata.generated_at` 來判斷資料是否過期

### 2. 缺失資料處理
- 某些 ZIP Code 可能沒有 Zillow 或 Census 資料
- 檢查 `zillow_data` 和 `census_data` 是否為 `null`
- HCI 計算會自動處理缺失資料的情況

### 3. 資料範圍
- 使用 `metadata.index_ranges` 來了解資料範圍
- 用於標準化或正規化資料

### 4. 犯罪率計算
- 優先使用犯罪率（每 1000 居民）計算 HCI
- 如果沒有 Census 資料，則使用犯罪總數
- 檢查 `crime_rate_per_1000` 是否為 `null`

### 5. 權重調整
- `w1` 和 `w2` 通常相加為 1（但不是必須）
- `alpha` 控制 MoM 和 YoY 的權重
- 權重調整會影響 HCI 分數和排名

---

## 🔗 相關資源

- **API URL**: https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json
- **HCI Calculator Service**: `frontend/hci-calculator.service.ts`
- **範例 HTML**: `frontend/test-angular.html`
- **完整文件**: `docs/HCI_IMPLEMENTATION_GUIDE.md`

---

## 📝 TypeScript 類型定義（完整版）

可以將以下類型定義複製到你的專案中：

```typescript
// types/dc-crime-data.ts

export interface Metadata {
  generated_at: string;
  total_zipcodes: number;
  total_crimes: number;
  total_zillow_records: number;
  total_census_records: number;
  index_ranges: {
    crime_range: { min: number; max: number };
    price_range: { min: number | null; max: number | null };
    crime_rate_range: { min: number | null; max: number | null };
  };
  census_summary?: {
    total_zip_codes: number;
    zip_codes_with_population: number;
    population?: {
      min: number;
      max: number;
      mean: number;
      median: number;
    };
  };
}

export interface ZillowData {
  region_name: string;
  state: string;
  metro: string;
  county_name: string;
  mom: number | null;
  yoy: number | null;
  current_price: number | null;
}

export interface CensusData {
  total_population: number | null;
  median_age: number | null;
  per_capita_income: number | null;
  total_families_below_poverty: number | null;
  poverty_rate: number | null;
  total_housing_units: number | null;
  median_rent: number | null;
  median_home_value: number | null;
  total_labor_force: number | null;
  unemployed_population: number | null;
  unemployment_rate: number | null;
  school_age_population: number | null;
  school_enrollment: number | null;
  school_enrollment_rate: number | null;
  median_commute_time: number | null;
  bank: number;
  bus: number;
  hospital: number;
  mall: number;
  park: number;
  restaurant: number;
  school_poi: number;
  station: number;
  supermarket: number;
}

export interface CrimeStats {
  total_crimes: number;
  by_offense: { [offense: string]: number };
  by_shift: { [shift: string]: number };
  by_ward: { [ward: string]: number };
  recent_crimes: Array<{
    CCN: string;
    REPORT_DAT: string;
    SHIFT: string;
    METHOD: string;
    OFFENSE: string;
    BLOCK: string;
    WARD: number | null;
    DISTRICT: number | null;
    LATITUDE: number | null;
    LONGITUDE: number | null;
    ZIP_CODE: string;
  }>;
}

export interface Indices {
  safety_index: number | null;
  affordability_index: number | null;
  premium_index: number | null;
  quality_of_life_index: number | null;
  investment_index: number | null;
  crime_index: number | null;
}

export interface HCIResult {
  hci_score: number;
  hci_score_100: number;
  growth_indicator: number;
  growth_indicator_100: number;
  crime_indicator: number;
  crime_indicator_100: number;
  safety_indicator: number;
  safety_indicator_100: number;
  crime_rate_per_1000: number | null;
}

export interface HCIRanges {
  min_mom: number | null;
  max_mom: number | null;
  min_yoy: number | null;
  max_yoy: number | null;
  min_crime_count: number;
  max_crime_count: number;
  min_population: number | null;
  max_population: number | null;
  min_crime_rate: number | null;
  max_crime_rate: number | null;
}

export interface HCI {
  default: HCIResult;
  ranges: HCIRanges;
}

export interface CrimeRecord {
  CCN: string;
  REPORT_DAT: string;
  SHIFT: string;
  METHOD: string;
  OFFENSE: string;
  BLOCK: string;
  WARD: number | null;
  DISTRICT: number | null;
  LATITUDE: number | null;
  LONGITUDE: number | null;
  ZIP_CODE: string;
}

export interface ZipCodeData {
  zip_code: string;
  zillow_data: ZillowData | null;
  census_data: CensusData | null;
  crime_stats: CrimeStats;
  indices: Indices;
  hci: HCI;
  crimes: CrimeRecord[];
}

export interface CombinedData {
  metadata: Metadata;
  data: { [zipCode: string]: ZipCodeData };
}

export interface HCIWeights {
  w1: number;    // 成長權重 (0-1)
  w2: number;    // 安全權重 (0-1)
  alpha: number; // YoY 權重 (0-1)
}
```

---

## 🎉 開始使用

現在你已經了解如何使用這個 API 了！如果有任何問題，請參考：
- `docs/HCI_IMPLEMENTATION_GUIDE.md` - HCI 實作詳細說明
- `frontend/test-angular.html` - 完整的前端範例
- `frontend/hci-calculator.service.ts` - HCI 計算服務

祝開發順利！🚀

