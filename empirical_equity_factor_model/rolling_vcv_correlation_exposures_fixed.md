# Rolling Covariance, Correlation, and Exposure Estimation

## 1. Notation and dimensions

Let:

- \(T\): rolling-window length (number of time observations).
- \(k\): number of factors.
- \(n\): number of securities/assets.
- \(f_t \in \mathbb{R}^{k}\): factor-return vector at date \(t\).
- \(r_t \in \mathbb{R}^{n}\): security-return vector at date \(t\).
- \(F_t \in \mathbb{R}^{T\times k}\): factor-return history in the window ending at \(t\).
- \(R_t \in \mathbb{R}^{T\times n}\): security-return history in the same window.
- \(\mu_{f,t}\in\mathbb{R}^{k}\), \(\mu_{r,t}\in\mathbb{R}^{n}\): rolling means.
- \(\widetilde F_t\in\mathbb{R}^{T\times k}\), \(\widetilde R_t\in\mathbb{R}^{T\times n}\): demeaned return matrices.
- \(V_t\in\mathbb{R}^{k\times k}\): factor variance-covariance (VCV) matrix.
- \(C_t\in\mathbb{R}^{k\times k}\): factor correlation matrix.
- \(D_t=\operatorname{diag}(\sigma_{1,t},\ldots,\sigma_{k,t})\in\mathbb{R}^{k\times k}\): diagonal matrix of factor standard deviations.
- \(B_t\in\mathbb{R}^{n\times k}\): security factor exposures/betas.

Throughout, \(+\) denotes an observation entering the rolling window and \(-\) denotes an observation leaving it.

---

## 2. Initial factor VCV computation

### 2.1 Demeaning

For the initial window,

\[
\mu_f=\frac{1}{T}\sum_{i=1}^{T}f_i,
\qquad
\widetilde f_i=f_i-\mu_f.
\]

Equivalently,

\[
\widetilde F=F-\mathbf 1_T\mu_f^T.
\]

**Dimensions**

\[
F,\widetilde F\in\mathbb{R}^{T\times k},
\qquad
\mu_f\in\mathbb{R}^{k}.
\]

**Complexity**

\[
O(Tk).
\]

### 2.2 Sample VCV

\[
\boxed{
V=\frac{1}{T-1}\widetilde F^T\widetilde F
}
\]

or

\[
V=\frac{1}{T-1}\sum_{i=1}^{T}\widetilde f_i\widetilde f_i^T.
\]

Each diagonal element is a variance,

\[
V_{jj}=\operatorname{Var}(f_j)\ge 0,
\]

and each off-diagonal element is a covariance,

\[
V_{ij}=\operatorname{Cov}(f_i,f_j).
\]

The covariance satisfies

\[
|V_{ij}|\le\sqrt{V_{ii}V_{jj}}.
\]

A covariance matrix is symmetric positive semidefinite. A strictly positive-definite VCV supports an ordinary Cholesky factorization.

**Dimensions**

\[
\widetilde F^T\widetilde F:
(k\times T)(T\times k)\rightarrow k\times k.
\]

**Complexity**

\[
\boxed{O(Tk^2)}.
\]

---

## 3. Sufficient statistics for an exact rolling sample covariance

Maintain

\[
\boxed{
s_{f,t}=\sum_{i\in W_t}f_i
}
\]

and

\[
\boxed{
Q_{ff,t}=\sum_{i\in W_t}f_if_i^T.
}
\]

Then

\[
\mu_{f,t}=\frac{s_{f,t}}{T}
\]

and

\[
\boxed{
V_t=
\frac{1}{T-1}
\left(
Q_{ff,t}-\frac{1}{T}s_{f,t}s_{f,t}^T
\right).
}
\]

This formulation handles a changing rolling mean exactly.

**Dimensions**

\[
s_{f,t}\in\mathbb{R}^{k},
\qquad
Q_{ff,t}\in\mathbb{R}^{k\times k},
\qquad
V_t\in\mathbb{R}^{k\times k}.
\]

**Storage**

\[
O(k^2)
\]

for the sufficient statistics, excluding the rolling observations needed to identify the observation leaving the window.

**Initialization complexity**

\[
O(Tk^2).
\]

---

## 4. Daily rolling VCV update

When \(f_t^+\) enters and \(f_t^-\) leaves,

