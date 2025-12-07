// Angular Service 範例：讀取 GCP Storage JSON 資料
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface ZipCodeData {
  zip_code: string;
  zillow_data: {
    current_price: number;
    mom: number;
    yoy: number;
    region_name: string;
    state: string;
  } | null;
  crime_stats: {
    total_crimes: number;
    by_offense: { [key: string]: number };
    by_shift: { [key: string]: number };
    by_ward: { [key: string]: number };
  };
  crimes: any[];
}

export interface CombinedData {
  metadata: {
    generated_at: string;
    total_zipcodes: number;
    total_crimes: number;
    total_zillow_records: number;
  };
  data: { [zipCode: string]: ZipCodeData };
}

@Injectable({
  providedIn: 'root'
})
export class CrimeZillowDataService {
  // GCP Storage 公開 URL
  private readonly DATA_URL = 'https://storage.googleapis.com/dc-crime-data-zhangxuanqi-1762814591/data/dc_crime_zillow_combined.json';

  constructor(private http: HttpClient) {}

  /**
   * 取得所有資料
   */
  getAllData(): Observable<CombinedData> {
    return this.http.get<CombinedData>(this.DATA_URL);
  }

  /**
   * 取得特定 ZIP Code 的資料
   */
  getZipCodeData(zipCode: string): Observable<ZipCodeData | null> {
    return this.getAllData().pipe(
      map(data => data.data[zipCode] || null)
    );
  }

  /**
   * 取得所有 ZIP Code 列表
   */
  getZipCodeList(): Observable<string[]> {
    return this.getAllData().pipe(
      map(data => Object.keys(data.data))
    );
  }

  /**
   * 取得統計資訊
   */
  getStatistics(): Observable<CombinedData['metadata']> {
    return this.getAllData().pipe(
      map(data => data.metadata)
    );
  }

  /**
   * 取得有 Zillow 資料的 ZIP Code
   */
  getZipCodesWithZillow(): Observable<string[]> {
    return this.getAllData().pipe(
      map(data => {
        return Object.keys(data.data).filter(
          zipCode => data.data[zipCode].zillow_data !== null
        );
      })
    );
  }
}

