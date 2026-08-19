# Empirical Equity Factor Return Model

Workspace for calculating stock returns, estimating empirical equity factor
returns, and evaluating factor models.

Install the module and its dependencies with uv:

```bash
uv sync
```

Run Python inside the uv-managed environment with:

```bash
uv run python
```

Generate the reproducible default data set (1,000 stocks, eight factors, and
10 years x 251 trading days) and optionally persist it without CSV precision
loss:

```python
from empirical_equity_factor_model import generate_returns

simulation = generate_returns(seed=7)
simulation.save("returns_10y_1000_stocks.npz")

print(simulation.factor_returns.shape)  # (2510, 8)
print(simulation.stock_returns.shape)   # (2510, 1000)
```

All randomness comes from one NumPy generator. Reusing a seed reproduces every
factor return, exposure, specific variance, and stock return exactly. The
spectral covariance transform preserves the requested factor covariance's
eigenvalue magnitudes; by default the generated finite-sample factor covariance
also matches it to floating-point precision. Pass a positive-semidefinite
`factor_correlation` matrix or other annual factor volatilities to customize it.
