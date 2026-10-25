# ADR-022: Second-Order Moral Systems, Gossip Channels, and Observation Uncertainty

## Status

Accepted

## Context

Under first-order image scoring (ADR-021), an agent's reputation depends solely on its action: Cooperate $\to +1$, Defect $\to -1$.

This produces the **Enforcer's Dilemma (The Moral Paradox of Punishment)**:
- If a cooperative agent encounters a known predator, it must defect to avoid being exploited.
- But in a first-order system, that necessary defection drops the agent's image score by $-1$.
- Consequently, righteous enforcers look indistinguishable from unprovoked predators. This destroys trust and leaves society vulnerable to invasion by free-riders.

In evolutionary social biology (Hisashi Ohtsuki & Yoh Iwasa 2006 *Journal of Theoretical Biology*, Martin Nowak & Karl Sigmund 2005 *Nature*):
1. Stable indirect reciprocity requires **Second-Order Assessment (Stern Judging)**: an action's morality depends on the *recipient's* moral standing.
2. Defecting against a "bad" agent is **righteous punishment** and maintains or restores the punisher's "GOOD" standing.
3. In realistic human and decentralized systems, information does not arrive via an infallible central oracle; it propagates via **Gossip Channels** subject to transmission noise, misinterpretation, and deception.

## Decision

1. **Second-Order Moral Assessment (`SternJudging`)**:
   - Each agent possesses a binary moral standing: `MoralStanding.GOOD` (1) or `MoralStanding.BAD` (0).
   - When donor $u$ takes action $A \in \{\text{COOPERATE}, \text{DEFECT}\}$ against recipient $v$ with standing $S_v \in \{\text{GOOD}, \text{BAD}\}$, the donor's new standing $S_u'$ transitions according to the Stern Judging matrix:

| Donor Action | Recipient Standing ($S_v$) | New Donor Standing ($S_u'$) | Social Interpretation |
| :--- | :--- | :--- | :--- |
| **COOPERATE** | `GOOD` | **`GOOD`** | Mutual aid among trustworthy citizens |
| **DEFECT** | `GOOD` | **`BAD`** | Unprovoked betrayal / predatory exploitation |
| **COOPERATE** | `BAD` | **`BAD`** | Appeasing / rewarding a known parasite |
| **DEFECT** | `BAD` | **`GOOD`** | Righteous social sanction / justified punishment |

2. **Gossip Channel with Observation Uncertainty (`GossipChannel`)**:
   - In decentralized settings, agents transmit reputation reports to peers.
   - Channel error probability $\gamma \in [0.0, 1.0]$:
     - With probability $1 - \gamma$, the true standing $S_v$ is transmitted accurately.
     - With probability $\gamma$, transmission noise or malicious rumors invert the reported standing ($S_v' = \neg S_v$).
   - Gossip reports are seeded deterministically per ADR-003.

3. **Behavioral Archetypes for Indirect Reciprocity**:
   - **`ImageScorerStrategy`**: First-order discriminator. Cooperates if opponent's public score $q \ge \theta$; otherwise defects.
   - **`SternJudgingStrategy`**: Second-order discriminator. Cooperates if opponent is `GOOD`; defects (righteous punishment) if opponent is `BAD`.
   - **`HypocriteStrategy`**: Observational opportunist. Inspects whether the match is observed (`is_public`):
     - If public: Cooperates to artificially inflate its score and fool the community.
     - If private: Defects to maximize exploitation without social penalty.

## Consequences

### Positive
- Completely resolves the Enforcer's Dilemma: enforcers can punish defectors without tarnishing their own social standing.
- Models the evolutionary emergence of justice, moral norms, and social sanctions.
- Enables empirical study of how information noise ($\gamma$) and hypocrisy degrade or maintain systemic trust.

### Negative / Trade-offs
- Second-order assessment requires tracking both the donor's action and the recipient's prior standing, requiring richer decision contexts.
