# Data Generation Procedures (`hkdis/voleon`)

This document summarizes the data-generation functions currently present in this folder and the mathematical procedures they implement.

## 1) `gen_mode.py`

### `data_pipeline(n=750, p=10, seed=42)`
Generates a single feature matrix with a random target correlation structure.

Procedure:
1. Draw IID Gaussian base:
   - \(Z \in \mathbb{R}^{n \times p}\), \(Z_{ij} \sim \mathcal{N}(0,1)\)
2. Build symmetric target matrix \(\Sigma\):
   - \(\Sigma_{ii}=1\)
   - \(\Sigma_{ij}=\Sigma_{ji}\sim \mathrm{Uniform}(-0.2,0.2)\), \(i\neq j\)
3. Enforce PSD by jitter:
   - If \(\lambda_{\min}(\Sigma)<0\), set
     \[
     \Sigma \leftarrow \Sigma + \left(-\lambda_{\min}(\Sigma)+\epsilon\right)I
     \]
4. Cholesky map:
   - \(A=\mathrm{chol}(\Sigma)\)
   - \(X = Z A^\top\)

Result:
- `X` with empirical covariance approximately \(\Sigma\)
- `Sigma` used to shape `X`

### `gen_corr_matrix(p=10, seed=42, limits=(-0.2, 0.2))`
Constructs a symmetric correlation-like matrix by filling upper-triangle entries from Uniform limits and mirroring.

Math:
\[
\Sigma_{ii}=1,\quad \Sigma_{ij}=\Sigma_{ji}\sim \mathrm{Uniform}(a,b)
\]

### `ensure_psd(Sigma, jitter=1e-6)`
Applies minimum-eigenvalue shift to make \(\Sigma\) PSD.

### `stretch_rotate(Z, Sigma)`
Returns \(X = Z\mathrm{chol}(\Sigma)^\top\).

### `gen_corr_matrix2(...)`
Intended to generate a symmetric random matrix, but currently uses `rng` without initialization in the function body. Treat as non-operational unless fixed.

---

## 2) `generate_two_mode_dataset.py`

Purpose:
- Build two regimes \((X_1,y_1)\), \((X_2,y_2)\) with opposite response sign.
- Enforce near-zero pooled linear signal by covariance scaling.

### `random_corr(p, rng, lo=0.0, hi=0.2)`
Samples off-diagonal entries uniformly in \([0,0.2]\), retries until matrix is PSD.

### `centered_orthonormal(n, p, rng)`
Creates \(Q\in\mathbb{R}^{n\times p}\) with orthonormal columns and approximately zero column means (via centering + QR).

### `generate(seed=7, n1=750, n2=250, p=10, noise_std=0.0)`
Core model:
1. Draw correlation matrix \(C\) with \(C_{ij}\in[0,0.2]\), \(i\neq j\).
2. Draw feature scales \(s_j\in[0.8,1.2]\), form
   \[
   \Sigma_1 = (ss^\top)\odot C
   \]
3. Set
   \[
   \Sigma_2 = \frac{n_1-1}{n_2-1}\Sigma_1
   \]
4. Generate features:
   \[
   X_1 = \sqrt{n_1-1}\,Q_1\,\mathrm{chol}(\Sigma_1)^\top,\quad
   X_2 = \sqrt{n_2-1}\,Q_2\,\mathrm{chol}(\Sigma_2)^\top
   \]
5. Draw unit vector \(\beta\), set
   \[
   y_1 = X_1\beta+\varepsilon_1,\quad
   y_2 = -X_2\beta+\varepsilon_2
   \]
   where \(\varepsilon_k\sim\mathcal{N}(0,\sigma^2)\).

Why pooled cancellation occurs:
- Opposite slopes and covariance scaling are chosen so pooled OLS slope tends to cancel.

---

## 3) `generate_two_mode_rotated.py`

Purpose:
- Two separated clusters in \(X\)
- Strongly rotated eigenspaces across regimes
- Per-regime strong linear fits but pooled OLS near zero

### `random_orthonormal(p, rng)`
Returns random orthonormal basis \(Q\in\mathbb{R}^{p\times p}\) (\(\det(Q)=+1\)).

