# Classical Inference Clarification C-001

**Status:** Frozen operational clarification for Stage III validation.

Stage I requires market-model classical inference to account for parameter-estimation uncertainty. For a market-model estimation sample with design matrix `X_est = [1, R_m]`, residual variance `s^2 = RSS/(n-2)`, and an event window with `m` observations and event design matrix `X_evt`, EFL v0.1 defines the classical CAR predictive variance as

`Var_hat(CAR | X) = s^2 * [m + x_sum' (X_est' X_est)^(-1) x_sum]`,

where `x_sum = X_evt' 1_m`.

Equivalently, in simple-regression scalar form,

`Var_hat(CAR | X) = s^2 * [m + m^2/n + (sum(R_m,event) - m*mean(R_m,est))^2 / Sxx_est]`.

The classical statistic is

`t = CAR / sqrt(Var_hat(CAR | X))`,

with `df = n - 2` and a two-sided Student-t p-value under the maintained normal, independent, homoskedastic market-model disturbances.

This is not the permutation statistic. The Nguyen-Wolf permutation statistic retains its own definition `CAR/(sqrt(m)*s_n)` and assumptions.

## Why this clarification exists

MacKinlay (1997) explicitly shows that out-of-sample abnormal-return variance contains both disturbance variance and additional parameter-estimation variance, and notes that parameter estimation also induces covariance across event-window abnormal returns. The matrix expression above carries those terms through to the sum defining CAR rather than discarding them.

## Validation

`INF-001` is computed independently using (1) the scalar simple-regression expression and (2) the general matrix predictive-covariance expression. The two agree within `1e-15` in the Stage III reference environment.
