"""Run pooled and regime-specific OLS on synthetic data from gen_ortho.py."""

import argparse

import numpy as np

from gen_ortho import generate_two_mode_canceling


def fit_ols(x: np.ndarray, y: np.ndarray):
    """Fit OLS with intercept and return the fitted result object."""
    try:
        import statsmodels.api as sm
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "statsmodels is required. Install it with: pip install statsmodels"
        ) from exc
    x_ = sm.add_constant(x, has_constant="add")
    model = sm.OLS(y, x_)
    return model.fit()


def main():
    parser = argparse.ArgumentParser(
        description="Generate two-mode data in memory and print OLS summaries."
    )
    parser.add_argument("--n1", type=int, default=750)
    parser.add_argument("--n2", type=int, default=250)
    parser.add_argument("--p", type=int, default=10)
    parser.add_argument("--target-r2", type=float, default=0.2)
    parser.add_argument("--sep", type=float, default=5.0)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    x, y, mode, diag = generate_two_mode_canceling(
        n1=args.n1,
        n2=args.n2,
        p=args.p,
        target_r2=args.target_r2,
        sep=args.sep,
        seed=args.seed,
    )

    x1, y1 = x[mode == 1], y[mode == 1]
    x2, y2 = x[mode == 2], y[mode == 2]

    pooled = fit_ols(x, y)
    reg1 = fit_ols(x1, y1)
    reg2 = fit_ols(x2, y2)

    print("Generation diagnostics")
    print(diag)
    print()
    print("Pooled regression: y ~ X")
    print(pooled.summary())
    print()
    print("Mode 1 regression: y ~ X | mode=1")
    print(reg1.summary())
    print()
    print("Mode 2 regression: y ~ X | mode=2")
    print(reg2.summary())


if __name__ == "__main__":
    main()
