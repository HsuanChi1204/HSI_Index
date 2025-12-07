# 論文內容調整建議

## ✅ 已修復的問題

### 1. JSON NaN 問題
- **問題**: DISTRICT 欄位有 NaN 值，導致前端 JSON 解析失敗
- **解決**: 已修改 `combine_data_to_json.py`，將所有 NaN 值轉換為 `null`
- **結果**: JSON 可以正常解析，前端可以正常載入

---

## 📝 論文內容檢查結果

### ✅ 論文優點

1. **結構清晰**: 論文結構完整，包含 Introduction, Related Work, Proposed Approaches, System Design 等
2. **技術細節完整**: 詳細說明了資料處理、標準化、Index 計算方法
3. **倫理考量**: 包含了完整的倫理考量章節
4. **系統架構**: 清楚描述了四層架構（Frontend, GCP Backend, AWS AI Agent, Supabase）

### ⚠️ 需要調整的部分

#### 1. 標準化範圍不一致

**論文描述** (Line 177-187):
- 標準化到 [0, 1] 範圍
- 使用 min-max normalization

**實際實作**:
- 標準化到 [0, 100] 範圍（更容易視覺化）

**建議**:
在論文中加入註釋說明：
```latex
While the normalization formula produces values in the [0, 1] range, 
we scale the results to [0, 100] for improved visualization and 
user interpretability in the web interface.
```

#### 2. Index 計算公式不完全一致

**論文公式** (Equation 2, Line 192-196):
```
HCI_z = w1 * G_z + w2 * (1 - C_z)
```
其中：
- `G_z` = 標準化的成長指標（結合 MoM 和 YoY）
- `C_z` = 標準化的犯罪測量（每 1000 居民的犯罪率）

**實際實作**:
- 我們計算了多個指數（安全指數、可負擔性指數、生活品質指數等）
- 生活品質指數 = 安全指數 × 60% + 可負擔性指數 × 40%
- 但沒有完全按照論文的公式（結合 MoM 和 YoY）

**建議選項**:

**選項 A**: 調整實作以符合論文
- 修改 `calculate_index.py`，使其完全按照論文公式計算
- 結合 MoM 和 YoY 來計算成長指標
- 計算犯罪率（每 1000 居民）而不是犯罪總數

**選項 B**: 更新論文以反映實作
- 說明我們實作了更豐富的指數系統
- 說明我們使用當前房價和犯罪總數（因為缺少人口資料）
- 說明未來會加入人口資料來計算犯罪率

**推薦**: 選項 B（更實際），因為：
1. 我們目前沒有人口資料來計算犯罪率
2. 我們已經實作了可用的指數系統
3. 可以在未來工作中說明如何加入人口資料

#### 3. 成長指標計算

**論文公式** (Equation 3, Line 269):
```
G_z = α * YoY_z + (1 - α) * MoM_z
```

**實際實作**:
- 我們使用當前房價，沒有結合 MoM 和 YoY

**建議**:
在論文中說明當前實作使用當前房價作為成長指標，未來會結合 MoM 和 YoY：
```latex
In the current implementation, we use the current housing price 
as the growth indicator. Future work will combine MoM and YoY 
rates as specified in Equation 3, allowing users to adjust 
the weight α to emphasize short-term or long-term trends.
```

#### 4. 技術細節說明

**建議加入**:
1. **JSON 資料結構說明**: 說明 JSON 檔案的結構和欄位
2. **NaN 值處理**: 說明如何處理缺失值（轉換為 null）
3. **GCP Cloud Storage**: 說明使用 GCP Cloud Storage 儲存 JSON 檔案供前端讀取
4. **前端讀取方式**: 說明前端如何從 GCP Storage 讀取 JSON 資料

---

## 🔧 具體修改建議

### 修改 1: 在 Normalization  section 加入註釋

在 Line 177-187 之後加入：

```latex
For visualization purposes, we scale the normalized values to 
the [0, 100] range, where 0 represents the least favorable 
condition and 100 represents the most favorable condition. 
This scaling improves user interpretability while maintaining 
the relative relationships between ZIP codes.
```

### 修改 2: 在 Index Construction section 加入實作說明

在 Line 189-202 之後加入：

```latex
In the current implementation, we compute multiple indices 
to provide comprehensive insights:
\begin{itemize}
    \item \textbf{Safety Index:} Measures safety based on 
          normalized crime count (0-100, higher is safer)
    \item \textbf{Affordability Index:} Measures housing 
          affordability based on normalized price (0-100, 
          higher is more affordable)
    \item \textbf{Quality of Life Index:} Combines safety 
          and affordability with user-defined weights
    \item \textbf{Investment Index:} Evaluates investment 
          potential based on price appreciation and safety
\end{itemize}

Future work will integrate population data to compute 
crime rates per 1,000 residents and combine MoM and YoY 
growth rates as specified in Equations 3-4.
```

### 修改 3: 在 System Design section 加入 JSON 說明

在 Line 332 之後加入：

```latex
Processed data are stored as JSON files in Google Cloud Storage, 
enabling efficient frontend retrieval. The JSON structure includes 
metadata (total ZIP codes, generation timestamp, index ranges) 
and data organized by ZIP code, containing crime statistics, 
housing data, and computed indices. Missing values are handled 
by converting NaN to null, ensuring valid JSON parsing.
```

### 修改 4: 更新 Progress Report

在 Line 543-576 的 Progress Report 中加入：

- ✅ 完成 Index 計算實作
- ✅ 修復 JSON NaN 問題
- ✅ 建立前端測試頁面
- ⏳ 待完成：整合人口資料計算犯罪率
- ⏳ 待完成：結合 MoM 和 YoY 計算成長指標

---

## 📋 檢查清單

### 內容一致性
- [ ] 標準化範圍說明（[0,1] vs [0,100]）
- [ ] Index 計算公式說明
- [ ] 成長指標計算方式
- [ ] 犯罪率計算方式（目前使用犯罪總數）

### 技術細節
- [ ] JSON 資料結構說明
- [ ] NaN 值處理說明
- [ ] GCP Cloud Storage 使用說明
- [ ] 前端讀取方式說明

### 未來工作
- [ ] 說明如何加入人口資料
- [ ] 說明如何結合 MoM 和 YoY
- [ ] 說明 HouseTS 整合計劃

---

## 💡 其他建議

1. **加入實作範例**: 在論文中加入實際計算結果的範例
2. **視覺化說明**: 說明前端如何視覺化 Index 分數
3. **驗證結果**: 加入驗證結果和案例分析
4. **效能優化**: 說明如何優化查詢效能

---

需要我幫您調整論文內容嗎？或者調整實作以完全符合論文公式？

