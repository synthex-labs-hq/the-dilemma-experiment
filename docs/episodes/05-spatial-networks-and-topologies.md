# The Dilemma Experiment: Can Cooperation Survive?

## Episode 5 — Spatial Networks & Topologies

![The Dilemma Experiment: Spatial Networks & Topologies](images/ep5_hashnode_cover.jpg)

### Opening question

In Episodes 1 through 4, our computational society operated under a fundamental assumption:
**The well-mixed soup.**

Every agent was assumed to have an equal probability of bumping into and interacting with every other agent in the population. In Episode 4, we saw the brutal consequences of this assumption:
- 50 Altruists placed in a room with 50 Predators were slaughtered in 5 generations.
- Lone cooperators in a bad neighborhood could never survive because they were diluted across a sea of parasites.
- Cooperation could only conquer if it was artificially seeded with a massive initial cluster (20%+).

In reality, neither bacteria, trees, animals, human settlements, nor distributed microservices operate in a well-mixed soup.

We live in **geographies**. We interact with our physical neighbors, our local network nodes, and our immediate organizational teams.

> What happens when interactions are confined to spatial lattices and network topologies?
> Can the simple geometry of geography protect trust from contagious exploitation?

To find out, in **Episode 5**, we moved our agents out of the primordial soup and placed them onto **2D Toroidal Spatial Lattices** and **Complex Network Topologies**.

---

### The geometry of the fortress: Spatial Lattices (ADR-019)

In spatial evolutionary game theory (Martin Nowak & Robert May 1992 *Nature*, Francisco Santos & Jorge Pacheco 2005 *PRL*), agents occupy discrete nodes on a spatial structure $\mathcal{G} = (\mathcal{V}, \mathcal{E})$.

Instead of an all-to-all tournament ($K_N$), an agent at node $u$ interacts strictly with its topological neighbors $\mathcal{N}(u)$:

```text
+-------------------------------------------------------------------------+
|                  2D Toroidal Lattice (Moore Neighborhood)               |
|                                                                         |
|                       [u_NW]     [u_N]      [u_NE]                      |
|                                \   |   /                                |
|                       [u_W]  ─── [ u ] ───  [u_E]                       |
|                                /   |   \                                |
|                       [u_SW]     [u_S]      [u_SE]                      |
|                                                                         |
|         Periodic Boundary Conditions: x' = x % W , y' = y % H           |
|                No artificial edge borders or corner dead-ends           |
+------------------------------------+------------------------------------+
```

