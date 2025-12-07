// Angular Service: 動態計算 HCI（用戶自定義權重）
// 這個服務可以在前端動態計算 HCI，根據用戶調整的權重

export interface HCIParams {
  w1: number;  // 成長權重 (0-1)
  w2: number;  // 安全權重 (0-1)
  alpha: number;  // YoY 權重 (0-1)
}

export interface HCIRanges {
  min_mom: number | null;
  max_mom: number | null;
  min_yoy: number | null;
  max_yoy: number | null;
  min_crime_count: number;
  max_crime_count: number;
  min_crime_rate: number | null;
  max_crime_rate: number | null;
}

export interface ZipCodeData {
  zip_code: string;
  zillow_data: {
    mom: number | null;
    yoy: number | null;
    current_price: number | null;
  } | null;
  census_data: {
    total_population: number | null;
    [key: string]: any;
  } | null;
  crime_stats: {
    total_crimes: number;
  };
  hci: {
    default: any;
    ranges: HCIRanges;
  };
}

export interface HCIResult {
  hci_score: number;  // HCI 分數 (0-1)
  hci_score_100: number;  // HCI 分數 (0-100)
  growth_indicator: number;
  growth_indicator_100: number;
  crime_indicator: number;
  crime_indicator_100: number;
  safety_indicator: number;
  safety_indicator_100: number;
  crime_rate_per_1000: number | null;
  weights: {
    w1_growth: number;
    w2_safety: number;
    alpha_yoy: number;
  };
}

export class HCICalculatorService {
  
  /**
   * 標準化到 [0, 1] 範圍
   */
  private normalizeTo01(value: number, minVal: number, maxVal: number): number {
    if (maxVal === minVal) {
      return 0.5;
    }
    const normalized = (value - minVal) / (maxVal - minVal);
    return Math.max(0, Math.min(1, normalized));
  }
  
  /**
   * 計算成長指標 G_z
   * G_z = α * YoY_z + (1 - α) * MoM_z
   */
  private calculateGrowthIndicator(
    momRate: number | null,
    yoyRate: number | null,
    ranges: HCIRanges,
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
  
  /**
   * 計算犯罪指標 C_z
   */
  private calculateCrimeIndicator(
    crimeCount: number,
    population: number | null,
    ranges: HCIRanges
  ): number {
    let crimeRate: number | null = null;
    
    // 如果有人口資料，計算犯罪率
    if (population !== null && population > 0 && 
        ranges.min_crime_rate !== null && ranges.max_crime_rate !== null) {
      crimeRate = (crimeCount / population) * 1000;
      return this.normalizeTo01(crimeRate, ranges.min_crime_rate, ranges.max_crime_rate);
    } else {
      // 使用犯罪總數
      return this.normalizeTo01(crimeCount, ranges.min_crime_count, ranges.max_crime_count);
    }
  }
  
  /**
   * 計算 HCI（論文公式）
   * HCI_z = w1 * G_z + w2 * (1 - C_z)
   */
  calculateHCI(
    zipData: ZipCodeData,
    params: HCIParams
  ): HCIResult {
    const { w1, w2, alpha } = params;
    const ranges = zipData.hci.ranges;
    
    // 取得資料
    const momRate = zipData.zillow_data?.mom ?? null;
    const yoyRate = zipData.zillow_data?.yoy ?? null;
    const crimeCount = zipData.crime_stats.total_crimes;
    const population = zipData.census_data?.total_population ?? null;
    
    // 計算成長指標
    const growthIndicator = this.calculateGrowthIndicator(momRate, yoyRate, ranges, alpha);
    
    // 計算犯罪指標
    const crimeIndicator = this.calculateCrimeIndicator(crimeCount, population, ranges);
    
    // 計算安全指標（1 - C_z）
    const safetyIndicator = 1 - crimeIndicator;
    
    // 計算 HCI
    let hciScore: number;
    if (momRate !== null && yoyRate !== null) {
      // 有成長資料
      hciScore = w1 * growthIndicator + w2 * safetyIndicator;
    } else if (crimeCount > 0) {
      // 只有犯罪資料
      hciScore = w2 * safetyIndicator;
    } else {
      // 沒有資料
      hciScore = 0.0;
    }
    
    // 計算犯罪率
    let crimeRatePer1000: number | null = null;
    if (population !== null && population > 0) {
      crimeRatePer1000 = (crimeCount / population) * 1000;
    }
    
    return {
      hci_score: Math.round(hciScore * 10000) / 10000,  // 保留 4 位小數
      hci_score_100: Math.round(hciScore * 100 * 100) / 100,  // 0-100，保留 2 位小數
      growth_indicator: Math.round(growthIndicator * 10000) / 10000,
      growth_indicator_100: Math.round(growthIndicator * 100 * 100) / 100,
      crime_indicator: Math.round(crimeIndicator * 10000) / 10000,
      crime_indicator_100: Math.round(crimeIndicator * 100 * 100) / 100,
      safety_indicator: Math.round(safetyIndicator * 10000) / 10000,
      safety_indicator_100: Math.round(safetyIndicator * 100 * 100) / 100,
      crime_rate_per_1000: crimeRatePer1000 ? Math.round(crimeRatePer1000 * 100) / 100 : null,
      weights: {
        w1_growth: w1,
        w2_safety: w2,
        alpha_yoy: alpha
      }
    };
  }
  
  /**
   * 計算所有 ZIP Code 的 HCI
   */
  calculateAllHCI(
    data: { [zipCode: string]: ZipCodeData },
    params: HCIParams
  ): { [zipCode: string]: HCIResult } {
    const results: { [zipCode: string]: HCIResult } = {};
    
    for (const zipCode in data) {
      results[zipCode] = this.calculateHCI(data[zipCode], params);
    }
    
    return results;
  }
  
  /**
   * 驗證權重參數
   */
  validateParams(params: HCIParams): { valid: boolean; error?: string } {
    if (params.w1 < 0 || params.w1 > 1) {
      return { valid: false, error: 'w1 (成長權重) 必須在 0-1 之間' };
    }
    if (params.w2 < 0 || params.w2 > 1) {
      return { valid: false, error: 'w2 (安全權重) 必須在 0-1 之間' };
    }
    if (Math.abs(params.w1 + params.w2 - 1) > 0.01) {
      return { valid: false, error: 'w1 + w2 必須等於 1' };
    }
    if (params.alpha < 0 || params.alpha > 1) {
      return { valid: false, error: 'alpha (YoY 權重) 必須在 0-1 之間' };
    }
    return { valid: true };
  }
}

