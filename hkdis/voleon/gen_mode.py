import numpy as np

def data_pipeline(n=750, p=10, seed=42):

    n, p = 750, 10
    rng = np.random.default_rng(42)

    # 1) IID standard normal
    Z = rng.standard_normal((n, p))
    # 2) Target correlation matrix with random pairwise rhos
    Sigma = np.eye(p)
    for i in range(p):
        for j in range(i+1, p):
            rho = rng.uniform(-0.2, 0.2)
            Sigma[i, j] = rho
            Sigma[j, i] = rho
    # 3) Ensure PSD (jitter if needed)
    eig = np.linalg.eigvalsh(Sigma)
    if eig.min() < 0:
        Sigma += np.eye(p) * (-eig.min() + 1e-6)
    # 4) Stretch/rotate via matrix square root (Cholesky)
    A = np.linalg.cholesky(Sigma)
    X = Z @ A.T   # Now Cov(X) ≈ Sigma
    return X, Sigma

def gen_corr_matrix(p=10, seed=42, limits=(-0.2, 0.2)):
    rng = np.random.default_rng(seed)
    Sigma = np.eye(p)
    # indices of upper triangle (excluding diagonal)
    iu = np.triu_indices(p, k=1)
    # draw all pairwise correlations at once
    rhos = rng.uniform(limits[0], limits[1], size=len(iu[0]))
    Sigma[iu] = rhos
    Sigma[(iu[1], iu[0])] = rhos  # mirror to lower triangle
    np.fill_diagonal(Sigma, 1.0)  # ensure diagonal is exactly 1
    return Sigma

def gen_corr_matrix2(p=10, seed=42, limits=(-0.2, 0.2)):
    R = rng.uniform(-0.2, 0.2, size=(p, p))
    R = (R + R.T) / 2
    np.fill_diagonal(R, 1.0)
    Sigma = R
    return Sigma

def ensure_psd(Sigma, jitter=1e-6):
    eig = np.linalg.eigvalsh(Sigma)
    if eig.min() < 0:
        Sigma += np.eye(len(Sigma)) * (-eig.min() + jitter)
    return Sigma

def stretch_rotate(Z, Sigma):
    A = np.linalg.cholesky(Sigma)
    return Z @ A.T