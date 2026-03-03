# Two-Mode Rotated Dataset Design

## Goal
Build a dataset with:
- 10 features
- mode 1 size = 750
- mode 2 size = 250
- two clearly separated clusters in `X`
- strongly rotated eigendirections between modes
- near-zero linear predictability when fitting one OLS model on pooled `X -> y`

## Geometry (how to position the two datasets)
1. Use two different covariance ellipsoids:
   - `Sigma1 = Q1 * diag(lambda1) * Q1^T`
   - `Sigma2 = Q2 * diag(lambda2) * Q2^T`
2. Make `Q2` a strong rotation of `Q1` using large Givens rotations in paired axes:
   - `(0,9): 82 deg`, `(1,8): 74 deg`, `(2,7): 67 deg`, `(3,6): 58 deg`, `(4,5): 49 deg`
3. Separate cluster means along different (nearly orthogonal) directions:
   - `mu1 = +sep * q1_1`
   - `mu2 = -sep * q2_1`
4. Build regime-specific responses from centered features:
   - `y1 = (X1 - mean(X1)) @ beta1 + eps1`
   - `y2 = -(X2 - mean(X2)) @ beta2 + eps2`
5. Choose `beta2` to cancel pooled linear covariance exactly (sample-level):
   - `beta2 = (X2c^T X2c)^(-1) (X1c^T X1c) beta1`
   - this enforces pooled OLS slope ~ 0 (with intercept), while each mode remains strongly linear.

## Why this works
- The two modes are separable in `X` because means are far apart.
- The mode ellipsoids are rotated against each other (large eigenvector angles).
- Signal direction flips by regime (`+` vs `-`), and the covariance-weighted balancing makes pooled linear signal cancel.
- A single linear model on pooled data fails, but per-mode models fit well.

## Implementation
Code file:
- [generate_two_mode_rotated.py](/Users/Shared/repos/hkrnk/hkdis/voleon/generate_two_mode_rotated.py)

Outputs produced by the script:
- [mode1_rotated.csv](/Users/Shared/repos/hkrnk/hkdis/voleon/mode1_rotated.csv)
- [mode2_rotated.csv](/Users/Shared/repos/hkrnk/hkdis/voleon/mode2_rotated.csv)
- [combined_rotated.csv](/Users/Shared/repos/hkrnk/hkdis/voleon/combined_rotated.csv)
- [beta_mode1.npy](/Users/Shared/repos/hkrnk/hkdis/voleon/beta_mode1.npy)
- [beta_mode2.npy](/Users/Shared/repos/hkrnk/hkdis/voleon/beta_mode2.npy)
- [cov_mode1.npy](/Users/Shared/repos/hkrnk/hkdis/voleon/cov_mode1.npy)
- [cov_mode2.npy](/Users/Shared/repos/hkrnk/hkdis/voleon/cov_mode2.npy)
- [eigvec_mode1.npy](/Users/Shared/repos/hkrnk/hkdis/voleon/eigvec_mode1.npy)
- [eigvec_mode2.npy](/Users/Shared/repos/hkrnk/hkdis/voleon/eigvec_mode2.npy)

Run command:
```bash
python /Users/Shared/repos/hkrnk/hkdis/voleon/generate_two_mode_rotated.py
```

## Generation record (seed=7)
- pooled `R^2`: `0.00000000`
- mode1 `R^2`: `0.95696181`
- mode2 `R^2`: `0.99926849`
- `||pooled beta||_2`: `2.860e-15`
- mode slope opposition corr (`b1` vs `-b2`): `0.5644`
- cluster center distance: `7.6900`
- cluster mean-direction angle: `98.00 deg`
- top-3 eigenspace principal angles: `[67, 74, 82] deg`
- eigenvector angles (index-wise): `[82, 74, 67, 58, 49, 49, 58, 67, 74, 82] deg`

## Note on constraints
This rotated-eigenspace construction prioritizes geometry and segmentation.  
If you need the stricter earlier constraint "every pairwise feature correlation in `[0, 0.2]`", use the simpler correlation-bounded generator (already created earlier), but that makes strong eigenvector rotation much harder.
