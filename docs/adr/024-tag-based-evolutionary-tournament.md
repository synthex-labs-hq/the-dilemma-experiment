# ADR-024: Tag-Based Evolutionary Tournament and Tolerance Dynamics

## Status
Accepted

## Context
A central question raised by Dawkins (1976) and subsequent game theorists (Roberts & Sherratt 2002) is: **Why don't "false-beards" immediately destroy tag-based cooperation?**

A "false-beard" is a mutant that displays the green beard (tag) but possesses a defector strategy. In a static game, false-beards earn the maximum temptation payoff $T=5$, driving cooperators extinct.

However, Riolo, Cohen, and Axelrod (2001) demonstrated that in a dynamic evolutionary population where both tags $\tau$ and tolerance thresholds $T$ mutate independently:
1. When a tag cluster forms, mutual cooperation raises its fitness.
2. Cooperators drift toward higher tolerance $T$, expanding the cooperative umbrella.
3. Once tolerance is high, a mutant with a nearby tag that defects (a false-beard) invades and reaps enormous payoffs.
4. As the cluster's fitness collapses, low-tolerance individuals surviving on the periphery abandon the compromised tag or evolve a new tag $\tau'$, starting a new cooperative cycle.

This creates cyclical boom-and-bust dynamics: cooperation does not settle into a static point, but perpetually reinvents itself across the tag landscape.

## Decision
1. **Evolutionary Engine**:
   - Implement `TagEvolutionaryTournament` operating across discrete generations $g = 1, \dots, G$.
   - Agents are paired for stranger interactions in each generation.
   - Payoffs determine reproduction probability via fitness-proportional roulette or rank-based selection.
2. **Mutation Mechanics**:
   - Tag mutation: with probability $\mu_\tau$, $\tau' = (\tau + \mathcal{N}(0, \sigma_\tau)) \pmod{1.0}$.
   - Tolerance mutation: with probability $\mu_T$, $T' = \max(0.0, T + \mathcal{N}(0, \sigma_T))$.
3. **Telemetry & Metrics**:
   - Track average system cooperation rate per generation.
   - Track mean and variance of tolerance $\bar{T}$.
   - Calculate Shannon diversity index of tag distributions: $H = -\sum p_k \ln p_k$.
   - Classify interactions into *In-Group* ($d \le T$) vs *Out-Group* ($d > T$) encounters.

## Consequences
- Accurately reproduces the Riolo et al. (2001) empirical findings in Python.
- Provides quantitative telemetry for video visualizations and screencasts.
- Exposes the fundamental fragility and resilience of tribal stratification.
