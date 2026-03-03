from pathlib import Path

import numpy as np


def random_corr(p: int, rng: np.random.Generator, lo: float = 0.0, hi: float = 0.2) -> np.ndarray:
    """PSD correlation matrix with off-diagonal entries ~ Uniform[lo, hi]."""
    iu = np.triu_indices(p, 1)
    while True:
        c = np.eye(p)
        v = rng.uniform(lo, hi, size=iu[0].size)
        c[iu] = v
        c[(iu[1], iu[0])] = v
        if np.linalg.eigvalsh(c).min() > 1e-12:
            return c


def centered_orthonormal(n: int, p: int, rng: np.random.Generator) -> np.ndarray:
    """n x p matrix with orthonormal, mean-zero columns."""
    a = rng.normal(size=(n, p))
    a -= a.mean(axis=0, keepdims=True)
    q, _ = np.linalg.qr(a, mode="reduced")
    return q


def ols_r2(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    x_ = np.column_stack([np.ones(len(x)), x])
    coef = np.linalg.lstsq(x_, y, rcond=None)[0]
    yhat = x_ @ coef
    sst = np.square(y - y.mean()).sum()
    sse = np.square(y - yhat).sum()
    return coef[1:], 1.0 - sse / sst


def generate(seed: int = 7, n1: int = 750, n2: int = 250, p: int = 10, noise_std: float = 0.0):
    rng = np.random.default_rng(seed)

    corr = random_corr(p, rng, 0.0, 0.2)
    std = rng.uniform(0.8, 1.2, size=p)
    sigma1 = np.outer(std, std) * corr
    sigma2 = ((n1 - 1) / (n2 - 1)) * sigma1  # inflates mode 2 so pooled slope cancels

    x1 = np.sqrt(n1 - 1) * centered_orthonormal(n1, p, rng) @ np.linalg.cholesky(sigma1).T
    x2 = np.sqrt(n2 - 1) * centered_orthonormal(n2, p, rng) @ np.linalg.cholesky(sigma2).T

    beta = rng.normal(size=p)
    beta /= np.linalg.norm(beta)
    y1 = x1 @ beta + rng.normal(0.0, noise_std, size=n1)
    y2 = -(x2 @ beta) + rng.normal(0.0, noise_std, size=n2)

    return x1, x2, y1, y2, beta, corr


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    x1, x2, y1, y2, beta, corr = generate(seed=7, noise_std=0.0)
    n1, p = x1.shape
    n2 = x2.shape[0]
    cols = [f"x{i+1}" for i in range(p)]
    header = ",".join(cols + ["y", "mode"])

    mode1 = np.column_stack([x1, y1, np.ones(n1)])
    mode2 = np.column_stack([x2, y2, np.full(n2, 2.0)])
    combined = np.vstack([mode1, mode2])

    np.savetxt(out_dir / "mode1.csv", mode1, delimiter=",", header=header, comments="")
    np.savetxt(out_dir / "mode2.csv", mode2, delimiter=",", header=header, comments="")
    np.savetxt(out_dir / "combined.csv", combined, delimiter=",", header=header, comments="")
    np.save(out_dir / "beta.npy", beta)
    np.save(out_dir / "feature_corr.npy", corr)

    x_all = np.vstack([x1, x2])
    y_all = np.concatenate([y1, y2])
    b_all, r2_all = ols_r2(x_all, y_all)
    b1, r2_1 = ols_r2(x1, y1)
    b2, r2_2 = ols_r2(x2, y2)

    print(f"saved to: {out_dir}")
    print(f"pooled R^2: {r2_all:.8f}")
    print(f"mode1 R^2:  {r2_1:.8f}")
    print(f"mode2 R^2:  {r2_2:.8f}")
    print(f"||b_pooled||_2: {np.linalg.norm(b_all):.3e}")
    print(f"||b1 - beta||_2: {np.linalg.norm(b1 - beta):.3e}")
    print(f"||b2 + beta||_2: {np.linalg.norm(b2 + beta):.3e}")