\[
\boxed{
s_{f,t}
=
s_{f,t-1}+f_t^+-f_t^-.
}
\]

and

\[
\boxed{
Q_{ff,t}
=
Q_{ff,t-1}
+
f_t^+(f_t^+)^T
-
f_t^-(f_t^-)^T.
}
\]

Then

\[
V_t=
\frac{1}{T-1}
\left(
Q_{ff,t}-\frac1T s_{f,t}s_{f,t}^T
\right).
\]

**Dimensions**

\[
s_{f,t}\in\mathbb{R}^{k},
\qquad
Q_{ff,t},V_t\in\mathbb{R}^{k\times k}.
\]

**Complexity per date**

\[
s_f:\ O(k),
\]

\[
Q_{ff}:\ O(k^2),
\]

\[
V_t:\ O(k^2).
\]

Therefore,

\[
\boxed{\text{rolling VCV update}=O(k^2)}
\]

instead of

\[
\boxed{\text{native VCV recomputation}=O(Tk^2)}.
\]

The leading-order improvement in the covariance accumulation stage is approximately

\[
\boxed{T\times}.
\]

---

## 5. Correlation matrix

Define

\[
D_t=
\operatorname{diag}
\left(
\sqrt{V_{11,t}},\ldots,\sqrt{V_{kk,t}}
\right).
\]

Then

\[
\boxed{
C_t=D_t^{-1}V_tD_t^{-1}.
}
\]

Elementwise,

\[
\boxed{
C_{ij,t}
=
\frac{V_{ij,t}}
{\sqrt{V_{ii,t}V_{jj,t}}}.
}
\]

Its diagonal is \(1\) when all variances are nonzero, and

\[
-1\le C_{ij,t}\le 1.
\]

**Dimensions**

\[
D_t\in\mathbb{R}^{k\times k},
\qquad
C_t\in\mathbb{R}^{k\times k}.
\]

**Complexity**

Because \(D_t\) is diagonal, compute correlation by row/column scaling rather than dense matrix multiplication:

\[
\boxed{O(k^2)}.
\]

Thus:

- native covariance + correlation: \(O(Tk^2)\);
- rolling covariance + correlation: \(O(k^2)\).

The asymptotic improvement remains approximately \(T\times\).

---

## 6. Cholesky factorization

For a symmetric positive-definite covariance matrix,

\[
\boxed{
V_t=L_tL_t^T,
}
\]

where \(L_t\) is lower triangular.

The entries are constructed as

\[
L_{jj}
=
\sqrt{
V_{jj}-\sum_{\ell<j}L_{j\ell}^2
}
\]

and, for \(i>j\),

\[
L_{ij}
=
\frac{
V_{ij}-\sum_{\ell<j}L_{i\ell}L_{j\ell}
}{
L_{jj}
}.
\]

**Dimensions**

\[
V_t,L_t\in\mathbb{R}^{k\times k}.
\]

**Complexity from scratch**

Approximately

\[
\frac13k^3
\]

floating-point operations, hence

\[
\boxed{O(k^3)}.
\]

A successful Cholesky factorization also serves as a practical positive-definiteness check.

---

## 7. Cholesky update/downdate

If the covariance update has low-rank form,

\[
V_t
=
V_{t-1}+uu^T-vv^T,
\]

and

\[
V_{t-1}=L_{t-1}L_{t-1}^T,
\]

the Cholesky factor may be rank-one updated and downdated rather than recomputed.

For a fixed-mean/equally weighted covariance example,

\[
u=\frac{f^+}{\sqrt{T}},
\qquad
v=\frac{f^-}{\sqrt{T}}.
\]

Each rank-one Cholesky update or downdate costs

\[
\boxed{O(k^2)}
\]

instead of \(O(k^3)\).

**Dimensions**

\[
u,v\in\mathbb{R}^{k},
\qquad
L_t\in\mathbb{R}^{k\times k}.
\]

**Important**

When the rolling mean is re-estimated, the exact covariance change contains additional low-rank terms. The sufficient-statistics VCV update remains \(O(k^2)\), but the Cholesky update must reflect the full covariance change correctly.

Periodic full recomputation is useful for controlling accumulated floating-point error.

---

## 8. Eigendecomposition, PCA shrinkage, and SVD

For a symmetric VCV matrix,

