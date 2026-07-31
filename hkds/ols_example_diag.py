# %%
# OLS Diagnostics Playbook (statsmodels-centric)
# This file mirrors hkds/ols_diag.md with executable cells.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.graphics.api as smg
from statsmodels.stats.diagnostic import normal_ad, het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

# %%
# 1. Baseline setup (reproducible)
np.random.seed(42)

n = 300
x1 = np.random.normal(size=n)
x2 = 0.95 * x1 + np.random.normal(scale=0.1, size=n)  # collinear
x3 = np.random.normal(size=n)

y = 2 * x1 - 1.5 * x2 + 0.5 * x3 + np.random.normal(scale=1.0, size=n)

df = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "y": y})

# %%
# 2. Fit the OLS model
X = sm.add_constant(df[["x1", "x2", "x3"]])
y = df["y"]

ols = sm.OLS(y, X).fit()
ols_summary = ols.summary()
ols_summary

# %%
# 2.1 Fitted vs residuals (quick visual check)
fitted = ols.fittedvalues
resid = ols.resid

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(fitted, resid, alpha=0.7)
ax.axhline(0, color="black", linewidth=1)
ax.set_xlabel("Fitted values")
ax.set_ylabel("Residuals")
ax.set_title("Residuals vs Fitted")
plt.show()

#%% sklearn

import scipy.stats as st
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.linear_model import LinearRegression

# %%
# 2.0b Sklearn regression + coefficient confidence intervals (OLS-equivalent)
X_sk = df[["x1", "x2", "x3"]].values
y_sk = y.values

lr = LinearRegression(fit_intercept=True)
lr.fit(X_sk, y_sk)

coef_names = ["const", "x1", "x2", "x3"]
beta_hat = np.r_[lr.intercept_, lr.coef_]

X_design = np.column_stack([np.ones(X_sk.shape[0]), X_sk])
resid_sk = y_sk - X_design @ beta_hat

n_obs = X_design.shape[0]
n_params = X_design.shape[1]
dof = n_obs - n_params
sigma2 = (resid_sk @ resid_sk) / dof

xtx_inv = np.linalg.inv(X_design.T @ X_design)
se = np.sqrt(np.diag(sigma2 * xtx_inv))

alpha = 0.05
tcrit = st.t.ppf(1 - alpha / 2, dof)
ci_low = beta_hat - tcrit * se
ci_high = beta_hat + tcrit * se

sklearn_ci = pd.DataFrame(
    {"coef": beta_hat, "se": se, "ci_low": ci_low, "ci_high": ci_high},
    index=coef_names,
)
sklearn_ci

# %%

# %%
# 2.2 Normal Q-Q plot (normality)
fig = smg.qqplot(resid, line="45", fit=True)
plt.title("Q-Q Plot (Residuals)")
plt.show()

# %%
# 2.3 Scale-location plot (sqrt|resid| vs fitted)
fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(fitted, np.sqrt(np.abs(resid)), alpha=0.7)
ax.set_xlabel("Fitted values")
ax.set_ylabel("Sqrt(|Residuals|)")
ax.set_title("Scale-Location")
plt.show()
# %%
# 3. Coefficient uncertainty (confidence intervals)
conf_int = ols.conf_int(alpha=0.05)
conf_int

# %%
# 4. Multicollinearity diagnostics
# 4.1 VIF
X_no_const = df[["x1", "x2", "x3"]]

vif = pd.DataFrame({
    "variable": X_no_const.columns,
    "VIF": [
        variance_inflation_factor(X_no_const.values, i)
        for i in range(X_no_const.shape[1])
    ],
})
vif

# %%
# 4.2 Condition number (global collinearity)
cond_number = np.linalg.cond(X_no_const.values)
cond_number

# %%
# 5. Residual diagnostics
# 5.1 Normality (Anderson-Darling) p-values
normal_ad_result = normal_ad(ols.resid)
normal_ad_result

# %%
# 5.2 Heteroskedasticity (Breusch-Pagan)
bp_stat = het_breuschpagan(ols.resid, ols.model.exog)
bp_stat

# %%
# If heteroskedasticity detected, use robust SEs
ols_robust = ols.get_robustcov_results(cov_type="HC3")
ols_robust_summary = ols_robust.summary()
ols_robust_summary

# %%
# 6. Outliers and influence
influence = ols.get_influence()
inf_df = influence.summary_frame()
inf_df.head()

# %%
# 6.1 Influence plot (leverage vs residuals with Cook's distance)
fig, ax = plt.subplots(figsize=(6, 4))
smg.influence_plot(ols, ax=ax, criterion="cooks")
plt.title("Influence Plot")
plt.show()

# %%
# 6.1b Leverage vs residuals squared
fig = smg.plot_leverage_resid2(ols)
plt.title("Leverage vs Residuals Squared")
plt.show()

# %%
# 6.2 Flag influential observations
n = X.shape[0]
cooks_cutoff = 4 / n

influential_points = inf_df["cooks_d"] > cooks_cutoff
influential_rows = df[influential_points]
influential_rows.head()

# %%
# 7. Stability check (refit with reduced model)
X_reduced = sm.add_constant(df[["x1", "x3"]])
ols_reduced = sm.OLS(y, X_reduced).fit()
ols_reduced_summary = ols_reduced.summary()
ols_reduced_summary

# %%
# 8. Nested model comparison (formal statistics)
X1 = sm.add_constant(df[["x1", "x3"]])
X2 = sm.add_constant(df[["x1", "x2", "x3"]])

m1 = sm.OLS(y, X1).fit()
m2 = sm.OLS(y, X2).fit()

# %%
# 8.1 F-test (preferred)
f_test = m2.compare_f_test(m1)
f_test

# %%
# 8.2 Information criteria
m1_aic_bic = (m1.aic, m1.bic)
m2_aic_bic = (m2.aic, m2.bic)
m1_aic_bic, m2_aic_bic

# %%
# 9. Minimal checklist (quick sanity)
checklist = {
    "vif_computed": True,
    "condition_number_checked": True,
    "residual_diagnostics_run": True,
    "influence_analyzed": True,
    "nested_models_tested": True,
    "goal_clarified": "inference vs prediction",
}
checklist
