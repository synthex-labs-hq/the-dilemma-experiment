# ADR 027: Zero-Determinant Memory-One Strategies and Markov Invariants

## Context
In 2012, theoretical physicist Freeman J. Dyson and mathematician William H. Press published a landmark discovery in the *Proceedings of the National Academy of Sciences* (PNAS): *"Iterated Prisoner's Dilemma contains strategies that dominate any evolutionary opponent"*.

Prior to Press and Dyson's proof, game theory literature widely assumed that:
1. Symmetric games with memory produce mutual outcomes where no single player can unilaterally enforce a relationship between payoffs.
2. An opponent possessing longer memory could always outwit an opponent with shorter memory.

Press and Dyson overturned both assumptions by proving the existence of **Zero-Determinant (ZD) strategies**:
- A player playing a **memory-one** strategy—conditioned only on the immediate outcome of the previous round—can unilaterally enforce a linear relation between their own expected payoff $s_X$ and their co-player's expected payoff $s_Y$:
  $$\alpha s_X + \beta s_Y + \gamma = 0$$
- This mathematical relationship holds regardless of the co-player's strategy, memory length, computational power, or adaptive heuristics.

## Decision
We implement a zero-mock Markov domain architecture for memory-one strategies and Zero-Determinant mechanisms:
1. **`MemoryOneStrategy` Abstract Base**:
   - Parameterized by the four-tuple of conditional cooperation probabilities:
     $$\mathbf{p} = (p_{CC}, p_{CD}, p_{DC}, p_{DD})$$
     where $p_{ab} = P(X = \text{COOPERATE} \mid X_{\text{prev}} = a, Y_{\text{prev}} = b)$.
   - Parameterized by initial move $p_0 \in [0.0, 1.0]$.
   - Implements the standard `Strategy` interface (`make_action(history, context)`).
2. **Markov Chain & Stationary Distribution Engine**:
   - Pure Python standard library implementation of 4x4 Markov transition matrix $M(p, q)$.
   - Gaussian elimination solver for the stationary distribution $\mathbf{v} M = \mathbf{v}$, $\sum v_i = 1$.
   - Exact analytical expected payoff calculator for theoretical benchmarks without relying on empirical Monte Carlo variance.

## Consequences
- **Pros**:
  - Provides mathematical ground truth for theoretical validation.
  - Zero external dependencies (no NumPy/SciPy requirement).
  - Enables exact verification of Press-Dyson invariant determinants in unit tests.
- **Cons**:
  - Requires handling edge cases where the transition matrix has non-unique stationary components (absorbing defection states). Handled via standard regularization or tie-breaking pivots.