\[
\boxed{
V=Q\Lambda Q^T
}
\]

where \(Q\) contains orthonormal eigenvectors and

\[
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_k).
\]

PCA or spectral shrinkage modifies the eigenvalues,

\[
\lambda_i\mapsto\widetilde\lambda_i,
\]

and reconstructs

\[
\boxed{
\widetilde V
=
Q\widetilde\Lambda Q^T.
}
\]

**Dimensions**

\[
Q\in\mathbb{R}^{k\times k},
\qquad
\Lambda,\widetilde\Lambda\in\mathbb{R}^{k\times k}.
\]

**Complexity**

A full dense symmetric eigendecomposition is

\[
\boxed{O(k^3)}.
\]

If one starts from the demeaned return matrix,

\[
\widetilde F=U\Sigma W^T,
\]

then

\[
V
=
\frac{1}{T-1}
W\Sigma^2W^T.
\]

Thus,

\[
Q=W,
\qquad
\lambda_i=\frac{\sigma_i^2}{T-1}.
\]

A thin SVD can be attractive when \(T\ll k\).

An existing Cholesky factor does not generally reduce a required full eigendecomposition to \(O(k^2)\).

---

## 9. Security-factor covariance sufficient statistics

Let

\[
r_i\in\mathbb{R}^{n},
\qquad
f_i\in\mathbb{R}^{k}.
\]

Maintain

\[
\boxed{
s_{r,t}=\sum_{i\in W_t}r_i
}
\]

and

\[
\boxed{
Q_{rf,t}
=
\sum_{i\in W_t}r_if_i^T.
}
\]

Together with

\[
s_{f,t}=\sum f_i,
\qquad
Q_{ff,t}=\sum f_if_i^T,
\]

define the demeaned security-factor cross-product

\[
\boxed{
S_{rf,t}
=
Q_{rf,t}
-
\frac1T s_{r,t}s_{f,t}^T
}
\]

and the demeaned factor cross-product

\[
\boxed{
S_{ff,t}
=
Q_{ff,t}
-
\frac1T s_{f,t}s_{f,t}^T.
}
\]

Then

\[
V_t=\frac{1}{T-1}S_{ff,t}.
\]

**Dimensions**

\[
s_{r,t}\in\mathbb{R}^{n},
\]

\[
Q_{rf,t},S_{rf,t}\in\mathbb{R}^{n\times k},
\]

\[
S_{ff,t}\in\mathbb{R}^{k\times k}.
\]

**Initial complexity**

\[
Q_{rf}=R^TF:\ O(Tnk),
\]

\[
Q_{ff}=F^TF:\ O(Tk^2).
\]

When \(n\gg k\), \(O(Tnk)\) usually dominates.

---

## 10. Rolling updates for exposure sufficient statistics

When \(r^+,f^+\) enter and \(r^-,f^-\) leave,

\[
\boxed{
s_{r,t}=s_{r,t-1}+r^+-r^-,
}
\]

\[
\boxed{
s_{f,t}=s_{f,t-1}+f^+-f^-,
}
\]

\[
\boxed{
Q_{rf,t}
=
Q_{rf,t-1}
+
r^+(f^+)^T
-
r^-(f^-)^T,
}
\]

\[
\boxed{
Q_{ff,t}
=
Q_{ff,t-1}
+
f^+(f^+)^T
-
f^-(f^-)^T.
}
\]

Then

\[
S_{rf,t}
=
Q_{rf,t}-\frac1T s_{r,t}s_{f,t}^T,
\]

\[
S_{ff,t}
=
Q_{ff,t}-\frac1T s_{f,t}s_{f,t}^T.
\]

**Dimensions**

\[
Q_{rf,t}\in\mathbb{R}^{n\times k},
\qquad
Q_{ff,t}\in\mathbb{R}^{k\times k}.
\]

**Complexity per date**

\[
s_r:\ O(n),
\]

\[
s_f:\ O(k),
\]

\[
Q_{rf}:\ O(nk),
\]

\[
Q_{ff}:\ O(k^2).
\]

Therefore,

\[
\boxed{O(nk+k^2)}
\]

per date, typically

\[
\boxed{O(nk)}
\]

when \(n\gg k\).

Native reconstruction from \(T\) observations is

\[
\boxed{O(Tnk+Tk^2)}.
\]

---

