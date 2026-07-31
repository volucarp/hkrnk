# Daily Stock Return Generation

## 1. Purpose

Generate a matrix of correlated daily arithmetic stock returns for:

$$
T=251
$$

trading days and \(N\) securities. The user supplies a population average pairwise correlation, for example:

$$
\rho=0.30.
$$

The baseline design uses a constant-correlation model, so every distinct pair of securities has population correlation \(\rho\). Consequently, the population average pairwise correlation is also exactly \(\rho\).

The output is:

$$
R\in\mathbb{R}^{T\times N},
$$

where row \(t\) contains the returns on trading day \(t\), and column \(i\) contains the return history of security \(i\).

## 2. Inputs and notation

Define all inputs before generating any returns:

| Symbol | Code name | Dimension | Definition |
| --- | --- | ---: | --- |
| \(T\) | `n_days` | scalar | Number of simulated days; default \(251\) |
| \(N\) | `n_assets` | scalar | Number of securities |
| \(D\) | `trading_days` | scalar | Trading days per year; default \(251\) |
| \(\rho\) | `average_correlation` | scalar | Target population pairwise correlation |
| \(\mu^{(a)}\) | `annual_return` | \(N\times1\) | Annual expected arithmetic returns |
| \(s^{(a)}\) | `annual_volatility` | \(N\times1\) | Annualized volatilities |
| \(\mathbf{1}_T\) | — | \(T\times1\) | Vector of ones |
| \(\mathbf{1}_N\) | — | \(N\times1\) | Vector of ones |
| \(I_N\) | — | \(N\times N\) | Identity matrix |

Scalar return or volatility inputs are broadcast to all securities. The restrictions are:

$$
s_i^{(a)}>0
\quad\text{for every }i,
$$

and:

$$
-\frac{1}{N-1}\leq\rho\leq1.
$$

The efficient one-factor implementation described below additionally requires \(\rho\geq0\).

## 3. Step 1 — initialize the random-number generator

Create one reproducible NumPy random generator:

```python
rng = np.random.default_rng(seed)
```

All random variables in the construction must come from this generator. A fixed seed reproduces the same return matrix.

## 4. Step 2 — generate independent standard-normal shocks

Generate:

$$
E=
\begin{bmatrix}
\varepsilon_1^\top\\
\varepsilon_2^\top\\
\vdots\\
\varepsilon_T^\top
\end{bmatrix}
\in\mathbb{R}^{T\times N},
$$

with independent entries:

$$
E_{t,i}\overset{\text{iid}}{\sim}\mathcal{N}(0,1).
$$

Equivalently, each row satisfies:

$$
\varepsilon_t\sim\mathcal{N}(0,I_N),
\qquad
\mathbb{E}[\varepsilon_t]=0,
\qquad
\operatorname{Cov}(\varepsilon_t)=I_N.
$$

At this stage, the columns are independent. The shocks form a spherical cloud in \(\mathbb{R}^N\): every direction has unit variance, and there is no preferred direction or cross-security correlation.

In NumPy:

```python
E = rng.standard_normal((n_days, n_assets))
```

## 5. Step 3 — convert annual parameters to daily parameters

Define the daily expected-return vector:

$$
\mu=\frac{\mu^{(a)}}{D}
\in\mathbb{R}^N,
$$

and the daily volatility vector:

$$
s=\frac{s^{(a)}}{\sqrt{D}}
\in\mathbb{R}^N.
$$

Define the diagonal daily-volatility matrix:

$$
S=\operatorname{Diag}(s)
\in\mathbb{R}^{N\times N}.
$$

This specification models arithmetic returns. For a log-return process, the annual-to-daily drift conversion must include the chosen lognormal convention.

## 6. Step 4 — design the target correlation matrix

For the baseline constant-correlation model, define:

$$
C=(1-\rho)I_N+\rho\mathbf{1}_N\mathbf{1}_N^\top
\in\mathbb{R}^{N\times N}.
$$

Its entries are:

$$
C_{ij}=
\begin{cases}
1, & i=j,\\
\rho, & i\neq j.
\end{cases}
$$

Therefore, the mean off-diagonal correlation is:

$$
\bar{\rho}(C)
=
\frac{1}{N(N-1)}
\sum_{i\neq j}C_{ij}
=\rho.
$$

The eigenvalues of \(C\) explain its geometry:

