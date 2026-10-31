# ADR 030: Cognitive Personas and Provider-Agnostic LLM Client Architecture

## Context
Integrating Large Language Models into a scientific simulation framework presents three key engineering challenges:
1. **Zero-Mock & Offline Reproducibility**: The codebase must guarantee 100% deterministic test execution in CI/CD without mandatory API keys, external network latency, or variable billing.
2. **Support for Frontier Production Models**: When API credentials are provided (e.g. `GEMINI_API_KEY`), the simulation must seamlessly execute using Google Gemini models (e.g., `gemini-3.7-flash`, `gemini-2.5-flash`) via the modern `google-genai` SDK.
3. **Cognitive Persona Diversity**: Societal simulations require diverse agent personalities—from naive idealists and unbending pragmatists to Machiavellian manipulators and cynical realists.

## Decision
We implement a decoupled provider-agnostic client architecture:
1. **`LLMProviderProtocol` (Abstract Contract)**:
   - `generate_message(system_prompt: str, conversation_history: list[dict], round_info: dict) -> str`
   - `decide_action(system_prompt: str, conversation_history: list[dict], match_history: list[dict], round_info: dict) -> tuple[Action, str]`
2. **`SimulatedCognitiveClient` (Zero-Mock Native Provider)**:
   - Built-in, zero-dependency cognitive engine supporting four distinct persona profiles:
     - `HonestDiplomat`: Strives for mutual cooperation, communicates transparently, keeps promises, forgives once upon genuine apology.
     - `Machiavellian`: Employs persuasive, sycophantic rhetoric in chat to coax cooperation, while exploiting opportunities to defect.
     - `PragmaticContractor`: Forms conditional pacts ("I will cooperate if and only if you cooperate"), auditing actions strictly against words.
     - `SkepticalRealist`: Dismisses dialogue as cheap talk, relying exclusively on physical action history to dictate moves.
   - Generates natural, dynamic dialogue and decisions deterministically (or seeded pseudo-randomly).
3. **`GeminiLLMClient` (Live Frontier Model Provider)**:
   - Uses the official `google-genai` SDK when available and configured.
   - Formats structured system instructions, conversation turns, and game telemetry into Gemini prompt contexts.
4. **`CognitiveStrategy`**:
   - Implements the core `Strategy` interface.
   - Pluggable into standard `Tournament`, `SpatialTournament`, or `CognitiveTournament`.

## Consequences
- **Pros**:
  - Full adherence to zero-mock testing: all unit tests run in <1 second with zero network dependency.
  - Users can test live Gemini models by simply setting `GEMINI_API_KEY`.
  - Enables scientific comparison between LLM cognitive reasoning and classic game-theoretic benchmarks.
- **Cons**:
  - Live API inference incurs network latency and token costs; mitigated by keeping offline simulated clients as default for automated benchmarks.
