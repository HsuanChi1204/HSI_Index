// Angular Component 範例：使用 CrimeZillowDataService
import { Component, OnInit } from '@angular/core';
import { CrimeZillowDataService, ZipCodeData } from './angular-example.service';

@Component({
  selector: 'app-crime-zillow',
  template: `
    <div class="container">
      <h1>DC Crime & Zillow 資料</h1>
      
      <!-- 載入狀態 -->
      <div *ngIf="loading" class="loading">
        載入中...
      </div>
      
      <!-- 錯誤訊息 -->
      <div *ngIf="error" class="error">
        ❌ 錯誤: {{ error }}
      </div>
      
      <!-- 資料顯示 -->
      <div *ngIf="!loading && !error">
        <!-- 統計資訊 -->
        <div class="stats">
          <h2>統計資訊</h2>
          <p>總 ZIP Code 數: {{ statistics?.total_zipcodes }}</p>
          <p>總犯罪記錄數: {{ statistics?.total_crimes }}</p>
          <p>總 Zillow 記錄: {{ statistics?.total_zillow_records }}</p>
        </div>
        
        <!-- ZIP Code 選擇器 -->
        <div class="zip-selector">
          <label>選擇 ZIP Code:</label>
          <select [(ngModel)]="selectedZipCode" (change)="loadZipCodeData()">
            <option value="">-- 請選擇 --</option>
            <option *ngFor="let zip of zipCodeList" [value]="zip">
              {{ zip }}
            </option>
          </select>
        </div>
        
        <!-- ZIP Code 詳細資料 -->
        <div *ngIf="zipCodeData" class="zip-details">
          <h2>ZIP Code {{ selectedZipCode }} 詳細資料</h2>
          
          <!-- Zillow 資料 -->
          <div *ngIf="zipCodeData.zillow_data" class="zillow-data">
            <h3>房價資訊</h3>
            <p>當前價格: ${{ zipCodeData.zillow_data.current_price | number:'1.0-0' }}</p>
            <p>月變化 (MOM): {{ zipCodeData.zillow_data.mom * 100 | number:'1.2-2' }}%</p>
            <p>年變化 (YOY): {{ zipCodeData.zillow_data.yoy * 100 | number:'1.2-2' }}%</p>
          </div>
          
          <!-- Crime 統計 -->
          <div class="crime-stats">
            <h3>犯罪統計</h3>
            <p>總犯罪數: {{ zipCodeData.crime_stats.total_crimes }}</p>
            
            <h4>按犯罪類型</h4>
            <ul>
              <li *ngFor="let item of getOffenseList()">
                {{ item.offense }}: {{ item.count }} 筆
              </li>
            </ul>
            
            <h4>按時段</h4>
            <ul>
              <li *ngFor="let item of getShiftList()">
                {{ item.shift }}: {{ item.count }} 筆
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    .loading {
      text-align: center;
      padding: 20px;
      font-size: 18px;
    }
    .error {
      color: red;
      padding: 20px;
      background: #ffe6e6;
      border-radius: 4px;
    }
    .stats {
      background: #f5f5f5;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 20px;
    }
    .zip-selector {
      margin: 20px 0;
    }
    .zip-selector select {
      padding: 8px 12px;
      font-size: 16px;
      border-radius: 4px;
      border: 1px solid #ddd;
    }
    .zip-details {
      margin-top: 20px;
      padding: 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .zillow-data {
      background: #e8f5e9;
      padding: 15px;
      border-radius: 4px;
      margin-bottom: 20px;
    }
    .crime-stats {
      background: #fff3e0;
      padding: 15px;
      border-radius: 4px;
    }
    ul {
      list-style-type: none;
      padding-left: 0;
    }
    li {
      padding: 5px 0;
      border-bottom: 1px solid #eee;
    }
  `]
})
export class CrimeZillowComponent implements OnInit {
  loading = true;
  error: string | null = null;
  statistics: any = null;
  zipCodeList: string[] = [];
  selectedZipCode: string = '';
  zipCodeData: ZipCodeData | null = null;

  constructor(private dataService: CrimeZillowDataService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.loading = true;
    this.error = null;

    // 載入統計資訊
    this.dataService.getStatistics().subscribe({
      next: (stats) => {
        this.statistics = stats;
      },
      error: (err) => {
        this.error = `載入統計資訊失敗: ${err.message}`;
        this.loading = false;
      }
    });

    // 載入 ZIP Code 列表
    this.dataService.getZipCodeList().subscribe({
      next: (zipCodes) => {
        this.zipCodeList = zipCodes.sort();
        this.loading = false;
      },
      error: (err) => {
        this.error = `載入 ZIP Code 列表失敗: ${err.message}`;
        this.loading = false;
      }
    });
  }

  loadZipCodeData() {
    if (!this.selectedZipCode) {
      this.zipCodeData = null;
      return;
    }

    this.dataService.getZipCodeData(this.selectedZipCode).subscribe({
      next: (data) => {
        this.zipCodeData = data;
      },
      error: (err) => {
        this.error = `載入 ZIP Code 資料失敗: ${err.message}`;
      }
    });
  }

  getOffenseList() {
    if (!this.zipCodeData) return [];
    return Object.entries(this.zipCodeData.crime_stats.by_offense)
      .map(([offense, count]) => ({ offense, count }))
      .sort((a, b) => b.count - a.count);
  }

  getShiftList() {
    if (!this.zipCodeData) return [];
    return Object.entries(this.zipCodeData.crime_stats.by_shift)
      .map(([shift, count]) => ({ shift, count }))
      .sort((a, b) => b.count - a.count);
  }
}