$$
\lambda_{\mathrm{market}}=1+(N-1)\rho
$$

in the direction \(\mathbf{1}_N/\sqrt{N}\), and:

$$
\lambda_{\mathrm{idiosyncratic}}=1-\rho
$$

in each of the \(N-1\) directions orthogonal to \(\mathbf{1}_N\). These eigenvalues produce the admissible bound:

$$
-\frac{1}{N-1}\leq\rho\leq1.
$$

## 7. Step 5 — design the target covariance matrix

Combine the target correlations and stock-specific daily volatilities:

$$
\Sigma=SCS
\in\mathbb{R}^{N\times N}.
$$

Its entries are:

$$
\Sigma_{ij}=s_i s_j C_{ij}.
$$

In particular:

$$
\Sigma_{ii}=s_i^2,
\qquad
\Sigma_{ij}=\rho s_i s_j
\quad\text{for }i\neq j.
$$

Thus, \(C\) controls standardized co-movement, while \(S\) controls the scale of each security's returns.

## 8. Step 6 — compute a covariance square root

Choose a matrix:

$$
A\in\mathbb{R}^{N\times N}
$$

such that:

$$
AA^\top=\Sigma.
$$

### Eigenvalue construction

Because \(\Sigma\) is symmetric and positive semidefinite, it has an eigendecomposition:

$$
\Sigma=Q\Lambda Q^\top,
$$

where:

$$
Q^\top Q=QQ^\top=I_N
$$

and:

$$
\Lambda=\operatorname{Diag}(\lambda_1,\ldots,\lambda_N),
\qquad
\lambda_i\geq0.
$$

A valid square root is:

$$
A=Q\Lambda^{1/2},
$$

because:

$$
AA^\top
=
Q\Lambda^{1/2}\Lambda^{1/2}Q^\top
=
Q\Lambda Q^\top
=\Sigma.
$$

### Geometric interpretation

For a column shock \(\varepsilon_t\), the transformation:

$$
x_t=A\varepsilon_t=Q\Lambda^{1/2}\varepsilon_t
$$

has two geometric effects:

1. \(\Lambda^{1/2}\) stretches or compresses the spherical shock along orthogonal coordinates.
2. \(Q\) rotates those axes into the principal directions of the target covariance matrix.

The spherical cloud becomes an ellipsoid. Its principal-axis directions are the columns of \(Q\), and its principal-axis standard deviations are \(\sqrt{\lambda_i}\).

A Cholesky factor:

$$
\Sigma=LL^\top
$$

is another valid choice, with \(A=L\). Cholesky and the spectral square root produce the same covariance distribution, even though their intermediate geometric transformations differ.

## 9. Step 7 — transform independent shocks into correlated returns

For one day, define:

$$
r_t=\mu+A\varepsilon_t
\in\mathbb{R}^N.
$$

For all \(T\) days simultaneously:

$$
\boxed{
R=\mathbf{1}_T\mu^\top+EA^\top
}
$$

because row \(t\) of \(EA^\top\) is \((A\varepsilon_t)^\top\).

The construction has the required population moments:

$$
\mathbb{E}[r_t]
=
\mu+A\mathbb{E}[\varepsilon_t]
=\mu,
$$

and:

$$
\begin{aligned}
\operatorname{Cov}(r_t)
&=
A\operatorname{Cov}(\varepsilon_t)A^\top\\
&=
AI_NA^\top\\
&=
AA^\top\\
&=
\Sigma.
\end{aligned}
$$

This is the exact step that turns independent random numbers into correlated returns. The random numbers provide the unpredictable shocks; \(A\) imposes the designed covariance geometry; and \(\mu\) shifts the center of the distribution.

## 10. Equivalent one-factor construction for \(\rho\geq0\)

The constant-correlation model has a more efficient representation that avoids building or factorizing an \(N\times N\) covariance matrix.

Generate a common market-shock vector:

$$
f\in\mathbb{R}^T,
\qquad
f_t\overset{\text{iid}}{\sim}\mathcal{N}(0,1),
$$

and an idiosyncratic-shock matrix:

$$
Z\in\mathbb{R}^{T\times N},
\qquad
Z_{t,i}\overset{\text{iid}}{\sim}\mathcal{N}(0,1),
$$

with \(f\) independent of every entry in \(Z\).

Construct standardized correlated shocks:

