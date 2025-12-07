# HCI (Housing-Crime Index) Calculation Formulas

This document details the mathematical formulas used to calculate the Housing-Crime Index (HCI) and its components.

## 1. Overview

The HCI is a composite index that balances **Housing Market Growth** and **Community Safety**. It is calculated for each Zip Code ($z$).

$$
HCI_z = w_1 \times G_z + w_2 \times (1 - C_z)
$$

Where:
- $G_z$: Growth Indicator (0 to 1)
- $C_z$: Crime Indicator (0 to 1, where 1 is high crime)
- $1 - C_z$: Safety Indicator (0 to 1, where 1 is safest)
- $w_1$: Weight for Growth (default 0.5)
- $w_2$: Weight for Safety (default 0.5)

---

## 2. Normalization (Min-Max Scaling)

All raw values are normalized to a [0, 1] range using Min-Max Normalization:

$$
Normalized(x) = \frac{x - \min(X)}{\max(X) - \min(X)}
$$

Where:
- $x$: The value for a specific Zip Code.
- $\min(X)$ and $\max(X)$: The minimum and maximum values across **all** Zip Codes in the dataset.

---

## 3. Growth Indicator ($G_z$)

Reflects the investment potential based on price appreciation. It combines Month-over-Month (MoM) and Year-over-Year (YoY) growth rates.

$$
G_z = \alpha \times Normalized(YoY_z) + (1 - \alpha) \times Normalized(MoM_z)
$$

Where:
- $YoY_z$: Year-over-Year price change for Zip Code $z$.
- $MoM_z$: Month-over-Month price change for Zip Code $z$.
- $\alpha$: Weight for YoY growth (default 0.5).

---

## 4. Crime Indicator ($C_z$) - Clipped Score Method

To better differentiate between safe and unsafe areas and handle outliers, we use a **Clipped Score** method with a dynamic ceiling.

### Step 4.1: Calculate Crime Rate
$$
CrimeRate_z = \left( \frac{TotalCrimes_z}{Population_z} \right) \times 1000
$$

### Step 4.2: Determine Ceiling ($Ceiling_{90}$)
We calculate the **90th percentile** of crime rates across all Zip Codes. This serves as the "danger threshold".
- Current Ceiling ($\approx 77.9$): Any crime rate above this value is considered maximum danger.

### Step 4.3: Calculate Score
$$
C_z = \begin{cases} 
1.0 & \text{if } CrimeRate_z \ge Ceiling_{90} \\
\frac{CrimeRate_z}{Ceiling_{90}} & \text{if } CrimeRate_z < Ceiling_{90}
\end{cases}
$$

**Why this method?**
- **Differentiation**: It stretches the scores for typical residential areas (0-80 range), making it easier to distinguish between "safe" and "very safe".
- **Outlier Handling**: Extreme outliers (e.g., commercial districts with very high crime rates) are capped at 1.0, preventing them from skewing the entire distribution.

---

## 5. Safety Indicator ($S_z$)

The inverse of the Crime Indicator.

$$
S_z = 1 - C_z
$$

- If $CrimeRate_z \ge Ceiling_{90}$, then $S_z = 0$ (Minimum Safety).
- Otherwise, $S_z$ scales linearly from 1 (Safest) to 0 (Threshold).

### Missing Population Data Fallback
If population data is unavailable for a Zip Code, we cannot calculate the Crime Rate per 1,000 residents. In this case:
1.  We use the **Total Crime Count** directly.
2.  We normalize it using the standard Min-Max Normalization based on the range of crime counts across all areas.
3.  **Note**: This is less accurate for comparing density, but provides a reasonable fallback.

---

## 6. Final HCI Score

The final score is a weighted sum of Growth and Safety.

$$
HCI_z = w_1 \times G_z + w_2 \times S_z
$$

### Display Score (0-100)
For easier readability, the final score is multiplied by 100:

$$
HCI_{100} = HCI_z \times 100
$$

---

## Example Calculation

Given:
- $w_1 = 0.5, w_2 = 0.5$
- Growth Indicator ($G_z$) = 0.5202
- Crime Indicator ($C_z$) = 0.2258

1. **Calculate Safety Indicator**:
   $$S_z = 1 - 0.2258 = 0.7742$$

2. **Calculate HCI**:
   $$HCI_z = (0.5 \times 0.5202) + (0.5 \times 0.7742)$$
   $$HCI_z = 0.2601 + 0.3871 = 0.6472$$

3. **Convert to 100-scale**:
   $$HCI_{100} = 64.72$$