In our domain architecture ([ADR-019](file:///home/vayana/Desktop/personal/projects/synthex/the-dilemma-experiment/docs/adr/019-spatial-topology-abstraction.md)), we implemented two primary spatial geometries:
1. **`ToroidalGrid2D`**: A regular 2D lattice wrapped around a torus (periodic boundaries). We support both **Von Neumann** (4 orthogonal neighbors) and **Moore** (8 surrounding neighbors) rules.
2. **`NetworkGraph`**: Arbitrary complex network graphs supporting **Small-World networks** (Watts-Strogatz with rewiring parameter $\beta$) and **Scale-Free networks** (Barabási-Albert preferential attachment).

---

### Local imitation dynamics: How spatial societies evolve (ADR-020)

How do strategies reproduce across a spatial grid?

Unlike global Replicator Dynamics (where total wealth dictates a global birth quota), reproduction in spatial games follows **Local Imitation Dynamics** (Nowak-May 1992):

```text
+-------------------------------------------------------------------------+
|                  Generation t: Local Interaction Phase                  |
|     Every edge (u, v) executes an atomic Match between node u and v     |
|      Scores accumulated locally: S(u) = Sum_{v in N(u)} MatchScore      |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                Synchronous Local Imitation (ADR-020)                    |
|                                                                         |
|     For each node u:                                                    |
|     1. Candidate set: C(u) = Neighbors(u) + {u}                         |
|     2. Inspect the fitness of all candidates in C(u)                     |
|     3. Node u adopts the strategy of the highest-scoring candidate:     |
|                                                                         |
|            Strategy(u, t+1) = Strategy( argmax_{c in C(u)} Score(c) )    |
|                                                                         |
|     Inertia Rule: If u's current strategy ties for highest, retain it   |
+------------------------------------+------------------------------------+
```

This local dynamic creates an extraordinary evolutionary phenomenon: **The Fortress Effect**.

---

### Experiment A: The Altruist Fortress (Surviving without Retaliation)

In Episode 4, we paired pure Altruists (`AlwaysCooperate`) against pure Predators (`AlwaysDefect`). Without retaliation, Altruists were wiped out to absolute extinction in just 5 generations.

In Episode 5, we tested the exact same matchup on a $20 \times 20$ Toroidal Moore Grid ($N = 400$ agents).
We seeded the grid with **391 Predators (97.75%)** and planted a tiny $3 \times 3$ cluster of **9 Altruists (2.25%)** at the center.

#### The Result:
In the well-mixed soup, 2.25% Altruists would die in round 1.
On the 2D spatial grid: **The Altruist Fortress held its boundary indefinitely.**

| Metric | Well-Mixed Soup (Episode 4) | 2D Spatial Lattice (Episode 5) |
| :--- | :--- | :--- |
| **Initial Altruists** | 9 agents (2.25%) | 9 agents (2.25%) |
| **Generation 1** | Extinction collapse | **9 agents (Fortress intact)** |
| **Generation 5** | Extinct (0) | **9 agents (Fortress intact)** |
| **Generation 15** | Extinct (0) | **9 agents (Fortress intact)** |
| **Cooperator Clustering Ratio** | 0.022 | **0.667 (Clustered defense)** |

#### Why did the Fortress survive?
Look at the local mathematics:
1. **The Center Cooperator**: Surrounded exclusively by 8 fellow cooperators. In every round, it earns mutual cooperation dividends: $8 \times 3 = +24\text{ pts}$.
2. **The Boundary Cooperator**: Shares edges with 5 cooperators and 3 exterior predators. It earns $5 \times 3 + 3 \times 0 = +15\text{ pts}$.
3. **The Exterior Predator**: Directly adjacent to 3 boundary cooperators, but surrounded by 5 fellow predators. It exploits the 3 cooperators ($3 \times 5 = 15$) and interacts with defectors ($5 \times 1 = 5$), achieving a total score of $+20\text{ pts}$.

When the boundary cooperator looks around to see who to imitate, it sees the exterior predator ($+20$), but it ALSO sees the center cooperator ($+24$).
Because $24 > 20$, the boundary cooperator **retains its cooperation**! The center cooperator's mutual wealth anchors the entire perimeter.

---

### Experiment B: Reciprocal Spatial Expansion (Tit-for-Tat Conquers the World)

While pure Altruists can defend their territory, they cannot expand against predators because they do not retaliate.

What happens when we replace the $3 \times 3$ seed with **`TitForTatStrategy`** (reciprocal enforcers) on a 400-node lattice with 5 repeated interaction rounds?

```text
Generation 0:  [·····███·····]  TFT =   9 / 400 (  2.2%)  Seed planted
Generation 1:  [····█████····]  TFT =  25 / 400 (  6.2%)  Perimeter converts
Generation 2:  [···███████···]  TFT =  49 / 400 ( 12.2%)  Outward wave front
Generation 3:  [··█████████··]  TFT =  81 / 400 ( 20.2%)  Accelerating frontier
Generation 4:  [·███████████·]  TFT = 121 / 400 ( 30.2%)  Predator collapse
Generation 6:  [█████████████]  TFT = 225 / 400 ( 56.2%)  Majority conquest
Generation 9:  [█████████████]  TFT = 400 / 400 (100.0%)  Total Fixation!
```

In 9 generations, **a 2.25% minority conquered 100% of the world**.

Why did Tit-for-Tat expand while Altruists merely held their ground?
Because when an exterior predator interacts with Tit-for-Tat over 5 rounds, it gets $+5$ on round 1, but is immediately punished with mutual defection on rounds 2 through 5 ($+1 \times 4 = +4$, total $+9$).
Meanwhile, interior Tit-for-Tat agents reap mutual trust on all 5 rounds ($+15 \times 8 = +120$).
The exterior predators see that the reciprocal cooperators are vastly wealthier than themselves.
**The predators imitate the cooperators.** Trust spreads outward like an expanding crystal.

---

### Experiment C: The Small-World Infection (When Shortcuts Destroy Boundaries)

Real networks are rarely pristine 2D grids. In modern human societies, social media, and distributed microservices, systems resemble **Small-World Networks** (Duncan Watts & Steven Strogatz 1998): mostly local connections, punctuated by random long-range "shortcuts".

We tested how adding a rewiring probability $\beta \in [0.0, 0.5]$ impacts the survival of a 20% cooperative cluster in a 100-node network:

```text
+-------------------------------------------------------------------------+
|                  Small-World Rewiring vs Cooperator Survival            |
|                                                                         |
|  Beta = 0.00 (Pure Lattice, 0% shortcuts):     TFT Survival = 100.0%    |
|  Beta = 0.05 (Rare shortcuts, 5% shortcuts):   TFT Survival = 100.0%    |
|  Beta = 0.10 (Small-World regime, 10% short):  TFT Survival = 100.0%    |
|  Beta = 0.25 (High shortcut density):          TFT Leaked / Breached    |
|  Beta = 0.50 (Random graph regime):            Cluster Disintegrated    |
+-------------------------------------------------------------------------+
```

#### The Takeaway:
Local geography is a natural firewall.
When shortcuts are rare, clusters remain insulated and can organize their defense.
When long-range shortcuts become dense ($\beta > 0.2$), defector pathogens can bypass the defensive perimeter and strike directly into the vulnerable interior, unraveling social trust.

---

### Architectural highlights

1. **Pure Python & Zero External Dependencies ([ADR-006](file:///home/vayana/Desktop/personal/projects/synthex/the-dilemma-experiment/docs/adr/006-standard-library-first.md), [ADR-019](file:///home/vayana/Desktop/personal/projects/synthex/the-dilemma-experiment/docs/adr/019-spatial-topology-abstraction.md))**:
   - `ToroidalGrid2D` and `NetworkGraph` are built exclusively with standard Python 3.12 dataclasses. Zero dependencies on heavy graph libraries.
2. **Symmetric Edge Scheduling ([ADR-020](file:///home/vayana/Desktop/personal/projects/synthex/the-dilemma-experiment/docs/adr/020-spatial-tournament-and-local-imitation.md))**:
   - Each unique undirected edge $\{u, v\}$ is evaluated exactly once per generation, guaranteeing computational speed and deterministic consistency.
3. **Synchronous Double-Buffering**:
   - Generational transitions are atomic and double-buffered, eliminating sequential in-place update bias.
4. **139 Passing Unit Tests**:
   - Full suite executed in 0.52 seconds with zero mocks.

---

### What's Next: Episode 6 — Indirect Reciprocity, Reputation & Gossip

In Episode 5, we solved the problem of scale by giving agents **physical neighbors**.

In **Episode 6**, we tackle an even harder question:
*How do you build trust when you never meet the same stranger twice?*

Direct reciprocity requires repeated interactions. In large-scale markets and modern cities, transactions are mostly one-shot encounters between strangers.
In Episode 6, we will build:
- **Public Image Scoring Registers** (Martin Nowak & Karl Sigmund's Indirect Reciprocity).
- **Gossip Communication Channels** with transmission noise and misinformation.
- **The Hypocrite Archetype**: Agents that play holy in public and defect in the shadows.

---

### A note from the builder

*The Dilemma Experiment is built manually, incrementally, and transparently.*

*Every architectural choice is documented via Architecture Decision Records under `docs/adr/`, verified with zero-mock behavioral unit tests, and committed with conventional commit history.*

*Follow the project development on GitHub: [synthex-labs-hq/the-dilemma-experiment](https://github.com/synthex-labs-hq/the-dilemma-experiment).*