## 11. Betas / exposures from multivariate OLS

For the demeaned model

\[
r_i=Bf_i+\epsilon_i,
\]

with \(B\in\mathbb{R}^{n\times k}\),

\[
\boxed{
B_t
=
S_{rf,t}S_{ff,t}^{-1}.
}
\]

Equivalently,

\[
B_t
=
\operatorname{Cov}(r,f)
\operatorname{Cov}(f,f)^{-1}.
\]

Do not explicitly form \(S_{ff}^{-1}\) in a numerical implementation.

If

\[
S_{ff}=LL^T,
\]

solve

\[
LY=S_{rf}^T
\]

and then

\[
L^TB^T=Y.
\]

**Dimensions**

\[
S_{rf}\in\mathbb{R}^{n\times k},
\]

\[
S_{ff}\in\mathbb{R}^{k\times k},
\]

\[
B\in\mathbb{R}^{n\times k}.
\]

The system solved is

\[
S_{ff}B^T=S_{rf}^T,
\]

with

\[
(k\times k)(k\times n)=k\times n.
\]

**Complexity**

Fresh Cholesky:

\[
O(k^3).
\]

Triangular solves for \(n\) right-hand sides:

\[
\boxed{O(nk^2)}.
\]

Thus,

\[
\boxed{O(k^3+nk^2)}.
\]

If the Cholesky factor is already available,

\[
\boxed{O(nk^2)}.
\]

---

## 12. Univariate beta as a special case

For a single factor \(f\),

\[
\boxed{
\beta_j
=
\frac{\operatorname{Cov}(r_j,f)}
{\operatorname{Var}(f)}.
}
\]

For all \(n\) securities, once the rolling covariance sufficient statistics are maintained, this costs

\[
\boxed{O(n)}
\]

per date.

---

## 13. Native versus rolling computational cost

Assume a rolling window of \(T\) observations, \(k\) factors, and \(n\) securities.

| End result | Native recomputation per date | Rolling per date | Leading improvement |
|---|---:|---:|---:|
| Factor VCV \(V_t\) | \(O(Tk^2)\) | \(O(k^2)\) | about \(T\times\) |
| Correlation \(C_t\), including VCV | \(O(Tk^2)\) | \(O(k^2)\) | about \(T\times\) |
| Fresh Cholesky after VCV | \(O(Tk^2+k^3)\) | \(O(k^2+k^3)\) | depends on \(T/k\) |
| Rank-update Cholesky | \(O(Tk^2+k^3)\) | \(O(k^2)\) | potentially very large |
| Cross-products for exposures | \(O(Tnk+Tk^2)\) | \(O(nk+k^2)\) | about \(T\times\) for statistics |
| Final multivariate exposures \(B_t\) | \(O(Tnk+Tk^2+k^3+nk^2)\) | \(O(nk+k^2+k^3+nk^2)\) | depends on \(T,n,k\) |
| Exposures if Cholesky is already available | \(O(Tnk+Tk^2+nk^2)\) | \(O(nk+k^2+nk^2)\) | often substantial |
| Full PCA/eigen shrinkage | \(O(Tk^2+k^3)\) | \(O(k^2+k^3)\) | covariance stage improves; eigensolve remains \(O(k^3)\) |

### 13.1 VCV speedup

Ignoring constant factors,

\[
\text{native}=Tk^2,
\qquad
\text{rolling}=k^2.
\]

Therefore,

\[
\boxed{
\text{speedup}\approx T.
}
\]

### 13.2 Correlation speedup

Correlation normalization itself is \(O(k^2)\). The expensive native component is rebuilding the covariance.

Using an illustrative equal-constant operation model,

\[
\frac{Tk^2+k^2}{k^2+k^2}
=
\frac{T+1}{2}.
\]

Asymptotically,

\[
\boxed{O(T)}
\]

improvement remains.

### 13.3 Exposure speedup

A useful simplified comparison is

\[
\text{native}
\approx
Tnk+nk^2+k^3
\]

versus

\[
\text{rolling}
\approx
nk+nk^2+k^3.
\]

Divide by \(nk\):

\[
\text{native}
\approx
T+k+\frac{k^2}{n},
\]

\[
\text{rolling}
\approx
1+k+\frac{k^2}{n}.
\]

Thus an approximate speedup is