$$
X
=
\sqrt{\rho}\,f\mathbf{1}_N^\top
+
\sqrt{1-\rho}\,Z
\in\mathbb{R}^{T\times N}.
$$

Then generate returns:

$$
\boxed{
R=\mathbf{1}_T\mu^\top+XS.
}
$$

For one day:

$$
x_t
=
\sqrt{\rho}\,f_t\mathbf{1}_N
+
\sqrt{1-\rho}\,z_t.
$$

Its covariance is:

$$
\begin{aligned}
\operatorname{Cov}(x_t)
&=
\rho\mathbf{1}_N\mathbf{1}_N^\top
+
(1-\rho)I_N\\
&=C.
\end{aligned}
$$

Therefore:

$$
\operatorname{Cov}(r_t)
=
S\operatorname{Cov}(x_t)S
=SCS
=\Sigma.
$$

For two distinct securities:

$$
\operatorname{Cov}(r_{t,i},r_{t,j})
=
\rho s_i s_j,
$$

and:

$$
\operatorname{Corr}(r_{t,i},r_{t,j})
=
\frac{\rho s_i s_j}{s_i s_j}
=\rho.
$$

When \(\rho=0.30\), 30% of each standardized return's variance comes from the common shock and 70% comes from its idiosyncratic shock.

## 11. Returns implied by an eight-factor risk model

The constant-correlation model is equivalent to a one-factor model. A more realistic simulation can instead generate returns from:

$$
K=8
$$

systematic risk factors plus security-specific shocks.

Possible factor labels are market, size, value, momentum, quality, low volatility, liquidity, and growth. The labels do not affect the mathematics; the model only requires eight factor-return series and an exposure to each factor for every security.

### 11.1 Define the factor-model variables

Define:

| Symbol | Dimension | Definition |
| --- | ---: | --- |
| \(K\) | scalar | Number of factors; \(K=8\) |
| \(U\) | \(T\times K\) | Independent standard-normal factor source shocks |
| \(V_f\) | \(K\times K\) | Daily factor covariance matrix |
| \(A_f\) | \(K\times K\) | Factor covariance square root |
| \(F\) | \(T\times K\) | Simulated factor returns |
| \(B\) | \(N\times K\) | Security factor-exposure matrix |
| \(Z\) | \(T\times N\) | Independent standard-normal specific source shocks |
| \(d_\epsilon\) | \(N\times1\) | Security-specific daily variances |
| \(D_\epsilon\) | \(N\times N\) | Diagonal matrix of specific volatilities |
| \(\Delta\) | \(N\times N\) | Diagonal specific covariance matrix |

The exposure vector for security \(i\) is row \(i\) of \(B\):

$$
b_i^\top
=
\begin{bmatrix}
b_{i,1} & \cdots & b_{i,8}
\end{bmatrix}.
$$

### 11.2 Generate the factor source shocks

Generate independent standard-normal variables:

$$
U_{t,k}\overset{\text{iid}}{\sim}\mathcal{N}(0,1),
$$

so that:

$$
U\in\mathbb{R}^{T\times K}.
$$

For each day, the column vector \(u_t\in\mathbb{R}^K\) satisfies:

$$
\mathbb{E}[u_t]=0,
\qquad
\operatorname{Cov}(u_t)=I_K.
$$

### 11.3 Design the factor covariance matrix

Choose a symmetric positive-semidefinite daily factor covariance matrix:

$$
V_f\in\mathbb{R}^{K\times K}.
$$

Its diagonal contains factor variances, and its off-diagonal entries contain factor covariances. It may be diagonal for independent factors or dense for correlated factors.

Choose a factor covariance square root:

$$
A_fA_f^\top=V_f.
$$

For example, with:

$$
V_f=Q_f\Lambda_fQ_f^\top,
$$

use:

$$
A_f=Q_f\Lambda_f^{1/2}.
$$

Generate the factor-return matrix:

$$
\boxed{
F=UA_f^\top
}
$$

so row \(t\) is \(f_t^\top\), where:

$$
f_t=A_fu_t.
$$

Consequently:

$$
\mathbb{E}[f_t]=0,
\qquad
\operatorname{Cov}(f_t)=V_f.
$$

Nonzero expected factor returns may be introduced with:

$$
F=\mathbf{1}_T\mu_f^\top+UA_f^\top,
$$

where \(\mu_f\in\mathbb{R}^K\). If this form is used, the expected stock-return vector becomes \(\mu+B\mu_f\). The baseline below uses zero-mean factor shocks and keeps expected stock returns in \(\mu\).

