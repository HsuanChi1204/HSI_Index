# 前端快速開始指南

## 🚀 5 分鐘快速開始

### 1. 讀取資料

```typescript
const response = await fetch(
  'https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json'
);
const data = await response.json();
```

### 2. 取得所有 ZIP Code

```typescript
const zipCodes = Object.keys(data.data).sort();
```

### 3. 取得特定 ZIP Code 的資料

```typescript
const zipData = data.data['20001'];
```

### 4. 顯示基本資訊

```typescript
console.log('ZIP Code:', zipData.zip_code);
console.log('房價:', zipData.zillow_data?.current_price);
console.log('總人口:', zipData.census_data?.total_population);
console.log('總犯罪數:', zipData.crime_stats.total_crimes);
console.log('HCI 分數:', zipData.hci.default.hci_score_100);
```

### 5. 計算 HCI（自訂權重）

```typescript
function calculateHCI(zipData, w1 = 0.5, w2 = 0.5, alpha = 0.5) {
  const ranges = zipData.hci.ranges;
  const mom = zipData.zillow_data?.mom ?? 0;
  const yoy = zipData.zillow_data?.yoy ?? 0;
  const crimeCount = zipData.crime_stats.total_crimes;
  const population = zipData.census_data?.total_population;
  
  // 計算成長指標
  const normalizedMom = (mom - ranges.min_mom) / (ranges.max_mom - ranges.min_mom);
  const normalizedYoy = (yoy - ranges.min_yoy) / (ranges.max_yoy - ranges.min_yoy);
  const growthIndicator = alpha * normalizedYoy + (1 - alpha) * normalizedMom;
  
  // 計算安全指標
  let crimeIndicator = 0;
  if (population && ranges.min_crime_rate) {
    const crimeRate = (crimeCount / population) * 1000;
    crimeIndicator = (crimeRate - ranges.min_crime_rate) / 
                     (ranges.max_crime_rate - ranges.min_crime_rate);
  } else {
    crimeIndicator = (crimeCount - ranges.min_crime_count) / 
                     (ranges.max_crime_count - ranges.min_crime_count);
  }
  const safetyIndicator = 1 - crimeIndicator;
  
  // 計算 HCI
  const hciScore = w1 * growthIndicator + w2 * safetyIndicator;
  
  return {
    hci_score_100: Math.round(hciScore * 100 * 100) / 100,
    growth_indicator_100: Math.round(growthIndicator * 100 * 100) / 100,
    safety_indicator_100: Math.round(safetyIndicator * 100 * 100) / 100
  };
}

// 使用
const hciResult = calculateHCI(zipData, 0.6, 0.4, 0.5);
console.log('HCI 分數:', hciResult.hci_score_100);
```

---

## 📋 常用操作

### 取得 HCI 排名

```typescript
function getHCIRanking(data, w1 = 0.5, w2 = 0.5, alpha = 0.5) {
  const results = [];
  
  for (const [zipCode, zipData] of Object.entries(data.data)) {
    const hciResult = calculateHCI(zipData, w1, w2, alpha);
    results.push({
      zipCode,
      hciScore: hciResult.hci_score_100,
      regionName: zipData.zillow_data?.region_name || zipCode
    });
  }
  
  return results.sort((a, b) => b.hciScore - a.hciScore);
}
```

### 篩選 ZIP Code

```typescript
function filterZipCodes(data, minHCI = 0, maxPrice = Infinity) {
  const results = [];
  
  for (const zipData of Object.values(data.data)) {
    const hciScore = zipData.hci.default.hci_score_100;
    const price = zipData.zillow_data?.current_price || 0;
    
    if (hciScore >= minHCI && price <= maxPrice) {
      results.push(zipData);
    }
  }
  
  return results;
}
```

---

## 📚 詳細文件

- **完整 API 說明**: `docs/FRONTEND_API_GUIDE.md`
- **HCI 實作指南**: `docs/HCI_IMPLEMENTATION_GUIDE.md`
- **範例程式碼**: `frontend/test-angular.html`
- **API 範例**: `docs/API_EXAMPLE.json`

---

## 🔗 API URL

```
https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json
```