\[
\boxed{
\frac{T+k+k^2/n}
{1+k+k^2/n}.
}
\]

When \(n\gg k\),

\[
\boxed{
\text{speedup}
\approx
\frac{T+k}{1+k}.
}
\]

This is smaller than the roughly \(T\times\) improvement in the sufficient-statistics accumulation stage because the \(O(nk^2)\) regression solve still has to be performed each date if all exposures are required.

---

## 14. Recommended rolling pipeline

A practical daily pipeline is

\[
(f^-,r^-;\ f^+,r^+)
\]

\[
\downarrow
\]

update

\[
s_f,\quad Q_{ff},\quad s_r,\quad Q_{rf}
\]

\[
\downarrow
\]

construct

\[
S_{ff},\quad V,\quad C,\quad S_{rf}
\]

\[
\downarrow
\]

factor

\[
S_{ff}=LL^T
\]

\[
\downarrow
\]

solve

\[
S_{ff}B^T=S_{rf}^T.
\]

The main daily complexity stages are

\[
\boxed{
O(nk)
\quad\text{rolling statistics}
}
\]

\[
\boxed{
O(k^2)
\quad\text{VCV/correlation construction}
}
\]

\[
\boxed{
O(k^3)
\quad\text{fresh Cholesky, if required}
}
\]

\[
\boxed{
O(nk^2)
\quad\text{all multivariate exposure solves}.
}
\]

For \(n\gg k\), computing all multivariate exposures can become the dominant daily operation once the historical \(T\)-dimension has been removed from covariance and cross-product accumulation.

---

## 15. Key implementation conclusions

1. **VCV means variance-covariance matrix.** It is symmetric positive semidefinite; a strictly positive-definite VCV admits ordinary Cholesky factorization.
2. **Do not recompute a rolling covariance from all \(T\) observations unless necessary.** Maintain first moments and second cross-products.
3. Exact rolling covariance sufficient statistics are
   \[
   s_f=\sum f,
   \qquad
   Q_{ff}=\sum ff^T.
   \]
4. For rolling exposures additionally maintain
   \[
   s_r=\sum r,
   \qquad
   Q_{rf}=\sum rf^T.
   \]
5. These remove the historical dimension \(T\) from the daily sufficient-statistics update:
   - VCV: \(O(Tk^2)\rightarrow O(k^2)\);
   - security-factor cross-products: \(O(Tnk)\rightarrow O(nk)\).
6. **Use Cholesky solves rather than an explicit inverse** when computing exposures.
7. Reuse the Cholesky factor if it is already computed for the factor covariance.
8. **Cholesky does not replace PCA/eigen shrinkage** when the shrinkage rule actually requires eigenvalues/eigenvectors.
9. If eigendecomposition was used only as a positive-definiteness check, a successful Cholesky factorization makes it redundant.
10. A full PCA/eigendecomposition remains \(O(k^3)\) even when covariance statistics are rolled.
11. Periodically compare rolling statistics against a clean recomputation from the active window to control accumulated numerical error.

---

## 16. Compact formula reference

### Factor sufficient statistics

\[
s_f^t=s_f^{t-1}+f^+-f^-,
\]

\[
Q_{ff}^t=Q_{ff}^{t-1}+f^+(f^+)^T-f^-(f^-)^T,
\]

\[
S_{ff}^t=Q_{ff}^t-\frac1T s_f^t(s_f^t)^T,
\]

\[
V_t=\frac1{T-1}S_{ff}^t.
\]

### Correlation

\[
D_t=\operatorname{diag}\left(\sqrt{\operatorname{diag}(V_t)}\right),
\]

\[
C_t=D_t^{-1}V_tD_t^{-1}.
\]

### Security-factor sufficient statistics

\[
s_r^t=s_r^{t-1}+r^+-r^-,
\]

\[
Q_{rf}^t=Q_{rf}^{t-1}+r^+(f^+)^T-r^-(f^-)^T,
\]

\[
S_{rf}^t=Q_{rf}^t-\frac1T s_r^t(s_f^t)^T.
\]

### Exposures

\[
\boxed{
B_t=S_{rf}^t(S_{ff}^t)^{-1}
}
\]

but numerically solve

\[
\boxed{
S_{ff}^tB_t^T=(S_{rf}^t)^T
}
\]

using Cholesky rather than explicitly forming the inverse.
