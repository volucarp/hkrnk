# Empirical Equity Factor Return Model Specifications

## Overview

This specification defines an exact, finite-window, exponentially weighted rolling factor model using weighted sufficient-statistic matrices. Each day is updated through one rank-one addition and one rank-one removal, without rebuilding the rolling factor or security-return matrices.

Let \(L=52\), \(K=8\), and \(N\) be the number of securities. On day \(t\), \(f_t^+\in\mathbb{R}^K\) and \(r_t^+\in\mathbb{R}^N\) are the added factor-return and security-return vectors. The removed vectors are \(f_t^-=f_{t-L}\in\mathbb{R}^K\) and \(r_t^-=r_{t-L}\in\mathbb{R}^N\). The \(+\) and \(-\) superscripts label added and removed observations; they are not arithmetic signs.

## 1. Rolling exponential weights

For half-life \(h=52\):

$$a=2^{-1/h}=2^{-1/52}.$$

For a finite \(L=52\) day window, the normalized leading weight is:

$$c=\frac{1-a}{1-a^L}=2(1-a),$$

where the latter equality follows from \(a^{52}=1/2\). The oldest-to-newest window weights are:

$$w=c\begin{bmatrix}a^{L-1}\\a^{L-2}\\\vdots\\a\\1\end{bmatrix},\qquad\mathbf{1}^{\top}w=1.$$

The current rolling factor and security-return matrices are:

$$F_t=\begin{bmatrix}f_{t-L+1}^{\top}\\\vdots\\f_t^{\top}\end{bmatrix}\in\mathbb{R}^{L\times K},\qquad R_t=\begin{bmatrix}r_{t-L+1}^{\top}\\\vdots\\r_t^{\top}\end{bmatrix}\in\mathbb{R}^{L\times N}.$$

## 2. Augmented regression representation

Include an intercept by defining:

$$z_s=\begin{bmatrix}1\\f_s\end{bmatrix}\in\mathbb{R}^{K+1},\qquad z_t^+=\begin{bmatrix}1\\f_t^+\end{bmatrix},\qquad z_t^-=\begin{bmatrix}1\\f_t^-\end{bmatrix}.$$

Maintain the weighted sufficient statistics:

$$G_t=c\sum_{j=0}^{L-1}a^jz_{t-j}z_{t-j}^{\top}\in\mathbb{R}^{(K+1)\times(K+1)},$$

$$H_t=c\sum_{j=0}^{L-1}a^jz_{t-j}r_{t-j}^{\top}\in\mathbb{R}^{(K+1)\times N},$$

$$q_t=c\sum_{j=0}^{L-1}a^j(r_{t-j}\odot r_{t-j})\in\mathbb{R}^N,$$

where \(\odot\) denotes elementwise multiplication.

## 3. Daily add/remove updates

Update the state without rebuilding \(F_t\) or \(R_t\):

$$\boxed{G_t=aG_{t-1}+cz_t^+(z_t^+)^{\top}-ca^Lz_t^-(z_t^-)^{\top}}$$

$$\boxed{H_t=aH_{t-1}+cz_t^+(r_t^+)^{\top}-ca^Lz_t^-(r_t^-)^{\top}}$$

$$\boxed{q_t=aq_{t-1}+c(r_t^+\odot r_t^+)-ca^L(r_t^-\odot r_t^-)}$$

The \(a^L\) coefficient arises because the removed observation has aged one further period after the previous state is decayed by \(a\). Each update is a decayed state plus a rank-one addition minus a rank-one removal.

## 4. Means and moments

Partition the sufficient statistics as:

$$G_t=\begin{bmatrix}1&\mu_{f,t}^{\top}\\\mu_{f,t}&S_{ff,t}\end{bmatrix},\qquad H_t=\begin{bmatrix}\mu_{r,t}^{\top}\\S_{fr,t}\end{bmatrix}.$$

The component moments are:

$$\mu_{f,t}=c\sum_{j=0}^{L-1}a^jf_{t-j}\in\mathbb{R}^K,\qquad S_{ff,t}=c\sum_{j=0}^{L-1}a^jf_{t-j}f_{t-j}^{\top}\in\mathbb{R}^{K\times K},$$

$$\mu_{r,t}=c\sum_{j=0}^{L-1}a^jr_{t-j}\in\mathbb{R}^N,\qquad S_{fr,t}=c\sum_{j=0}^{L-1}a^jf_{t-j}r_{t-j}^{\top}\in\mathbb{R}^{K\times N}.$$

## 5. Factor VCV and cross-covariance

The centered factor covariance is:

$$\boxed{V_{f,t}=S_{ff,t}-\mu_{f,t}\mu_{f,t}^{\top}}$$

