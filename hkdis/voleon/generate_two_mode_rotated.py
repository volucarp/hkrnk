from pathlib import Path

import numpy as np


def random_orthonormal(p: int, rng: np.random.Generator) -> np.ndarray:
    q, _ = np.linalg.qr(rng.normal(size=(p, p)))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return q


def givens_rotation(p: int, i: int, j: int, theta_rad: float) -> np.ndarray:
    g = np.eye(p)
    c = np.cos(theta_rad)
    s = np.sin(theta_rad)
    g[i, i] = c
    g[j, j] = c
    g[i, j] = -s
    g[j, i] = s
    return g


def fit_ols_r2(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    x_ = np.column_stack([np.ones(len(x)), x])
    coef = np.linalg.lstsq(x_, y, rcond=None)[0]
    yhat = x_ @ coef
    sst = np.square(y - y.mean()).sum()
    sse = np.square(y - yhat).sum()
    return coef[1:], 1.0 - sse / sst


def principal_angles_deg(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    s = np.linalg.svd(u.T @ v, compute_uv=False)
    s = np.clip(s, -1.0, 1.0)
    return np.degrees(np.arccos(s))


def vector_angle_deg(u: np.ndarray, v: np.ndarray) -> float:
    c = np.clip(np.abs(u @ v) / (np.linalg.norm(u) * np.linalg.norm(v)), -1.0, 1.0)
    return float(np.degrees(np.arccos(c)))


def generate(
    seed: int = 7,
    n1: int = 750,
    n2: int = 250,
    p: int = 10,
    sep: float = 5.0,
    noise_std: float = 0.25,
) -> dict[str, np.ndarray | float]:
    rng = np.random.default_rng(seed)

    q1 = random_orthonormal(p, rng)
    rotation_angles_deg = np.array([82.0, 74.0, 67.0, 58.0, 49.0])
    pairs = [(0, p - 1), (1, p - 2), (2, p - 3), (3, p - 4), (4, p - 5)]

    r = np.eye(p)
    for (i, j), ang in zip(pairs, rotation_angles_deg):
        r = r @ givens_rotation(p, i, j, np.deg2rad(ang))
    q2 = q1 @ r

    eig1 = np.array([3.50, 2.60, 1.90, 1.35, 0.95, 0.70, 0.50, 0.34, 0.22, 0.14])
    eig2 = np.array([3.20, 2.70, 1.80, 1.25, 1.00, 0.72, 0.52, 0.36, 0.24, 0.16])
    sigma1 = q1 @ np.diag(eig1) @ q1.T
    sigma2 = q2 @ np.diag(eig2) @ q2.T

    mu1 = sep * q1[:, 0]
    mu2 = -sep * q2[:, 0]

    x1 = rng.multivariate_normal(mu1, sigma1, size=n1)
    x2 = rng.multivariate_normal(mu2, sigma2, size=n2)
    x1c = x1 - x1.mean(axis=0, keepdims=True)
    x2c = x2 - x2.mean(axis=0, keepdims=True)

    beta1 = rng.normal(size=p)
    beta1 /= np.linalg.norm(beta1)
    beta2 = np.linalg.solve(x2c.T @ x2c, (x1c.T @ x1c) @ beta1)

    eps = np.r_[rng.normal(0.0, noise_std, n1), rng.normal(0.0, noise_std, n2)]
    xc = np.vstack([x1c, x2c])
    eps -= xc @ np.linalg.lstsq(xc, eps, rcond=None)[0]
    e1, e2 = eps[:n1], eps[n1:]

    y1 = x1c @ beta1 + e1
    y2 = -(x2c @ beta2) + e2
    y1 -= y1.mean()
    y2 -= y2.mean()

    x_all = np.vstack([x1, x2])
    y_all = np.r_[y1, y2]

    b_all, r2_all = fit_ols_r2(x_all, y_all)
    b1, r2_1 = fit_ols_r2(x1, y1)
    b2, r2_2 = fit_ols_r2(x2, y2)

    eigvec_angles = np.array([vector_angle_deg(q1[:, i], q2[:, i]) for i in range(p)])
    top3_principal = principal_angles_deg(q1[:, :3], q2[:, :3])
    mean_dir_angle = float(
        np.degrees(np.arccos(np.clip((mu1 @ mu2) / (np.linalg.norm(mu1) * np.linalg.norm(mu2)), -1.0, 1.0)))
    )
    center_dist = float(np.linalg.norm(x1.mean(axis=0) - x2.mean(axis=0)))

    return {
        "x1": x1,
        "x2": x2,
        "y1": y1,
        "y2": y2,
        "beta1": beta1,
        "beta2": beta2,
        "q1": q1,
        "q2": q2,
        "sigma1": sigma1,
        "sigma2": sigma2,
        "rotation_angles_deg": rotation_angles_deg,
        "eigvec_angles": eigvec_angles,
        "top3_principal": top3_principal,
        "mean_dir_angle": mean_dir_angle,
        "center_dist": center_dist,
        "pooled_r2": float(r2_all),
        "mode1_r2": float(r2_1),
        "mode2_r2": float(r2_2),
        "pooled_beta_norm": float(np.linalg.norm(b_all)),
        "mode_slope_opposition_corr": float(np.corrcoef(b1, -b2)[0, 1]),
    }


def write_csv(path: Path, x: np.ndarray, y: np.ndarray, mode_value: int) -> None:
    p = x.shape[1]
    cols = [f"x{i+1}" for i in range(p)]
    header = ",".join(cols + ["y", "mode"])
    mode = np.full((len(x), 1), float(mode_value))
    data = np.column_stack([x, y, mode])
    np.savetxt(path, data, delimiter=",", header=header, comments="")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    res = generate()

    write_csv(out_dir / "mode1_rotated.csv", res["x1"], res["y1"], mode_value=1)
    write_csv(out_dir / "mode2_rotated.csv", res["x2"], res["y2"], mode_value=2)
    combined = np.vstack(
        [
            np.column_stack([res["x1"], res["y1"], np.ones((len(res["x1"]), 1))]),
            np.column_stack([res["x2"], res["y2"], np.full((len(res["x2"]), 1), 2.0)]),
        ]
    )
    header = ",".join([f"x{i+1}" for i in range(res["x1"].shape[1])] + ["y", "mode"])
    np.savetxt(out_dir / "combined_rotated.csv", combined, delimiter=",", header=header, comments="")

    np.save(out_dir / "beta_mode1.npy", res["beta1"])
    np.save(out_dir / "beta_mode2.npy", res["beta2"])
    np.save(out_dir / "cov_mode1.npy", res["sigma1"])
    np.save(out_dir / "cov_mode2.npy", res["sigma2"])
    np.save(out_dir / "eigvec_mode1.npy", res["q1"])
    np.save(out_dir / "eigvec_mode2.npy", res["q2"])

    print(f"saved to: {out_dir}")
    print(f"pooled R^2: {res['pooled_r2']:.8f}")
    print(f"mode1  R^2: {res['mode1_r2']:.8f}")
    print(f"mode2  R^2: {res['mode2_r2']:.8f}")
    print(f"||pooled beta||_2: {res['pooled_beta_norm']:.3e}")
    print(f"mode slope opposition corr (b1 vs -b2): {res['mode_slope_opposition_corr']:.4f}")
    print(f"cluster center distance: {res['center_dist']:.4f}")
    print(f"cluster-mean direction angle: {res['mean_dir_angle']:.2f} deg")
    print(f"top-3 eigenspace principal angles: {np.round(res['top3_principal'], 2)}")
    print(f"eigenvector angles (i vs i): {np.round(res['eigvec_angles'], 2)}")
