# ADR-023: Arbitrary Surface Tags and Tolerance-Based Discrimination

## Status
Accepted

## Context
In previous episodes, cooperation was sustained through direct reciprocity (memory of past dyadic interactions, Episodes 1–3), natural selection (Episode 4), spatial clustering (Episode 5), and indirect reciprocity via public image scoring ledgers (Episode 6).

However, in many biological and socio-technical settings, agents possess neither past interaction history nor access to a shared global reputation registry. Instead, agents observe superficial, observable markers ("tags") carried by their peers—such as visual pigmentation, dialect, clothing, digital signatures, certificates, or protocol headers.

In 2001, Rick L. Riolo, Michael D. Cohen, and Robert Axelrod published a landmark paper in *Nature* (*"Evolution of cooperation without reciprocity"*), demonstrating that cooperation can spontaneously emerge when agents pair an arbitrary surface tag $\tau \in [0, 1]$ with a tolerance threshold $T \ge 0$. Under this model, an agent cooperates with a stranger if and only if the distance between their tags does not exceed its tolerance:

$$d(\tau_i, \tau_j) = |\tau_i - \tau_j| \le T_i$$

This mechanism is closely tied to the **Green-Beard Effect** (Hamilton 1964; Dawkins 1976), where an observable phenotypic marker acts as a proxy for cooperative intent.

## Decision
1. **Domain Representation**:
   - Define a `Tag` abstraction supporting continuous scalar tags $\tau \in [0.0, 1.0]$ and discrete categorical tags $\tau \in \mathcal{C}$ (e.g., `"RED"`, `"BLUE"`, `"GREEN"`).
   - Define distance functions:
     - Continuous: $d(\tau_1, \tau_2) = |\tau_1 - \tau_2|$ (or circular distance on a 1D torus if wrap-around is enabled).
     - Categorical: $d(\tau_1, \tau_2) = 0.0$ if $\tau_1 == \tau_2$ else $1.0$.
2. **Context Extension**:
   - Enhance `DecisionContext` with optional `opponent_tag` and `self_tag` fields, preserving full backwards compatibility with all previous strategies.
3. **Strategy Implementations**:
   - `RioloToleranceStrategy`: Continuous tag $\tau$ with tolerance $T$. Cooperates if distance $d \le T$.
   - `StrictTribalStrategy`: Discrete categorical tag. Cooperates unconditionally with in-group peers ($\tau_{\text{self}} == \tau_{\text{opp}}$), defects against out-group peers.
   - `FalseBeardStrategy`: Displays a cooperative/majority tag to attract altruistic donations from tolerant peers, but defects unconditionally to extract maximum payoffs.
   - `UniversalAltruistTagStrategy` ($T = \infty$) and `UniversalEgoistTagStrategy` ($T = -1.0$).

## Consequences
- **Zero Memory Overhead**: Agents make decisions in $O(1)$ time without maintaining interaction logs or querying external databases.
- **In-Group Favoritism**: Models how arbitrary markers partition a population into cooperative tribes and hostile out-groups.
- **Cheat Vulnerability**: Exposes the system to false-beard invaders, motivating evolutionary analysis in ADR-024.
