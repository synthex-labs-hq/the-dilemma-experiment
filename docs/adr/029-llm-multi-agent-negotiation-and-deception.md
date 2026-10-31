# ADR 029: LLM Multi-Agent Pre-Play Negotiation and Strategic Deception

## Context
In previous episodes (Episodes 1–9), all agents operated under fixed, symbolic, or mathematical decision rules (memory-one conditional probabilities, reputation registries, spatial graph topologies, or static heuristics). 

In human societies, biological swarms, and advanced multi-agent systems, agents possess cognitive agency:
1. **Natural Language Pre-Play Communication ("Cheap Talk")**: In classical game theory (Crawford & Sobel 1982, Farrell & Rabin 1996), non-binding communication without enforcement is called "cheap talk." In simple symmetric games, cheap talk is often dismissed as mathematically vacuous. However, in complex cognitive agents, pre-play dialogue establishes coordination focal points, clarifies intent, and builds psychological rapport.
2. **Strategic Deception ("The Machiavellian Index")**: A cognitive agent can leverage natural language strategically—promising unconditional cooperation during diplomatic talks to induce trust from a gullible partner, only to defect at the physical decision point to capture the $+5$ temptation payoff.
3. **Emergent Social Norms**: Over repeated rounds with persistent conversational memories, language-capable agents can develop shared diplomatic protocols, conditional contracts, apologies, and punitive gossip.

## Decision
We introduce a cognitive dialogue and negotiation architecture in `src/the_dilemma_experiment/domain/cognitive.py`:
1. **`DialogueTurn`**: Immutable record of an agent's conversational message, specifying round number, sender, recipient, natural language utterance, and inferred intent (`Action.COOPERATE`, `Action.DEFECT`, or neutral).
2. **`NegotiationChannel`**: Pre-play communication protocol allowing agents to exchange $K$ rounds of dialogue before each game round.
3. **`DeceptionTracker`**: An audit registry monitoring the delta between stated verbal commitments in chat and actual physical actions played in the Prisoner's Dilemma matrix.
   - Calculates `broken_promises`, `honesty_rate`, and `machiavellian_index`.
4. **`CognitiveMatch` & `CognitiveTournament`**: Match coordinators integrating pre-play negotiation, action resolution, and deception auditing.

## Consequences
- **Pros**:
  - Bridges mathematical game theory with frontier generative AI and agentic reasoning.
  - Quantifies deception, promise-keeping fidelity, and linguistic coordination.
  - Extensible to both frontier LLMs (Google Gemini) and offline deterministic cognitive models.
- **Cons**:
  - Pre-play dialogue adds conversational turns before every action; handled efficiently via clean structured data models.