### 11.4 Design the security exposure matrix

Define:

$$
B=
\begin{bmatrix}
b_1^\top\\
\vdots\\
b_N^\top
\end{bmatrix}
\in\mathbb{R}^{N\times K}.
$$

The systematic return of security \(i\) on day \(t\) is:

$$
b_i^\top f_t.
$$

The first column of \(B\) can contain positive market exposures centered near one. The other seven columns can contain standardized positive and negative style exposures. This design creates a broadly positive market-driven average correlation while allowing pairwise correlations to vary because securities have different style exposures.

### 11.5 Generate security-specific shocks

Choose security-specific daily variances:

$$
d_\epsilon
=
\begin{bmatrix}
d_{\epsilon,1} & \cdots & d_{\epsilon,N}
\end{bmatrix}^\top,
\qquad
d_{\epsilon,i}>0.
$$

Define:

$$
D_\epsilon
=
\operatorname{Diag}
\left(
\sqrt{d_\epsilon}
\right),
$$

and:

$$
\Delta
=
D_\epsilon^2
=
\operatorname{Diag}(d_\epsilon).
$$

Generate independent specific source shocks:

$$
Z_{t,i}\overset{\text{iid}}{\sim}\mathcal{N}(0,1),
\qquad
Z\in\mathbb{R}^{T\times N}.
$$

Assume \(Z\) is independent of \(U\). The specific-return matrix is:

$$
E_\epsilon=ZD_\epsilon
\in\mathbb{R}^{T\times N}.
$$

For day \(t\):

$$
\epsilon_t=D_\epsilon z_t,
\qquad
\operatorname{Cov}(\epsilon_t)=\Delta.
$$

### 11.6 Generate the stock-return matrix

The eight-factor return process is:

$$
\boxed{
R
=
\mathbf{1}_T\mu^\top
+
FB^\top
+
ZD_\epsilon.
}
$$

For security \(i\) on day \(t\):

$$
\boxed{
r_{t,i}
=
\mu_i
+
b_i^\top f_t
+
\sqrt{d_{\epsilon,i}}\,Z_{t,i}.
}
$$

The three terms are:

1. expected daily return;
2. return explained by the eight common factors; and
3. security-specific return unexplained by the factors.

Because factor and specific shocks are independent:

$$
\begin{aligned}
\operatorname{Cov}(r_t)
&=
\operatorname{Cov}(Bf_t+\epsilon_t)\\
&=
B\operatorname{Cov}(f_t)B^\top
+
\operatorname{Cov}(\epsilon_t)\\
&=
\boxed{
BV_fB^\top+\Delta
}.
\end{aligned}
$$

Thus, the stock covariance matrix is:

$$
\boxed{
\Sigma=BV_fB^\top+\Delta.
}
$$

The first component has rank at most eight:

$$
\operatorname{rank}(BV_fB^\top)\leq8,
$$

while \(\Delta\) is diagonal. The simulation therefore produces returns that are consistent with an eight-factor, low-rank-plus-diagonal risk model.

### 11.7 Implied stock correlations

For security \(i\), the total variance is:

$$
\sigma_i^2
=
b_i^\top V_fb_i+d_{\epsilon,i}.
$$

For two distinct securities \(i\neq j\), specific shocks do not contribute to covariance:

$$
\operatorname{Cov}(r_{t,i},r_{t,j})
=
b_i^\top V_fb_j.
$$

Therefore, their implied correlation is:

$$
\boxed{
C_{ij}
=
\frac{
b_i^\top V_fb_j
}{
\sqrt{
\left(b_i^\top V_fb_i+d_{\epsilon,i}\right)
\left(b_j^\top V_fb_j+d_{\epsilon,j}\right)
}
}.
}
$$

Unlike the one-factor constant-correlation construction, correlations are heterogeneous. Securities with similar exposures tend to have larger positive correlations; opposing exposures can reduce correlations or make them negative.

### 11.8 Calibrate the model to a target average correlation

Start with an unscaled exposure matrix:

$$
B_0\in\mathbb{R}^{N\times K},
$$

and introduce a non-negative systematic-risk scale:

$$
B(\gamma)=\gamma B_0,
\qquad
\gamma\geq0.
$$

Define:

$$
M_0=B_0V_fB_0^\top.
$$

