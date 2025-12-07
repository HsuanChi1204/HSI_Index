# Angular 前端整合快速指南

## 📋 公開 URL

```
https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json
```

## 🚀 快速整合

### 方法 1: 使用提供的 Service（推薦）

1. **複製 Service 到您的 Angular 專案**

```bash
# 複製 Service
cp frontend/angular-example.service.ts src/app/services/crime-zillow-data.service.ts

# 複製 Component（可選）
cp frontend/angular-example.component.ts src/app/components/crime-zillow/
```

2. **在 app.module.ts 或 standalone component 中註冊**

```typescript
import { HttpClientModule } from '@angular/common/http';
import { CrimeZillowDataService } from './services/crime-zillow-data.service';

@NgModule({
  imports: [HttpClientModule],
  providers: [CrimeZillowDataService]
})
```

3. **在 Component 中使用**

```typescript
import { Component, OnInit } from '@angular/core';
import { CrimeZillowDataService } from './services/crime-zillow-data.service';

@Component({
  selector: 'app-my-component',
  template: `<div>{{ data | json }}</div>`
})
export class MyComponent implements OnInit {
  data: any;

  constructor(private dataService: CrimeZillowDataService) {}

  ngOnInit() {
    this.dataService.getAllData().subscribe(data => {
      this.data = data;
    });
  }
}
```

### 方法 2: 直接使用 HttpClient

```typescript
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

const DATA_URL = 'https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json';

@Injectable({ providedIn: 'root' })
export class DataService {
  constructor(private http: HttpClient) {}

  getData(): Observable<any> {
    return this.http.get(DATA_URL);
  }
}
```

## 🧪 測試

開啟測試頁面：
```bash
open frontend/test-angular.html
```

或在瀏覽器中開啟：
```
file:///Users/zhangxuanqi/Downloads/Adv_Spatial_HCI/frontend/test-angular.html
```

## 📊 資料結構

```typescript
interface CombinedData {
  metadata: {
    generated_at: string;
    total_zipcodes: number;
    total_crimes: number;
    total_zillow_records: number;
  };
  data: {
    [zipCode: string]: {
      zip_code: string;
      zillow_data: {
        current_price: number;
        mom: number;
        yoy: number;
      } | null;
      crime_stats: {
        total_crimes: number;
        by_offense: { [key: string]: number };
        by_shift: { [key: string]: number };
      };
      crimes: any[];
    };
  };
}
```

## 💡 使用範例

### 取得所有 ZIP Code

```typescript
this.dataService.getZipCodeList().subscribe(zipCodes => {
  console.log('所有 ZIP Code:', zipCodes);
});
```

### 取得特定 ZIP Code 的資料

```typescript
this.dataService.getZipCodeData('20002').subscribe(data => {
  if (data) {
    console.log('房價:', data.zillow_data?.current_price);
    console.log('犯罪數:', data.crime_stats.total_crimes);
  }
});
```

### 取得統計資訊

```typescript
this.dataService.getStatistics().subscribe(stats => {
  console.log('總 ZIP Code:', stats.total_zipcodes);
  console.log('總犯罪記錄:', stats.total_crimes);
});
```
