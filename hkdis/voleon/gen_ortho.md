# Why `b2` Is Computed This Way

In the generator, regime signals are:

- `y1 = X1c @ b1`
- `y2 = -(X2c @ b2)`

where `X1c` and `X2c` are centered feature matrices for each mode.

For pooled OLS, the slope numerator is:

`X.T @ y = X1c.T @ y1 + X2c.T @ y2 = (X1c.T @ X1c) @ b1 - (X2c.T @ X2c) @ b2`

Define:

- `G1 = X1c.T @ X1c`
- `G2 = X2c.T @ X2c`

To force pooled linear signal to cancel, enforce:

`G1 @ b1 - G2 @ b2 = 0`

So:

`b2 = G2^{-1} @ G1 @ b1`

which is exactly:

```python
b2 = np.linalg.solve(X2c.T @ X2c, (X1c.T @ X1c) @ b1)
```

## Why `b2 != -b1` in general

- The minus sign is already applied in `y2 = -(X2c @ b2)`, so mode-2 slope is `-b2`.
- Cancellation depends on covariance-weighted terms (`G1 b1` vs `G2 b2`), not raw vector negation.
- If `G1 != G2` (different regime geometry), then the balancing solution is generally not `b2 = b1` or `b2 = -b1`.

Only in special cases (e.g., matched Gram structure) do simple equal/opposite coefficient relations hold exactly.
