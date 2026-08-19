import numpy as np
import pytest

from empirical_equity_factor_model import generate_returns


def test_shapes_reproducibility_and_factor_covariance():
    first = generate_returns(n_assets=20, n_years=2, trading_days=30, seed=123)
    second = generate_returns(n_assets=20, n_years=2, trading_days=30, seed=123)

    assert first.factor_returns.shape == (60, 8)
    assert first.stock_returns.shape == (60, 20)
    assert np.array_equal(first.factor_returns, second.factor_returns)
    assert np.array_equal(first.stock_returns, second.stock_returns)
    assert np.allclose(
        np.cov(first.factor_returns, rowvar=False), first.factor_covariance, atol=1e-17
    )
    assert first.population_average_correlation == pytest.approx(0.30, abs=1e-12)


def test_dense_factor_covariance_preserves_eigenvalues():
    correlation = np.full((8, 8), 0.2)
    np.fill_diagonal(correlation, 1.0)
    result = generate_returns(
        n_assets=20,
        n_years=2,
        trading_days=30,
        seed=9,
        factor_correlation=correlation,
    )

    expected = np.linalg.eigvalsh(result.factor_covariance)
    actual = np.linalg.eigvalsh(np.cov(result.factor_returns, rowvar=False))
    assert np.allclose(actual, expected, rtol=1e-12, atol=1e-17)


def test_invalid_covariance_is_rejected():
    invalid = np.eye(8)
    invalid[0, 1] = invalid[1, 0] = 2.0
    with pytest.raises(ValueError, match="positive semidefinite"):
        generate_returns(n_assets=10, factor_correlation=invalid)