It is also the Schur complement of the upper-left block of \(G_t\):

$$V_{f,t}=G_{22,t}-G_{21,t}G_{11,t}^{-1}G_{12,t}=G_{22,t}-G_{21,t}G_{12,t},$$

because normalized weights give \(G_{11,t}=1\).

The factor-security cross-covariance and vector of security variances are:

$$\boxed{C_{fr,t}=S_{fr,t}-\mu_{f,t}\mu_{r,t}^{\top}},\qquad C_{rf,t}=C_{fr,t}^{\top},$$

$$\boxed{v_{r,t}=q_t-\mu_{r,t}\odot\mu_{r,t}}.$$

No \(N\times N\) empirical security covariance matrix is required.

## 6. Factor volatility and correlation

Define:

$$\boxed{\mathcal{V}_{f,t}=\operatorname{Diag}\!\left(\operatorname{diag}(V_{f,t})\right)},\qquad D_{f,t}=\mathcal{V}_{f,t}^{1/2}.$$

Then:

$$\boxed{C_{f,t}=D_{f,t}^{-1}V_{f,t}D_{f,t}^{-1}},\qquad\boxed{V_{f,t}=D_{f,t}C_{f,t}D_{f,t}}.$$

This separates factor volatility from factor correlation.

## 7. All security betas in one matrix solve

Define:

$$\Theta_t=\begin{bmatrix}\alpha_t^{\top}\\B_t^{\top}\end{bmatrix}\in\mathbb{R}^{(K+1)\times N},$$

where \(\alpha_t\in\mathbb{R}^N\) contains intercepts and \(B_t\in\mathbb{R}^{N\times K}\) contains factor betas. The weighted rolling regression is:

$$\boxed{\Theta_t=\arg\min_{\Theta}\sum_{j=0}^{L-1}ca^j\left\lVert r_{t-j}-\Theta^{\top}z_{t-j}\right\rVert_2^2}$$

or equivalently:

$$\Theta_t=\arg\min_{\Theta}\left\lVert W_t^{1/2}(R_t-Z_t\Theta)\right\rVert_F^2.$$

The normal equations are:

$$\boxed{G_t\Theta_t=H_t}.$$

Conceptually, \(\Theta_t=G_t^{-1}H_t\), but the implementation must use one matrix solve rather than an explicit inverse or \(N\) independent regressions.

The centered beta equations are:

$$\boxed{B_t=C_{rf,t}V_{f,t}^{-1}},\qquad\boxed{V_{f,t}B_t^{\top}=C_{fr,t}}.$$

Thus, one \(8\times8\) factor solve produces betas for all securities. The intercepts are:

$$\boxed{\alpha_t=\mu_{r,t}-B_t\mu_{f,t}}.$$

## 8. Smooth rolling betas

To shrink today's beta estimate toward yesterday's, set \(B_{0,t}=B_{t-1}\) and define:

$$P=\begin{bmatrix}0&0\\0&I_K\end{bmatrix},\qquad\Theta_{0,t}=\begin{bmatrix}0\\B_{t-1}^{\top}\end{bmatrix}.$$

The intercept is not penalized. Solve:

$$\boxed{\Theta_t=\arg\min_{\Theta}\left\lVert W_t^{1/2}(R_t-Z_t\Theta)\right\rVert_F^2+\lambda\left\lVert P^{1/2}(\Theta-\Theta_{0,t})\right\rVert_F^2}$$

with normal equations:

$$\boxed{(G_t+\lambda P)\Theta_t=H_t+\lambda P\Theta_{0,t}}.$$

Conceptually:

$$\Theta_t=(G_t+\lambda P)^{-1}\left(H_t+\lambda P\Theta_{0,t}\right).$$

The centered form is:

$$\boxed{B_t=\left(C_{rf,t}+\lambda B_{t-1}\right)\left(V_{f,t}+\lambda I_K\right)^{-1}}.$$

This produces all \(N\times8\) rolling betas in one matrix operation.

## 9. Specific variances without residual matrices

For \(\hat{r}_s=\Theta_t^{\top}z_s\), compute the weighted residual second-moment vector entirely from sufficient statistics:

$$\boxed{d_{\epsilon,t}=q_t-2\operatorname{diag}(\Theta_t^{\top}H_t)+\operatorname{diag}(\Theta_t^{\top}G_t\Theta_t)}.$$

Equivalently:

$$\boxed{d_{\epsilon,t}=q_t-2(\Theta_t\odot H_t)^{\top}\mathbf{1}_{K+1}+\left[\Theta_t\odot(G_t\Theta_t)\right]^{\top}\mathbf{1}_{K+1}}.$$

For unregularized WLS, \(G_t\Theta_t=H_t\), giving:

