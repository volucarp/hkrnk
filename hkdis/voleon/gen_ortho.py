import numpy as np

def _random_orthonormal(p, rng):
    """Return a random p x p orthonormal matrix with determinant +1."""
    q, _ = np.linalg.qr(rng.normal(size=(p, p)))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return q

def _givens(p, i, j, theta):
    """Return a p x p Givens rotation in the (i, j) plane by angle theta (radians)."""
    g = np.eye(p)
    c, s = np.cos(theta), np.sin(theta)
    g[i, i] = c
    g[j, j] = c
    g[i, j] = -s
    g[j, i] = s
    return g

def _ols_r2(X, y):
    """Fit OLS with intercept and return (slopes, R^2)."""
    A = np.c_[np.ones(len(X)), X]
    coef = np.linalg.lstsq(A, y, rcond=None)[0]
    yhat = A @ coef
    r2 = 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return coef[1:], r2

def _orth_noise(X, target_std, rng):
    """Generate noise orthogonal to [1, X], then scale it to target_std."""
    A = np.c_[np.ones(len(X)), X]
    z = rng.normal(size=len(X))
    e = z - A @ np.linalg.lstsq(A, z, rcond=None)[0]
    e -= e.mean()
    e *= target_std / e.std(ddof=1)
    return e

def generate_two_mode_canceling(
    n1=750, n2=250, p=10, target_r2=0.2, sep=5.0, seed=7
):
    """
    Generate two X-regimes whose pooled linear regression has near-zero R^2.

    Design:
    - Two Gaussian modes in X with separated means and rotated covariances.
    - Mode-specific linear signals are strong (target_r2 per mode).
    - Slopes are calibrated so pooled cross-moment cancels:
      (X1c^T X1c) b1 - (X2c^T X2c) b2 = 0.

    Returns:
    - X: stacked feature matrix, shape (n1+n2, p)
    - y: stacked response, shape (n1+n2,)
    - mode: regime labels (1 or 2), shape (n1+n2,)
    - diagnostics dict with regime and pooled R^2
    """
    rng = np.random.default_rng(seed)

    # Rotated eigenspaces
    q1 = _random_orthonormal(p, rng)
    r = np.eye(p)
    for (i, j, deg) in [(0, 9, 82), (1, 8, 74), (2, 7, 67), (3, 6, 58), (4, 5, 49)]:
        r = r @ _givens(p, i, j, np.deg2rad(deg))
    q2 = q1 @ r

    # Two cluster covariances + separated means
    lam1 = np.array([3.50, 2.60, 1.90, 1.35, 0.95, 0.70, 0.50, 0.34, 0.22, 0.14])
    lam2 = np.array([3.20, 2.70, 1.80, 1.25, 1.00, 0.72, 0.52, 0.36, 0.24, 0.16])
    S1 = q1 @ np.diag(lam1) @ q1.T
    S2 = q2 @ np.diag(lam2) @ q2.T
    mu1 = sep * q1[:, 0]
    mu2 = -sep * q2[:, 0]

    X1 = rng.multivariate_normal(mu1, S1, size=n1)
    X2 = rng.multivariate_normal(mu2, S2, size=n2)
    X1c = X1 - X1.mean(0)
    X2c = X2 - X2.mean(0)

    # Exact pooled cancellation condition:
    # X^T y = X1c^T(X1c b1) + X2c^T(-X2c b2) = G1 b1 - G2 b2 = 0.
    b1 = rng.normal(size=p)
    b1 /= np.linalg.norm(b1)
    b2 = np.linalg.solve(X2c.T @ X2c, (X1c.T @ X1c) @ b1)

    s1 = X1c @ b1
    s2 = -(X2c @ b2)

    # Calibrate noise so each regime has target R^2
    sd1 = np.sqrt(s1.var(ddof=1) * (1 - target_r2) / target_r2)
    sd2 = np.sqrt(s2.var(ddof=1) * (1 - target_r2) / target_r2)

    y1 = s1 + _orth_noise(X1c, sd1, rng)
    y2 = s2 + _orth_noise(X2c, sd2, rng)
    y1 -= y1.mean()
    y2 -= y2.mean()

    X = np.vstack([X1, X2])
    y = np.r_[y1, y2]
    mode = np.r_[np.ones(n1, dtype=int), np.full(n2, 2, dtype=int)]

    _, r2_pool = _ols_r2(X, y)
    _, r2_1 = _ols_r2(X1, y1)
    _, r2_2 = _ols_r2(X2, y2)

    return X, y, mode, {
        "r2_mode1": float(r2_1),
        "r2_mode2": float(r2_2),
        "r2_pooled": float(r2_pool),
    }

# Example
def example():
    """Minimal usage example."""
    X, y, mode, diag = generate_two_mode_canceling(target_r2=0.2, seed=7)
    print(diag)  # {'r2_mode1': ~0.2, 'r2_mode2': ~0.2, 'r2_pooled': ~0.0}