For a candidate \(\gamma\), the covariance matrix is:

$$
\Sigma(\gamma)
=
\gamma^2M_0+\Delta.
$$

Define its volatility matrix:

$$
D(\gamma)
=
\operatorname{Diag}
\left(
\sqrt{\operatorname{diag}(\Sigma(\gamma))}
\right),
$$

and its correlation matrix:

$$
C(\gamma)
=
D(\gamma)^{-1}
\Sigma(\gamma)
D(\gamma)^{-1}.
$$

The implied average pairwise correlation is:

$$
\bar{\rho}(\gamma)
=
\frac{1}{N(N-1)}
\sum_{i\neq j}C_{ij}(\gamma).
$$

Choose:

$$
\boxed{
\gamma^\star
=
\arg\min_{\gamma\geq0}
\left(
\bar{\rho}(\gamma)-\rho_{\mathrm{target}}
\right)^2.
}
$$

Then use:

$$
B=\gamma^\star B_0
$$

in the return-generation equation. A positive market-exposure column in \(B_0\) generally makes a positive target such as 0.30 attainable. The calibration result must still be checked numerically because arbitrary exposure patterns and specific variances may not support every requested target.

### 11.9 Vectorized NumPy form

Given `V_f`, `B`, `specific_variance`, and `mu`:

```python
K = 8

U = rng.standard_normal((T, K))
A_f = np.linalg.cholesky(V_f)
F = U @ A_f.T

Z = rng.standard_normal((T, N))
specific_volatility = np.sqrt(specific_variance)

R = (
    mu[None, :]
    + F @ B.T
    + Z * specific_volatility[None, :]
)
```

The factor and specific draws must be independent. The implied population covariance used to validate the generator is:

```python
Sigma = B @ V_f @ B.T + np.diag(specific_variance)
```

## 12. Vectorized NumPy implementation

The following code implements the one-factor construction using the same variable names as the mathematical specification:

```python
import numpy as np

rng = np.random.default_rng(seed)

T = n_days
N = n_assets
D = trading_days
rho = average_correlation

mu = np.broadcast_to(annual_return, (N,)) / D
s = np.broadcast_to(annual_volatility, (N,)) / np.sqrt(D)

f = rng.standard_normal(T)
Z = rng.standard_normal((T, N))

X = (
    np.sqrt(rho) * f[:, None]
    + np.sqrt(1.0 - rho) * Z
)

R = mu[None, :] + X * s[None, :]
```

The array expression `X * s[None, :]` is the NumPy equivalent of \(XS\): it scales column \(i\) by \(s_i\).

## 13. Population targets versus a 251-day sample

The constant-correlation procedures set the population moments:

$$
\mathbb{E}[r_t]=\mu,
\qquad
\operatorname{Cov}(r_t)=\Sigma,
\qquad
\operatorname{Corr}(r_{t,i},r_{t,j})=\rho.
$$

The eight-factor procedure instead sets:

$$
\mathbb{E}[r_t]=\mu,
\qquad
\operatorname{Cov}(r_t)=BV_fB^\top+\Delta,
$$

with heterogeneous pairwise correlations implied by \(B\), \(V_f\), and \(\Delta\). If the scale calibration in Section 11.8 is used, the population average correlation targets \(\rho_{\mathrm{target}}\), while individual pairwise correlations generally differ from it.

Neither procedure forces a finite sample of 251 observations to equal its population target. Sampling variation causes realized estimates to differ from population values.

Define the sample mean:

$$
\widehat{\mu}
=
\frac{1}{T}R^\top\mathbf{1}_T
\in\mathbb{R}^N,
$$

the centered return matrix:

$$
R_c
=
R-\mathbf{1}_T\widehat{\mu}^\top,
$$

and the sample covariance:

$$
\widehat{\Sigma}
=
\frac{1}{T-1}R_c^\top R_c.
$$

Let:

$$
\widehat{S}
=
\operatorname{Diag}
\left(
\sqrt{\operatorname{diag}(\widehat{\Sigma})}
\right).
$$

The sample correlation matrix is:

$$
\widehat{C}
=
\widehat{S}^{-1}
\widehat{\Sigma}
\widehat{S}^{-1}.
$$

The realized average pairwise correlation is:

$$
\widehat{\bar{\rho}}
=
\frac{1}{N(N-1)}
\sum_{i\neq j}\widehat{C}_{ij}.
$$

