"""Train and evaluate RandomForestRegressor on synthetic two-mode data."""

import argparse

import numpy as np
from gen_ortho import generate_two_mode_canceling

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
except ModuleNotFoundError as exc:
    raise SystemExit(
        "scikit-learn is required. Install it with: "
        "/Users/Shared/apps/miniforge3/envs/lpy/bin/python -m pip install scikit-learn"
    ) from exc


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run RandomForestRegressor on generated two-mode data."
    )
    parser.add_argument("--n1", type=int, default=750)
    parser.add_argument("--n2", type=int, default=250)
    parser.add_argument("--p", type=int, default=10)
    parser.add_argument("--target-r2", type=float, default=0.2)
    parser.add_argument("--sep", type=float, default=5.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--n-estimators", type=int, default=600)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--min-samples-leaf", type=int, default=5)
    parser.add_argument("--min-samples-split", type=int, default=10)
    parser.add_argument("--max-features", type=float, default=1.0)
    return parser.parse_args()


def metrics(y_true, y_pred):
    """Return basic regression metrics."""
    return {
        "r2": r2_score(y_true, y_pred),
        "rmse": mean_squared_error(y_true, y_pred, squared=False),
        "mae": mean_absolute_error(y_true, y_pred),
    }


def main():
    args = parse_args()

    x, y, mode, diag = generate_two_mode_canceling(
        n1=args.n1,
        n2=args.n2,
        p=args.p,
        target_r2=args.target_r2,
        sep=args.sep,
        seed=args.seed,
    )

    x_train, x_test, y_train, y_test, mode_train, mode_test = train_test_split(
        x,
        y,
        mode,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=mode,
    )

    # Tuned for low-dimensional tabular data (p ~ 10) with nonlinear regime effects.
    rf = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_leaf=args.min_samples_leaf,
        min_samples_split=args.min_samples_split,
        max_features=args.max_features,
        bootstrap=True,
        oob_score=True,
        n_jobs=-1,
        random_state=args.seed,
    )
    rf.fit(x_train, y_train)

    pred_train = rf.predict(x_train)
    pred_test = rf.predict(x_test)

    m_train = metrics(y_train, pred_train)
    m_test = metrics(y_test, pred_test)

    print("Generation diagnostics:")
    print(diag)
    print()
    print("RandomForest settings:")
    print(
        {
            "n_estimators": args.n_estimators,
            "max_depth": args.max_depth,
            "min_samples_leaf": args.min_samples_leaf,
            "min_samples_split": args.min_samples_split,
            "max_features": args.max_features,
        }
    )
    print()
    print("Overall metrics")
    print(f"train -> R2: {m_train['r2']:.4f} | RMSE: {m_train['rmse']:.4f} | MAE: {m_train['mae']:.4f}")
    print(f"test  -> R2: {m_test['r2']:.4f} | RMSE: {m_test['rmse']:.4f} | MAE: {m_test['mae']:.4f}")
    print(f"OOB R2: {rf.oob_score_:.4f}")
    print()

    print("Per-mode test metrics")
    for m in [1, 2]:
        idx = mode_test == m
        mm = metrics(y_test[idx], pred_test[idx])
        print(
            f"mode {m} -> R2: {mm['r2']:.4f} | RMSE: {mm['rmse']:.4f} | MAE: {mm['mae']:.4f} | n={idx.sum()}"
        )

    print()
    print("Feature importances")
    for i, val in enumerate(rf.feature_importances_, start=1):
        print(f"x{i}: {val:.4f}")


if __name__ == "__main__":
    main()
