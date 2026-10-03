# ADR-017: Replicator Dynamics and Generational Evolution Model

## Status

Accepted

## Context

In Episodes 1 through 3, tournament populations were static: the experimenter chose an initial roster of agents, and that roster remained fixed for the duration of the tournament. Neither birth, death, reproduction, nor generational adaptation existed.

In evolutionary game theory (John Maynard Smith 1982, Peter Taylor & Leo Jonker 1978, Robert Axelrod 1984), populations evolve over successive generations according to **Replicator Dynamics**:
- Strategies that achieve above-average fitness multiply and expand their demographic share.
- Strategies that achieve below-average fitness contract and face ecological extinction.

To simulate evolutionary natural selection, we need a formal, deterministic, discrete replicator model that:
1. Operates over discrete generations of finite multi-agent populations.
2. Maintains a strictly constant carrying capacity ($N$, e.g., $N=100$ agents).
3. Evaluates fitness empirically from round-robin tournaments executed in each generation.
4. Allocates discrete integer offspring counts without demographic leakage, fractional drift, or non-deterministic rounding bias.
5. Fully respects agent and strategy instance isolation (ADR-001, ADR-010, ADR-011, ADR-014).

## Decision

1. **Carrying Capacity ($N$) and Generation Population**:
   - The total population size $N = \sum_{i=1}^K N_i(t)$ is invariant across all generations $t \ge 0$, representing the environmental carrying capacity.
   - At generation $t$, each active strategy archetype $i \in \{1, \dots, K\}$ possesses $N_i(t) \ge 0$ individual agents.
   - For each generation $t$, every individual agent is instantiated with a fresh, isolated `Strategy` instance per ADR-010 and ADR-011.

2. **Empirical Generation Fitness**:
   - In generation $t$, a complete round-robin `Tournament` is executed across all $N$ agents.
   - Each agent accumulates an empirical total tournament score.
   - The strategy fitness $W_i(t)$ is the mean total score earned by agents of strategy $i$:
     $$W_i(t) = \frac{\sum_{a \in \text{Agents}_i} \text{TotalScore}(a)}{N_i(t)}$$
   - The total score earned across the entire population is:
     $$T_{\text{pop}}(t) = \sum_{i=1}^K N_i(t) W_i(t)$$
   - The population mean fitness per agent is:
     $$\bar{W}(t) = \frac{T_{\text{pop}}(t)}{N}$$

3. **Replicator Proportion and Offspring Quota**:
   - The unrounded expected offspring count for strategy $i$ in generation $t+1$ follows the standard discrete replicator dynamic:
     $$N_i'(t+1) = N_i(t) \cdot \frac{W_i(t)}{\bar{W}(t)} = N \cdot \frac{N_i(t) W_i(t)}{T_{\text{pop}}(t)}$$
   - If $T_{\text{pop}}(t) = 0$ (all agents earned 0), populations remain unchanged: $N_i'(t+1) = N_i(t)$.

4. **Discrete Integer Seat Allocation (Largest Remainder Method / Hamilton-Hare)**:
   - Because agents are discrete entities, fractional offspring must be converted to integers summing to exactly $N$.
   - For each active strategy:
     - Compute base integer seats: $k_i = \lfloor N_i'(t+1) \rfloor$.
     - Compute remainder: $r_i = N_i'(t+1) - k_i$.
   - Calculate remaining unassigned seats: $R = N - \sum_{i=1}^K k_i$.
   - Distribute the $R$ seats one-by-one to strategies in descending order of remainder $r_i$.
   - Ties in $r_i$ are broken deterministically by strategy archetype name alphabetically.
   - This guarantees $\sum_{i=1}^K N_i(t+1) = N$ with zero rounding drift.

5. **Extinction Mechanics and Absorbing States**:
   - If $N_i(t+1) = 0$, strategy $i$ is declared extinct.
   - Extinct strategies cannot play matches, earn fitness, or reproduce in subsequent generations (extinction is absorbing).
   - If only one strategy survives ($N_{\text{survivor}} = N$), fixation is reached: the population is homogeneous, and the simulation converges.

## Consequences

### Positive
- Exact conservation of population size ($N$ is constant across all generations).
- Deterministic, mathematically rigorous discrete replicator dynamics without heuristic approximations.
- Integrates seamlessly with existing `Tournament`, `Match`, and `Population` abstractions.
- Completely reproducible under deterministic seeds (ADR-003).

### Negative / Trade-offs
- Executing a full round-robin tournament for large populations (e.g. $N > 200$) across hundreds of generations requires quadratic match evaluations. (Mitigated by our sub-second benchmark of $4,950$ matches in $\sim 0.27\text{s}$).