For the constant-correlation process, \(\widehat{\bar{\rho}}\) converges toward \(\rho\). For the calibrated eight-factor process, it converges toward \(\bar{\rho}(\gamma^\star)\).

## 14. Required validation

The implementation must verify:

1. \(R\) has shape \(T\times N\).
2. Every element of \(R\) is finite.
3. \(\rho\) is in its admissible range.
4. Every volatility \(s_i\) is strictly positive.
5. \(C=C^\top\) and \(\operatorname{diag}(C)=\mathbf{1}_N\).
6. The minimum eigenvalue of \(C\) is non-negative up to numerical tolerance.
7. The diagonal of \(\Sigma\) equals \(s\odot s\).
8. The realized average sample correlation is reported alongside the population target.

For the eight-factor process, it must additionally verify:

1. \(B\) has shape \(N\times8\).
2. \(V_f\) has shape \(8\times8\), is symmetric, and is positive semidefinite.
3. Every element of \(d_\epsilon\) is strictly positive.
4. \(U\) and \(Z\) are generated independently.
5. \(\Sigma=BV_fB^\top+\Delta\) is symmetric and positive semidefinite.
6. The calibrated population average correlation is reported alongside \(\rho_{\mathrm{target}}\).

## 15. Optional heterogeneous-correlation extension

The constant-correlation baseline deliberately makes every pairwise correlation equal. For a heterogeneous correlation matrix, the generation step remains unchanged:

$$
R=\mathbf{1}_T\mu^\top+EA^\top,
\qquad
AA^\top=SCS.
$$

Only the design of \(C\) changes.

Inspired by the supplied code, one may generate an orthonormal matrix \(Q\), select non-negative eigenvalues, and construct a provisional covariance through:

$$
\widetilde{\Sigma}
=
Q\widetilde{\Lambda}Q^\top.
$$

Normalize it into a correlation matrix:

$$
\widetilde{C}
=
\widetilde{D}^{-1}
\widetilde{\Sigma}
\widetilde{D}^{-1},
$$

where:

$$
\widetilde{D}
=
\operatorname{Diag}
\left(
\sqrt{\operatorname{diag}(\widetilde{\Sigma})}
\right).
$$

The resulting \(\widetilde{C}\) must then be calibrated if its mean off-diagonal correlation is required to equal a specified target. Randomly rotating eigenvectors alone does not guarantee a chosen average correlation.

## 16. Generation sequence summary

The complete baseline sequence is:

$$
\boxed{
\begin{aligned}
E_{t,i}
&\overset{\text{iid}}{\sim}\mathcal{N}(0,1),\\
\mu
&=\mu^{(a)}/D,\\
s
&=s^{(a)}/\sqrt{D},\\
S
&=\operatorname{Diag}(s),\\
C
&=(1-\rho)I_N+\rho\mathbf{1}_N\mathbf{1}_N^\top,\\
\Sigma
&=SCS,\\
AA^\top
&=\Sigma,\\
R
&=\mathbf{1}_T\mu^\top+EA^\top.
\end{aligned}
}
$$

For \(\rho\geq0\), the equivalent efficient sequence is:

$$
\boxed{
\begin{aligned}
f_t
&\overset{\text{iid}}{\sim}\mathcal{N}(0,1),\\
Z_{t,i}
&\overset{\text{iid}}{\sim}\mathcal{N}(0,1),\\
X
&=\sqrt{\rho}\,f\mathbf{1}_N^\top
+\sqrt{1-\rho}\,Z,\\
R
&=\mathbf{1}_T\mu^\top+XS.
\end{aligned}
}
$$

The eight-factor sequence is:

$$
\boxed{
\begin{aligned}
K
&=8,\\
U_{t,k}
&\overset{\text{iid}}{\sim}\mathcal{N}(0,1),\\
Z_{t,i}
&\overset{\text{iid}}{\sim}\mathcal{N}(0,1),\\
A_fA_f^\top
&=V_f,\\
F
&=UA_f^\top,\\
\Delta
&=\operatorname{Diag}(d_\epsilon),\\
D_\epsilon
&=\operatorname{Diag}(\sqrt{d_\epsilon}),\\
\Sigma
&=BV_fB^\top+\Delta,\\
R
&=\mathbf{1}_T\mu^\top+FB^\top+ZD_\epsilon.
\end{aligned}
}
$$
