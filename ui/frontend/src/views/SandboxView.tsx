import React, { useState } from 'react'
import {
  simulateGauntlet,
  type GauntletDuelResult,
  type GauntletResponse,
} from '../api/client'

export const SandboxView: React.FC = () => {
  const [strategyName, setStrategyName] = useState<string>('NobleReciprocator')
  const [openingMove, setOpeningMove] = useState<'COOPERATE' | 'DEFECT'>('COOPERATE')
  const [forgiveness, setForgiveness] = useState<number>(0.15)
  const [retaliationSeverity, setRetaliationSeverity] = useState<string>('one_to_one')
  const [roundsPerOpponent, setRoundsPerOpponent] = useState<number>(20)

  const [loading, setLoading] = useState<boolean>(false)
  const [gauntletResult, setGauntletResult] = useState<GauntletResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [inspectedOpponentId, setInspectedOpponentId] = useState<string | null>(null)

  const handleRunGauntlet = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await simulateGauntlet({
        name: strategyName || 'CustomAgent',
        opening_move: openingMove,
        retaliation: retaliationSeverity,
        forgiveness: forgiveness,
        rounds_per_opponent: roundsPerOpponent,
      })
      setGauntletResult(res)
      if (res.duels.length > 0) {
        setInspectedOpponentId(res.duels[0].opponent_id)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Gauntlet simulation failed')
    } finally {
      setLoading(false)
    }
  }

  // Generate dynamic Python code representation
  const generatePythonCode = () => {
    return `from the_dilemma_experiment import Strategy, Action, DecisionContext
import random

class ${strategyName || 'CustomAgent'}(Strategy):
    """Dynamically configured strategy from The Dilemma Arena Sandbox."""

    def __init__(self, forgiveness: float = ${forgiveness.toFixed(2)}) -> None:
        self.forgiveness = forgiveness
        self.opponent_history: list[Action] = []
        self.my_history: list[Action] = []
        self.betrayed = False

    def choose_action(self, context: DecisionContext) -> Action:
        # First round policy
        if not self.opponent_history:
            return Action.${openingMove}
        
        last_opp = self.opponent_history[-1]
        
        # Stochastic forgiveness: forgive defection with probability p
        if last_opp == Action.DEFECT and self.forgiveness > 0.0:
            if random.random() < self.forgiveness:
                return Action.COOPERATE
        
        # Retaliation policy: ${retaliationSeverity}
        ${
          retaliationSeverity === 'grim'
            ? 'if self.betrayed:\n            return Action.DEFECT\n        return Action.COOPERATE'
            : retaliationSeverity === 'two_tats'
            ? 'if len(self.opponent_history) >= 2 and self.opponent_history[-1] == Action.DEFECT and self.opponent_history[-2] == Action.DEFECT:\n            return Action.DEFECT\n        return Action.COOPERATE'
            : retaliationSeverity === 'pavlov'
            ? 'last_my = self.my_history[-1]\n        was_win = (last_my == Action.COOPERATE and last_opp == Action.COOPERATE) or (last_my == Action.DEFECT and last_opp == Action.COOPERATE)\n        return last_my if was_win else last_my.opposite()'
            : retaliationSeverity === 'always_defect'
            ? 'return Action.DEFECT'
            : 'return last_opp  # Tit-for-Tat mirror'
        }

    def observe(self, opponent_id: str, action: Action) -> None:
        self.opponent_history.append(action)
        if action == Action.DEFECT:
            self.betrayed = True
`
  }

  const inspectedDuel: GauntletDuelResult | undefined = gauntletResult?.duels.find(
    (d) => d.opponent_id === inspectedOpponentId
  )

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="gradient-text-fire">STRATEGY SANDBOX: CREATE YOUR AGENT</h2>
          <p className="text-secondary">
            Design a custom game-theoretic strategy using behavioral trait sliders, inspect real-time Python code, and test your creation against The Gauntlet.
          </p>
        </div>
      </div>

      <div className="sandbox-layout-grid">
        {/* Visual Builder Card */}
        <div className="hud-panel sandbox-builder-panel">
          <div className="panel-title-bar">
            <h3>VISUAL TRAIT BUILDER</h3>
            <span className="badge badge-cyan">NO-CODE MODE</span>
          </div>

          <div className="control-group">
            <label className="mono input-label">STRATEGY IDENTIFIER</label>
            <input
              type="text"
              value={strategyName}
              onChange={(e) => setStrategyName(e.target.value)}
              className="hud-input mono"
              placeholder="e.g., AdaptiveGuardian"
            />
          </div>

          <div className="control-group">
            <label className="mono input-label">FIRST ROUND POLICY</label>
            <div className="toggle-btn-group">
              <button
                className={`btn ${openingMove === 'COOPERATE' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setOpeningMove('COOPERATE')}
              >
                🤝 OPEN WITH COOPERATE
              </button>
              <button
                className={`btn ${openingMove === 'DEFECT' ? 'btn-destructive' : 'btn-ghost'}`}
                onClick={() => setOpeningMove('DEFECT')}
              >
                🗡️ FIRST-STRIKE DEFECT
              </button>
            </div>
          </div>

          <div className="control-group">
            <label className="mono input-label">RETALIATION POLICY</label>
            <select
              className="hud-select"
              value={retaliationSeverity}
              onChange={(e) => setRetaliationSeverity(e.target.value)}
            >
              <option value="one_to_one">Tit-for-Tat (1 Round Retaliation)</option>
              <option value="two_tats">Tit-for-Two-Tats (Forgive 1st, Retaliate on 2nd)</option>
              <option value="grim">Grim Trigger (Permanent Defection Lockout)</option>
              <option value="pavlov">Win-Stay, Lose-Shift (Adaptive State Machine)</option>
              <option value="always_defect">Pure Defector (Unconditional Exploitation)</option>
            </select>
          </div>

          <div className="control-group">
            <div className="control-header">
              <label className="mono input-label">FORGIVENESS PROBABILITY: {(forgiveness * 100).toFixed(0)}%</label>
            </div>
            <input
              type="range"
              min="0"
              max="0.5"
              step="0.05"
              value={forgiveness}
              onChange={(e) => setForgiveness(Number(e.target.value))}
              className="hud-slider"
            />
          </div>

          <div className="control-group">
            <div className="control-header">
              <label className="mono input-label">GAUNTLET ROUNDS / DUEL: {roundsPerOpponent}</label>
            </div>
            <input
              type="range"
              min="10"
              max="40"
              step="5"
              value={roundsPerOpponent}
              onChange={(e) => setRoundsPerOpponent(Number(e.target.value))}
              className="hud-slider"
            />
          </div>

          <button
            className="btn btn-primary btn-run-gauntlet mt-3"
            onClick={handleRunGauntlet}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="pulse-indicator"></span>
                <span>RUNNING IN THE GAUNTLET...</span>
              </>
            ) : (
              '🛡️ TEST AGAINST THE GAUNTLET'
            )}
          </button>

          {error && <div className="error-banner mono mt-2">{error}</div>}
        </div>

        {/* Python Sandbox Preview Card */}
        <div className="hud-panel code-sandbox-panel">
          <div className="panel-title-bar">
            <h3>LIVE PYTHON CODE CONTRACT</h3>
            <span className="badge badge-gold">PYTHON 3.12 VALIDATED</span>
          </div>

          <pre className="code-editor-mock mono">
            {generatePythonCode()}
          </pre>
        </div>
      </div>

      {/* The Gauntlet Results Arena */}
      {gauntletResult && (
        <div className="hud-panel gauntlet-results-container mt-4">
          <div className="panel-title-bar">
            <div>
              <h3>THE GAUNTLET: AXIOMATIC SCORECARD</h3>
              <span className="mono text-muted text-xs">
                CUSTOM AGENT: {gauntletResult.custom_name} VS 5 CANONICAL BENCHMARKS
              </span>
            </div>
            <div className="scoreboard-pill mono">
              <span className="score-a font-bold text-cyan">
                TOTAL: {gauntletResult.scorecard.total_score} / {gauntletResult.scorecard.max_possible_score} PTS
              </span>
              <span className="score-sep">|</span>
              <span className="score-b font-bold text-gold">
                WIN RATE: {(gauntletResult.scorecard.overall_win_rate * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Archetype Verdict Banner */}
          <div className="gauntlet-verdict-banner">
            <div className="verdict-top">
              <span className="badge badge-cyan font-bold">{gauntletResult.scorecard.archetype_badge}</span>
            </div>
            <p className="verdict-desc text-secondary mt-1">
              {gauntletResult.scorecard.verdict}
            </p>
          </div>

          {/* 4 Cybernetic Axiom Gauges */}
          <div className="axioms-gauge-grid mt-3">
            <div className="axiom-gauge-card">
              <div className="gauge-header mono text-xs">
                <span>NICENESS RATING</span>
                <span className="text-cyan font-bold">{(gauntletResult.scorecard.niceness * 100).toFixed(0)}%</span>
              </div>
              <div className="gauge-bar-track">
                <div
                  className="gauge-bar-fill fill-cyan"
                  style={{ width: `${gauntletResult.scorecard.niceness * 100}%` }}
                />
              </div>
              <span className="gauge-subtext text-muted text-xs">Never defects first unprovoked</span>
            </div>

            <div className="axiom-gauge-card">
              <div className="gauge-header mono text-xs">
                <span>RETALIATORY SPEED</span>
                <span className="text-red font-bold">{(gauntletResult.scorecard.retaliation * 100).toFixed(0)}%</span>
              </div>
              <div className="gauge-bar-track">
                <div
                  className="gauge-bar-fill fill-red"
                  style={{ width: `${gauntletResult.scorecard.retaliation * 100}%` }}
                />
              </div>
              <span className="gauge-subtext text-muted text-xs">Punishes betrayal without hesitation</span>
            </div>

            <div className="axiom-gauge-card">
              <div className="gauge-header mono text-xs">
                <span>FORGIVING CAPACITY</span>
                <span className="text-gold font-bold">{(gauntletResult.scorecard.forgiveness * 100).toFixed(0)}%</span>
              </div>
              <div className="gauge-bar-track">
                <div
                  className="gauge-bar-fill fill-gold"
                  style={{ width: `${gauntletResult.scorecard.forgiveness * 100}%` }}
                />
              </div>
              <span className="gauge-subtext text-muted text-xs">Restores mutual cooperation loops</span>
            </div>

            <div className="axiom-gauge-card">
              <div className="gauge-header mono text-xs">
                <span>EXPLOITATION RESISTANCE</span>
                <span className="text-green font-bold">{(gauntletResult.scorecard.exploitation_resistance * 100).toFixed(0)}%</span>
              </div>
              <div className="gauge-bar-track">
                <div
                  className="gauge-bar-fill fill-green"
                  style={{ width: `${gauntletResult.scorecard.exploitation_resistance * 100}%` }}
                />
              </div>
              <span className="gauge-subtext text-muted text-xs">Denies surplus to predators & extortioners</span>
            </div>
          </div>

          {/* Benchmark Duels Table */}
          <div className="duels-table-section mt-4">
            <div className="section-title mono text-xs text-muted mb-2">
              THE 5 GUARDIAN DUELS (CLICK ANY ROW TO INSPECT ROUNDS):
            </div>
            <div className="leaderboard-table-container">
              <table className="hud-table">
                <thead>
                  <tr>
                    <th>OUTCOME</th>
                    <th>GUARDIAN</th>
                    <th>ARCHETYPE</th>
                    <th>SCORE</th>
                    <th>CUSTOM COOP</th>
                    <th>RIVAL COOP</th>
                  </tr>
                </thead>
                <tbody>
                  {gauntletResult.duels.map((duel) => {
                    const isSelected = inspectedOpponentId === duel.opponent_id
                    let outcomeBadge = <span className="badge badge-green">🏆 WIN</span>
                    if (duel.outcome === 'LOSS') {
                      outcomeBadge = <span className="badge badge-fire">❌ LOSS</span>
                    } else if (duel.outcome === 'TIE') {
                      outcomeBadge = <span className="badge badge-gold">🤝 TIE</span>
                    }

                    return (
                      <tr
                        key={duel.opponent_id}
                        className={`${isSelected ? 'row-selected' : ''}`}
                        onClick={() => setInspectedOpponentId(duel.opponent_id)}
                        style={{ cursor: 'pointer' }}
                      >
                        <td>{outcomeBadge}</td>
                        <td className="mono font-bold text-cyan">{duel.opponent_name}</td>
                        <td className="text-secondary text-sm">{duel.opponent_archetype}</td>
                        <td className="mono font-bold">
                          <span className="text-cyan">{duel.custom_score}</span>
                          <span className="text-muted"> - </span>
                          <span className="text-gold">{duel.opponent_score}</span>
                        </td>
                        <td className="mono text-cyan">{(duel.custom_coop_rate * 100).toFixed(0)}%</td>
                        <td className="mono text-gold">{(duel.opponent_coop_rate * 100).toFixed(0)}%</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {/* Duel Round Inspector */}
            {inspectedDuel && (
              <div className="inspected-duel-rounds-box hud-panel mt-3">
                <div className="drawer-header">
                  <span className="mono font-bold text-cyan">
                    ROUND TIMELINE: {strategyName} VS {inspectedDuel.opponent_name} ({inspectedDuel.custom_score} - {inspectedDuel.opponent_score})
                  </span>
                  <span className="mono text-xs text-muted">
                    {inspectedDuel.rounds.length} ROUNDS PLAYED
                  </span>
                </div>

                <div className="round-strip mt-2">
                  {inspectedDuel.rounds.map((r) => (
                    <div
                      key={r.round_number}
                      className="round-cell"
                      title={`R${r.round_number}: ${strategyName}(${r.action_a}) +${r.payoff_a} | ${inspectedDuel.opponent_name}(${r.action_b}) +${r.payoff_b}`}
                    >
                      <div className={`action-badge ${r.action_a === 'COOPERATE' ? 'action-c' : 'action-d'}`}>
                        {r.action_a === 'COOPERATE' ? 'C' : 'D'}
                      </div>
                      <div className="round-num mono">{r.round_number}</div>
                      <div className={`action-badge ${r.action_b === 'COOPERATE' ? 'action-c' : 'action-d'}`}>
                        {r.action_b === 'COOPERATE' ? 'C' : 'D'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