$$\boxed{d_{\epsilon,t}=q_t-\operatorname{diag}(\Theta_t^{\top}H_t)=q_t-(\Theta_t\odot H_t)^{\top}\mathbf{1}_{K+1}}.$$

The specific-risk matrix is:

$$\boxed{\Delta_t=\operatorname{Diag}(d_{\epsilon,t}).}$$

Using centered quantities, ordinary WLS gives:

$$\boxed{d_{\epsilon,t}=v_{r,t}-\operatorname{diag}(B_tC_{fr,t}).}$$

For ridge or smoothed betas:

$$\boxed{d_{\epsilon,t}=v_{r,t}-2\operatorname{diag}(B_tC_{fr,t})+\operatorname{diag}(B_tV_{f,t}B_t^{\top}).}$$

The diagonal terms can be computed vectorially:

$$\operatorname{diag}(B_tC_{fr,t})=(B_t\odot C_{rf,t})\mathbf{1}_K,$$

$$\operatorname{diag}(B_tV_{f,t}B_t^{\top})=\left[(B_tV_{f,t})\odot B_t\right]\mathbf{1}_K.$$

No \(N\times N\) intermediate matrix is required.

## 10. Daily security VCV

The factor-model security covariance matrix is:

$$\boxed{\Sigma_t=B_tV_{f,t}B_t^{\top}+\Delta_t.}$$

This is a low-rank-plus-diagonal decomposition:

$$\underbrace{\Sigma_t}_{N\times N}=\underbrace{B_tV_{f,t}B_t^{\top}}_{\operatorname{rank}\leq8}+\underbrace{\Delta_t}_{\text{diagonal}}.$$

In many applications, \(\Sigma_t\) should not be formed explicitly. For \(x\in\mathbb{R}^N\):

$$\boxed{\Sigma_tx=B_tV_{f,t}(B_t^{\top}x)+d_{\epsilon,t}\odot x.}$$

Portfolio variance is:

$$\boxed{\sigma_{p,t}^2=x^{\top}\Sigma_tx=(B_t^{\top}x)^{\top}V_{f,t}(B_t^{\top}x)+(x\odot x)^{\top}d_{\epsilon,t}.}$$

This reduces security-level risk calculations to operations involving an \(8\times8\) matrix.

## 11. Useful decompositions

### Cholesky factorization

Factor the regularized rolling system as:

$$G_t+\lambda P=L_tL_t^{\top}.$$

Then solve:

$$L_tU_t=H_t+\lambda P\Theta_{0,t},\qquad L_t^{\top}\Theta_t=U_t.$$

This solves for every security simultaneously. Because \(K+1=9\), recomputing this small Cholesky factor daily is generally more stable than maintaining an explicit inverse.

### Rank-one update and downdate

The Gram matrix is obtained from \(aG_{t-1}\) with one rank-one Cholesky update and one rank-one Cholesky downdate:

$$G_t=aG_{t-1}+cz_t^+(z_t^+)^{\top}-ca^Lz_t^-(z_t^-)^{\top}.$$

The same add/remove structure applies to \(H_t\), although \(H_t\) is updated directly rather than factorized.

### Woodbury identity

For \(\Sigma_t=\Delta_t+B_tV_{f,t}B_t^{\top}\):

$$\boxed{\Sigma_t^{-1}=\Delta_t^{-1}-\Delta_t^{-1}B_t\left(V_{f,t}^{-1}+B_t^{\top}\Delta_t^{-1}B_t\right)^{-1}B_t^{\top}\Delta_t^{-1}.}$$

The difficult inverse is only \(8\times8\).

## Compact daily system

The core daily state updates are:

$$\boxed{\begin{aligned}G_t&=aG_{t-1}+cz_t^+(z_t^+)^{\top}-ca^Lz_t^-(z_t^-)^{\top},\\H_t&=aH_{t-1}+cz_t^+(r_t^+)^{\top}-ca^Lz_t^-(r_t^-)^{\top},\\q_t&=aq_{t-1}+c(r_t^+\odot r_t^+)-ca^L(r_t^-\odot r_t^-).\end{aligned}}$$

Then solve:

$$\boxed{(G_t+\lambda P)\Theta_t=H_t+\lambda P\Theta_{0,t}},$$

derive:

$$\boxed{V_{f,t}=S_{ff,t}-\mu_{f,t}\mu_{f,t}^{\top}},\qquad\boxed{\Delta_t=\operatorname{Diag}(d_{\epsilon,t})},$$

and form or apply:

$$\boxed{\Sigma_t=B_tV_{f,t}B_t^{\top}+\Delta_t.}$$

The result is an exact finite-window exponentially weighted rolling model implemented with vectorized rank-one additions, removals, and small matrix factorizations.
