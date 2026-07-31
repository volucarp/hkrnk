import numpy as np

n, p = 750, 10
rng = np.random.default_rng(42)

# 1) IID standard normal
Z = rng.standard_normal((n, p))



# 3) Ensure PSD (jitter if needed)
eig = np.linalg.eigvalsh(Sigma)
if eig.min() < 0:
    Sigma += np.eye(p) * (-eig.min() + 1e-6)

# 4) Stretch/rotate via matrix square root (Cholesky)
A = np.linalg.cholesky(Sigma)
X = Z @ A.T   # Now Cov(X) ≈ Sigma