### `givens_rotation(p, i, j, theta_rad)`
Returns a Givens rotation matrix \(G(i,j,\theta)\) acting in plane \((i,j)\).

### `generate(...)`
Builds regime geometry and response:
1. Build \(Q_1\), then \(Q_2 = Q_1R\), where
   \[
   R=\prod_k G(i_k,j_k,\theta_k)
   \]
   with large angles (82°, 74°, 67°, 58°, 49°) to force eigenspace rotation.
2. Define anisotropic covariances:
   \[
   \Sigma_1=Q_1\Lambda_1Q_1^\top,\quad
   \Sigma_2=Q_2\Lambda_2Q_2^\top
   \]
3. Separate means along regime-leading directions:
   \[
   \mu_1=\text{sep}\cdot q_{1,1},\quad
   \mu_2=-\text{sep}\cdot q_{2,1}
   \]
4. Sample:
   \[
   X_k\sim\mathcal{N}(\mu_k,\Sigma_k)
   \]
5. Center within mode:
   \[
   X_{kc}=X_k-\bar X_k
   \]
6. Draw \( \beta_1 \), then choose \( \beta_2 \) by exact cancellation:
   \[
   \beta_2=(X_{2c}^\top X_{2c})^{-1}(X_{1c}^\top X_{1c})\beta_1
   \]
   This enforces
   \[
   X^\top y = X_{1c}^\top(X_{1c}\beta_1)-X_{2c}^\top(X_{2c}\beta_2)\approx 0
   \]
7. Response:
   \[
   y_1=X_{1c}\beta_1+e_1,\quad y_2=-X_{2c}\beta_2+e_2
   \]
   with noise residualized against pooled centered \(X\), then demeaned by mode.

Diagnostics included in return:
- pooled/mode \(R^2\)
- eigenvector angles
- top-k principal angles between regime eigenspaces
- cluster center distance

---

## 4) `gen_ortho.py`

Purpose:
- In-memory generator used in modeling notebooks/scripts
- Target per-regime \(R^2\) (e.g., 0.2) with pooled \(R^2\approx 0\)

### Helpers
- `_random_orthonormal`: random basis \(Q\)
- `_givens`: plane rotation \(G(i,j,\theta)\)
- `_ols_r2`: OLS \(R^2\) calculator
- `_orth_noise`: constructs noise orthogonal to \([1, X]\), then scales it

### `generate_two_mode_canceling(...)`
Procedure:
1. Build rotated bases \(Q_1, Q_2\) using fixed large-angle Givens sequence.
2. Build \(\Sigma_1,\Sigma_2\) from eigenvalues and bases.
3. Sample two Gaussian modes with separated means.
4. Center each mode \(X_{1c},X_{2c}\).
5. Draw \(b_1\), compute
   \[
   b_2=(X_{2c}^\top X_{2c})^{-1}(X_{1c}^\top X_{1c})b_1
   \]
   so pooled cross-moment cancels:
   \[
   (X_{1c}^\top X_{1c})b_1-(X_{2c}^\top X_{2c})b_2=0
   \]
6. Raw regime signal:
   \[
   s_1=X_{1c}b_1,\quad s_2=-X_{2c}b_2
   \]
7. Calibrate noise to hit target regime \(R^2\):
   \[
   \sigma_e^2 = \mathrm{Var}(s)\frac{1-R^2_{\text{target}}}{R^2_{\text{target}}}
   \]
   Noise is orthogonalized to avoid reintroducing pooled linear signal.
8. Return `X`, `y`, `mode`, and diagnostic \(R^2\) values.

Interpretation:
- This is the most controlled function for experiments where each regime has meaningful signal but pooled linear fit is intentionally weak.

---

## Which generator to use

- Use `gen_ortho.generate_two_mode_canceling` for in-memory modeling experiments and target per-regime \(R^2\).
- Use `generate_two_mode_rotated.generate` if you also want explicit eigenspace-angle diagnostics and rotated-cluster geometry artifacts.
- Use `generate_two_mode_dataset.generate` for a simpler opposite-slope two-mode construction with bounded positive correlations.
- Use `gen_mode.py` utilities for basic covariance/correlation shaping primitives.
