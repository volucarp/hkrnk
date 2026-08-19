"""Reproducible simulation of returns from an eight-factor equity model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike, NDArray


DEFAULT_FACTOR_ANNUAL_VOLATILITY = np.array(
    [0.18, 0.10, 0.09, 0.12, 0.08, 0.08, 0.07, 0.09]
)


@dataclass(frozen=True)
class SimulatedReturns:
    """A simulation and the population parameters which generated it."""

    factor_returns: NDArray[np.float64]
    stock_returns: NDArray[np.float64]
    exposures: NDArray[np.float64]
    factor_covariance: NDArray[np.float64]
    specific_variance: NDArray[np.float64]
    expected_daily_return: NDArray[np.float64]
    systematic_scale: float
    population_average_correlation: float
    seed: int

    def save(self, path: str | Path) -> None:
        """Save every result and parameter in one lossless, compressed archive."""
        np.savez_compressed(
            path,
            factor_returns=self.factor_returns,
            stock_returns=self.stock_returns,
            exposures=self.exposures,
            factor_covariance=self.factor_covariance,
            specific_variance=self.specific_variance,
            expected_daily_return=self.expected_daily_return,
            systematic_scale=self.systematic_scale,
            population_average_correlation=self.population_average_correlation,
            seed=self.seed,
        )


def _vector(value: ArrayLike, length: int, name: str) -> NDArray[np.float64]:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim == 0:
        result = np.full(length, result.item())
    if result.shape != (length,):
        raise ValueError(f"{name} must be a scalar or have shape ({length},)")
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite values")
    return result


def _covariance_root(covariance: NDArray[np.float64]) -> NDArray[np.float64]:
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("factor_covariance must be square")
    if not np.isfinite(covariance).all() or not np.allclose(covariance, covariance.T):
        raise ValueError("factor_covariance must be finite and symmetric")
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    tolerance = np.finfo(float).eps * covariance.shape[0] * max(1.0, np.max(abs(eigenvalues)))
    if eigenvalues.min() < -tolerance:
        raise ValueError("factor_covariance must be positive semidefinite")
    # The spectral root applies each requested eigenvalue without changing its
    # relative magnitude (unlike ad-hoc diagonal jitter).
    return eigenvectors @ np.diag(np.sqrt(np.clip(eigenvalues, 0.0, None)))


def _average_correlation(
    scale: float, loadings: NDArray[np.float64], specific_variance: NDArray[np.float64]
) -> float:
    variance = scale * scale * np.sum(loadings * loadings, axis=1) + specific_variance
    standardized = scale * loadings / np.sqrt(variance)[:, None]
    off_diagonal_sum = np.sum(np.sum(standardized, axis=0) ** 2) - np.sum(
        standardized * standardized
    )
    n_assets = loadings.shape[0]
    return float(off_diagonal_sum / (n_assets * (n_assets - 1)))


def _calibrate_scale(
    target: float, loadings: NDArray[np.float64], specific_variance: NDArray[np.float64]
) -> tuple[float, float]:
    grid = np.geomspace(1e-4, 1e4, 2_000)
    values = np.array([_average_correlation(x, loadings, specific_variance) for x in grid])
    errors = values - target
    crossings = np.flatnonzero(errors[:-1] * errors[1:] <= 0.0)
    if not crossings.size:
        closest = int(np.argmin(abs(errors)))
        raise ValueError(
            f"target_average_correlation={target} is unattainable; "
            f"closest value is {values[closest]:.6f}"
        )
    lower, upper = grid[crossings[0]], grid[crossings[0] + 1]
    lower_error = errors[crossings[0]]
    for _ in range(60):
        midpoint = np.sqrt(lower * upper)
        midpoint_error = _average_correlation(midpoint, loadings, specific_variance) - target
        if lower_error * midpoint_error <= 0.0:
            upper = midpoint
        else:
            lower, lower_error = midpoint, midpoint_error
    scale = float(np.sqrt(lower * upper))
    return scale, _average_correlation(scale, loadings, specific_variance)


def generate_returns(
    *,
    n_assets: int = 1_000,
    n_years: int = 10,
    trading_days: int = 251,
    seed: int = 7,
    annual_return: ArrayLike = 0.08,
    factor_annual_volatility: ArrayLike = DEFAULT_FACTOR_ANNUAL_VOLATILITY,
    factor_correlation: ArrayLike | None = None,
    specific_annual_volatility: ArrayLike | None = None,
    target_average_correlation: float = 0.30,
    exact_factor_moments: bool = True,
) -> SimulatedReturns:
    """Generate seeded factor and stock returns according to the documented model.

    Defaults produce 2,510 daily observations for 1,000 stocks and eight factors.
    When ``exact_factor_moments`` is true, the finite sample factor mean is zero
    and its sample covariance (``ddof=1``) equals the requested covariance up to
    floating-point precision, so its eigenvalue ratios are preserved.
    """
    if n_assets < 2 or n_years < 1 or trading_days < 2:
        raise ValueError("n_assets >= 2, n_years >= 1, and trading_days >= 2 are required")
    factor_volatility = np.asarray(factor_annual_volatility, dtype=float)
    if factor_volatility.ndim != 1 or factor_volatility.size < 1:
        raise ValueError("factor_annual_volatility must be a non-empty vector")
    if not np.isfinite(factor_volatility).all() or np.any(factor_volatility <= 0):
        raise ValueError("factor annual volatilities must be finite and positive")
    n_factors = factor_volatility.size
    n_days = n_years * trading_days
    if exact_factor_moments and n_days <= n_factors:
        raise ValueError("exact factor moments require n_days > n_factors")

    correlation = np.eye(n_factors) if factor_correlation is None else np.asarray(
        factor_correlation, dtype=float
    )
    if correlation.shape != (n_factors, n_factors):
        raise ValueError(f"factor_correlation must have shape ({n_factors}, {n_factors})")
    if not np.allclose(np.diag(correlation), 1.0):
        raise ValueError("factor_correlation must have a unit diagonal")
    daily_factor_volatility = factor_volatility / np.sqrt(trading_days)
    factor_covariance = correlation * np.outer(
        daily_factor_volatility, daily_factor_volatility
    )
    root = _covariance_root(factor_covariance)

    rng = np.random.default_rng(seed)
    factor_shocks = rng.standard_normal((n_days, n_factors))
    if exact_factor_moments:
        factor_shocks -= factor_shocks.mean(axis=0)
        sample_covariance = factor_shocks.T @ factor_shocks / (n_days - 1)
        whitening_root = _covariance_root(sample_covariance)
        factor_shocks = np.linalg.solve(whitening_root, factor_shocks.T).T
    factor_returns = factor_shocks @ root.T

    market_beta = np.clip(rng.normal(1.0, 0.15, n_assets), 0.4, 1.6)
    style_exposures = rng.normal(0.0, 0.35, (n_assets, n_factors - 1))
    base_exposures = np.column_stack((market_beta, style_exposures))
    if specific_annual_volatility is None:
        specific_daily_volatility = rng.uniform(0.18, 0.35, n_assets) / np.sqrt(trading_days)
    else:
        specific_daily_volatility = _vector(
            specific_annual_volatility, n_assets, "specific_annual_volatility"
        ) / np.sqrt(trading_days)
        if np.any(specific_daily_volatility <= 0):
            raise ValueError("specific annual volatilities must be positive")
    specific_variance = specific_daily_volatility**2
    base_loadings = base_exposures @ root
    scale, achieved_correlation = _calibrate_scale(
        target_average_correlation, base_loadings, specific_variance
    )
    exposures = scale * base_exposures

    expected_daily_return = _vector(annual_return, n_assets, "annual_return") / trading_days
    specific_shocks = rng.standard_normal((n_days, n_assets))
    stock_returns = (
        expected_daily_return[None, :]
        + factor_returns @ exposures.T
        + specific_shocks * specific_daily_volatility[None, :]
    )
    return SimulatedReturns(
        factor_returns=factor_returns,
        stock_returns=stock_returns,
        exposures=exposures,
        factor_covariance=factor_covariance,
        specific_variance=specific_variance,
        expected_daily_return=expected_daily_return,
        systematic_scale=scale,
        population_average_correlation=achieved_correlation,
        seed=seed,
    )
