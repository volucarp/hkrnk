# OLS Diagnostics Playbook (statsmodels-centric)

## Scope and Goal

This document summarizes **practical OLS diagnostics** for linear regression using
`statsmodels`, with emphasis on:

- coefficient reliability
- uncertainty quantification
- collinearity detection
- outlier and influence diagnostics
- statistical comparison of nested models

The goal is **debugging and inference**, not pure prediction.

---

## 1. Assumptions of OLS (what diagnostics are testing)

OLS inference relies on:

1. Linearity in parameters
2. Full column rank of the design matrix (no perfect multicollinearity)
3. Exogeneity: E[ε | X] = 0
4. Homoskedasticity (for classical SEs)
5. No extreme leverage / influence
6. Normality of errors (mainly for small-sample inference)

Diagnostics are checks for **violations that break inference**.

---

## 2. Baseline Setup (Reproducible)

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm

np.random.seed(42)

n = 300
x1 = np.random.normal(size=n)
x2 = 0.95 * x1 + np.random.normal(scale=0.1, size=n)  # collinear
x3 = np.random.normal(size=n)

y = 2 * x1 - 1.5 * x2 + 0.5 * x3 + np.random.normal(scale=1.0, size=n)

df = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "y": y})
```

---

## 3. Fit the OLS Model

```python
X = sm.add_constant(df[["x1", "x2", "x3"]])
y = df["y"]

ols = sm.OLS(y, X).fit()
print(ols.summary())
```

**First-pass red flags in summary:**

- large standard errors
- insignificant coefficients with high R²
- unexpected signs
- large condition number

---

## 4. Coefficient Uncertainty

### 4.1 Confidence Intervals (primary inference object)

```python
ols.conf_int(alpha=0.05)
```

**Interpretation:**

A coefficient is statistically unstable if the interval is wide or straddles zero.

---

## 5. Multicollinearity Diagnostics

### 5.1 Variance Inflation Factor (VIF)

**Definition**

VIF₍ⱼ₎ = 1 / (1 − R²ⱼ)

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

X_no_const = df[["x1", "x2", "x3"]]

vif = pd.DataFrame({
    "variable": X_no_const.columns,
    "VIF": [
        variance_inflation_factor(X_no_const.values, i)
        for i in range(X_no_const.shape[1])
    ],
})
print(vif)
```

**Interpretation**

| VIF | Meaning |
| --- | --- |
| ≈ 1 | no collinearity |
| 1–5 | mild |
| 5–10 | problematic |
| > 10 | severe (inference unreliable) |

### 5.2 Condition Number (global collinearity)

```python
np.linalg.cond(X_no_const.values)
```

**Rule of thumb:**

- 30 → problematic
- 100 → severe

---

## 6. Residual Diagnostics

### 6.1 Normality (for inference, not prediction)

```python
from statsmodels.stats.diagnostic import normal_ad

normal_ad(ols.resid)
```

Large p-value → no strong evidence against normality.

### 6.2 Heteroskedasticity (Breusch–Pagan)

```python
from statsmodels.stats.diagnostic import het_breuschpagan

bp_stat = het_breuschpagan(ols.resid, ols.model.exog)
bp_stat
```

If heteroskedasticity detected → use robust SEs:

```python
ols_robust = ols.get_robustcov_results(cov_type="HC3")
print(ols_robust.summary())
```

---

## 7. Outliers and Influence

### 7.1 Influence Measures

```python
influence = ols.get_influence()
inf_df = influence.summary_frame()
inf_df.head()
```

**Key columns:**

- student_resid → outliers
- hat_diag → leverage
- cooks_d → influence

### 7.2 Flag Influential Observations

```python
n = X.shape[0]
cooks_cutoff = 4 / n

influential_points = inf_df["cooks_d"] > cooks_cutoff
df[influential_points]
```

**Interpretation**

- high residual ≠ influential
- influence = leverage × residual

---

## 8. Stability Check (Critical)

Refit model after removing suspect points or variables.

```python
X_reduced = sm.add_constant(df[["x1", "x3"]])
ols_reduced = sm.OLS(y, X_reduced).fit()
print(ols_reduced.summary())
```

If coefficients or signs change materially → collinearity or influence problem.

---

## 9. Nested Model Comparison (Formal Statistics)

**Example:**

- Model 1: y ~ x1 + x3
- Model 2: y ~ x1 + x2 + x3

```python
X1 = sm.add_constant(df[["x1", "x3"]])
X2 = sm.add_constant(df[["x1", "x2", "x3"]])

m1 = sm.OLS(y, X1).fit()
m2 = sm.OLS(y, X2).fit()
```

### 9.1 F-test (preferred)

```python
m2.compare_f_test(m1)
```

**Returns:**

- F-statistic
- p-value
- df difference

**Interpretation:**

Does the extra regressor significantly improve fit?

### 9.2 Information Criteria (model selection)

```python
m1.aic, m2.aic
m1.bic, m2.bic
```

Lower is better (penalizes complexity).

---

## 10. Decision Framework

| Issue Detected | Action |
| --- | --- |
| VIF > 10 | Do not interpret individual coefficients |
| High condition number | Investigate feature dependence |
| Heteroskedasticity | Use robust SEs |
| Influential points | Inspect data integrity |
| Nested model insignificant | Prefer simpler model |

---

## 11. Mental Model

OLS asks:

> “What is the marginal effect of x_j holding all other regressors fixed?”

If that condition is ill-defined (collinearity), coefficients lose meaning even if prediction looks good.

---

## 12. Minimal Checklist (before trusting results)

- VIF computed
- Condition number checked
- Residual diagnostics run
- Influence analyzed
- Nested models tested
- Goal clarified (inference vs prediction)

---

End of Playbook

---

If you want, next we can:

- add **VIF-aware feature engineering patterns**
- contrast **OLS vs Ridge/LASSO diagnostics**
- show **exact sklearn ↔ statsmodels equivalence**
- extend this to **time-series regressions**

Just tell me the next axis.
