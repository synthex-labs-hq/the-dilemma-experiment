# ADR 028: Extortion, Equalizers, and Generous ZD Dynamics

## Context
Within the general family of Zero-Determinant strategies ($\alpha s_X + \beta s_Y + \gamma = 0$), two distinct classes have profound implications for social dilemmas and economic power:
1. **Extortioner Strategies ($\chi \ge 1$)**:
   - Enforce the linear contract:
     $$(s_X - P) = \chi (s_Y - P)$$
     where $P$ is the mutual defection payoff (baseline) and $\chi > 1$ is the extortion coefficient.
   - The extortioner guarantees that for every unit of payoff the opponent earns above $P$, the extortioner earns $\chi$ units.
   - Crucially, the opponent's best response to an extortioner is full cooperation, because defecting yields only $P = 1$, whereas cooperating yields $s_Y > 1$ (even though the extortioner reaps a far greater share).
2. **Equalizer Strategies ($s_Y = c$)**:
   - Set $\alpha = 0, \beta = 1, \gamma = -c$.
   - Unilaterally fix the co-player's expected score to a predetermined constant $c \in [P, R]$, rendering the co-player's actions completely irrelevant to their own long-term payoff.
3. **Generous ZD Strategies (Stewart & Plotkin 2012, 2013)**:
   - Anchor the linear relation at the mutual cooperation payoff $R$:
     $$(s_X - R) = \chi (s_Y - R) \quad (\chi \ge 1)$$
   - Ensures $p_{CC} = 1$ and $p_{DD} > 0$. If the co-player cooperates, both achieve $(R, R) = (3, 3)$. If defection occurs, the generous agent absorbs a disproportionate loss to incentivize forgiveness and protect cooperation against noise.

## Decision
We implement three canonical ZD strategy archetypes in `src/the_dilemma_experiment/strategies/zero_determinant.py`:
1. `ExtortionStrategy(chi: float = 3.0, phi: float | None = None)`:
   - Automatically computes optimal Press-Dyson scaling factor $\phi = \frac{1}{(P - S) + \chi(T - P)}$.
   - Yields valid probabilities $p \in [0, 1]^4$ with $p_{DD} = 0$.
2. `EqualizerStrategy(target_score: float = 2.0, phi: float | None = None)`:
   - Valid for target score $c \in [P, R]$.
   - Unilaterally pins opponent's expected payoff to $c$.
3. `GenerousZDStrategy(chi: float = 2.0, phi: float | None = None)`:
   - Stewart-Plotkin compliant cooperator anchored at $R$.
   - Promotes evolutionary stability of mutual cooperation.

## Consequences
- **Pros**:
  - Uncovers the asymmetry between individual pairwise dominance and evolutionary population fitness.
  - Extortioners win every head-to-head match ($s_X \ge s_Y$), but crash in evolutionary populations because mutual extortion yields $(P, P) = (1, 1)$.
  - Explains how asymmetric power operates in distributed bargaining, cloud scheduling, and predatory pricing.
- **Cons**:
  - Floating point stochastic sampling in finite round matches exhibits variance around the theoretical line; resolved by providing both deterministic Markov solvers and empirical Monte Carlo matches.
