# 用戶權重調整功能說明

## 📋 功能概述

用戶可以自由調整 HCI 計算中的權重，以反映個人偏好：
- **成長權重 (w1)**: 重視房價成長的程度
- **安全權重 (w2)**: 重視安全性的程度
- **YoY 權重 (α)**: 在成長指標中，重視長期趨勢（YoY）vs 短期波動（MoM）的程度

---

## 🎯 使用場景

### 場景 1: 投資者（重視成長）

- **w1 = 70%**: 重視房價成長
- **w2 = 30%**: 較不重視安全性
- **α = 60%**: 重視長期趨勢（YoY）

**結果**: 顯示高成長潛力的區域，即使安全性較低

### 場景 2: 居住者（重視安全）

- **w1 = 30%**: 較不重視房價成長
- **w2 = 70%**: 重視安全性
- **α = 40%**: 稍微重視短期波動（MoM）

**結果**: 顯示安全性高的區域，即使成長潛力較低

### 場景 3: 平衡型（均衡考量）

- **w1 = 50%**: 平衡成長和安全性
- **w2 = 50%**: 平衡成長和安全性
- **α = 50%**: 平衡長期和短期趨勢

**結果**: 顯示成長和安全平衡的區域

---

## 💻 前端使用方式

### 1. 調整權重滑桿

```html
<!-- 成長權重 -->
<input type="range" id="w1Slider" min="0" max="100" value="60">
<!-- 安全權重 -->
<input type="range" id="w2Slider" min="0" max="100" value="40">
<!-- YoY 權重 -->
<input type="range" id="alphaSlider" min="0" max="100" value="50">
```

### 2. 動態計算 HCI

```javascript
// 調整權重後，自動重新計算
const hciResult = hciCalculator.calculateHCI(zipData, {
  w1: 0.6,    // 成長權重 60%
  w2: 0.4,    // 安全權重 40%
  alpha: 0.5  // YoY 權重 50%
});
```

### 3. 顯示結果

- HCI 分數會根據權重自動更新
- 成長指標和安全指標會分別顯示
- 可以比較不同權重設定下的結果

---

## 📊 HCI 計算邏輯

### 公式

```
HCI_z = w1 * G_z + w2 * (1 - C_z)
```

其中：
- `G_z = α * YoY_z + (1 - α) * MoM_z`（成長指標）
- `C_z`（犯罪指標，標準化的犯罪率或犯罪數）

### 權重影響

- **w1 越大**: 越重視成長，高成長區域的 HCI 越高
- **w2 越大**: 越重視安全，低犯罪區域的 HCI 越高
- **α 越大**: 越重視長期趨勢（YoY），忽略短期波動（MoM）

---

## 🎨 前端 UI 建議

### 1. 權重調整滑桿

- 使用雙向綁定，確保 w1 + w2 = 100%
- 顯示當前權重百分比
- 提供預設權重選項（投資者、居住者、平衡型）

### 2. 實時更新

- 調整權重時，立即更新 HCI 分數
- 更新地圖顏色（如果有的話）
- 更新排序列表

### 3. 比較功能

- 允許保存多個權重設定
- 比較不同權重下的結果
- 顯示權重變化對 HCI 的影響

---

## 📝 實作範例

### Angular Component

```typescript
export class HCICalculatorComponent {
  w1 = 0.6;
  w2 = 0.4;
  alpha = 0.5;
  
  updateWeights() {
    // 確保 w1 + w2 = 1
    const total = this.w1 + this.w2;
    if (total !== 1) {
      this.w2 = 1 - this.w1;
    }
    
    // 重新計算所有 ZIP Code 的 HCI
    this.recalculateAllHCI();
  }
  
  recalculateAllHCI() {
    const params = {
      w1: this.w1,
      w2: this.w2,
      alpha: this.alpha
    };
    
    // 計算所有 ZIP Code 的 HCI
    this.allHCIResults = this.hciCalculator.calculateAllHCI(
      this.data.data,
      params
    );
    
    // 排序並更新顯示
    this.updateDisplay();
  }
}
```

---

## 🔍 驗證權重

### 權重驗證規則

1. **w1 + w2 = 1**: 必須滿足
2. **w1, w2 >= 0**: 不能為負數
3. **α 在 [0, 1]**: YoY 權重範圍

### 前端驗證

```typescript
validateParams(params: HCIParams): { valid: boolean; error?: string } {
  if (params.w1 < 0 || params.w1 > 1) {
    return { valid: false, error: 'w1 必須在 0-1 之間' };
  }
  if (params.w2 < 0 || params.w2 > 1) {
    return { valid: false, error: 'w2 必須在 0-1 之間' };
  }
  if (Math.abs(params.w1 + params.w2 - 1) > 0.01) {
    return { valid: false, error: 'w1 + w2 必須等於 1' };
  }
  return { valid: true };
}
```

---

## 💡 建議

### 1. 預設權重選項

提供預設權重選項，方便用戶快速選擇：
- **投資者**: w1=70%, w2=30%, α=60%
- **居住者**: w1=30%, w2=70%, α=40%
- **平衡型**: w1=50%, w2=50%, α=50%

### 2. 權重說明

在 UI 中加入權重說明：
- 解釋每個權重的意義
- 提供使用建議
- 顯示權重變化對結果的影響

### 3. 比較功能

允許用戶比較不同權重設定：
- 保存多個權重設定
- 並排比較結果
- 顯示差異分析

---

## 📚 相關文件

- `docs/HCI_IMPLEMENTATION_GUIDE.md`: HCI 實作指南
- `docs/COMPLETE_IMPLEMENTATION_SUMMARY.md`: 完整實作總結
- `frontend/hci-calculator.service.ts`: 前端 HCI 計算服務

---

需要協助調整 UI 或加入更多功能嗎？

