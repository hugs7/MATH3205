# Markowitz or Mean/Variance Models

## Sets

$N$ assets we want to invest in

## Data

$r_i$ return on asset $i \in N$
Typically these are slightly greater than 1.

$W$ Covariance Matrix

We assume the returns have a multivariate normal distribution

## Variables

$x_i$ is the fraction of our portfolio investged in each asset

## Maximise return

$$
\max (\lambda \sum_{i\in N} r_i x_i - (1-\lambda) x^T w X)
$$

with
$\lambda \in (0,1)$

subject to

$$\sum_{i\in N} x_i = 1$$

---

## General second order cone constraint

$$\boldsymbol{x}^\top W \boldsymbol{x} \le z$$

Where $x\ge 0$ and $z \ge 0$ are variables and $W$ is a positive semi-definite matrix.

Gurobi can do second order cone constraints because the Barrier algorithm turns regular constraints into these.
Solvable in polynomial time

---

Value at Risk and Conditional Value at Risk
(VaR) (CVaR)

Sample average approximation (SAA)

Assume we want VaR and CVaR at the $\alpha$ level (e.g. the bottom $5\%$).

Sets
$S$ samples

Data
$r_{is}$ return for investment $i \in N$ in sample $s \in S$

Variables

-   $\beta_s$ return of sample $s \in S$.
-   $\text{Var}$ estimate of VaR from samples
-   $\text{CVar}$ estimate of CVaR from samples
-   $\beta^{-}$ the amount by which the return of scenario $s \in S$ is below $\text{Var}$

Objective

$$ \max \frac{\lambda}{|S|} \sum\_{s \in S}\beta_s + (1 - \lambda)\text{CVar} $$

Subject to

$$ \sum\_{i\in N} x_i = 1 $$

$$ \beta*s = \sum*{ i \in N } r\_{is} X_i, \hspace{1cm} \forall s \in S $$

$$ \beta_s + \beta_s^{-} \ge \text{Var}, \hspace{1cm} \forall s \ in S $$

$$ \text{CVar} = \text{Var} - \frac{1}{\alpha |S|} \sum\_{s \in S} \beta^{-} $$

---

Chance constrained portfolio Models
$$ \max \sum\_{i \in N} r_i x_i $$

Subject to

$$ \sum\_{i \in N} = 1 $$

Chance constraint for small values of $\alpha$

$$ \mathbb{P}\left(\sum\_{i \in N} r_i x_i \ge 1\right) \ge (1 - \alpha) $$

This turns into
$$ \left(F^{-1} \left(1 - \alpha \right)\right)^2 x^\top W x \le \left(1 - \sum\_{i \ in N} r_i x_i \right)^2 $$

What if the data is not normally distributed

We can generate a lot of samples.

Use Campi & Garatti formula to calculate $k$: the numnber of failures permitted for a given sample size $\alpha$ and degrees of freedom. Replace $W$ with the sample variance and $r$ with the sample average returns.

Treat $F^{-1}(1-\alpha)$ as a parameter above, and repeatedly solve and count the number of failures, aiming to get exactly $k$ failures (via line search/interpolation techniques).
