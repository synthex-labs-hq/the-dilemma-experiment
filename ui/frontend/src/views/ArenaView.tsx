import React, { useState } from 'react'
import { simulateMatch, type MatchResponse, type StrategyMeta } from '../api/client'

interface ArenaViewProps {
  strategies: StrategyMeta[]
  speed: '1x' | '5x' | 'max'
}

export const ArenaView: React.FC<ArenaViewProps> = ({ strategies }) => {
  const [stratAId, setStratAId] = useState<string>('tit_for_tat')
  const [stratBId, setStratBId] = useState<string>('extortioner')
  const [rounds, setRounds] = useState<number>(15)
  const [noise, setNoise] = useState<number>(0.0)
  const [loading, setLoading] = useState<boolean>(false)
  const [matchResult, setMatchResult] = useState<MatchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const stratA = strategies.find((s) => s.id === stratAId) || strategies[0]
  const stratB = strategies.find((s) => s.id === stratBId) || strategies[1]

  const handleRunMatch = async () => {
    if (!stratA || !stratB) return
    setLoading(true)
    setError(null)
    try {
      const res = await simulateMatch({
        strategy_a: stratA.id,
        strategy_b: stratB.id,
        round_count: rounds,
        noise: noise,
      })
      setMatchResult(res)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Simulation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="view-container">
      {/* Top Banner */}
      <div className="view-header">
        <div>
          <h2 className="gradient-text-cyan">THE ARENA: PAIRWISE STRATEGIC DUEL</h2>
          <p className="text-secondary">
            Pit any two game-theoretic strategies against each other. Observe real-time reciprocity, retaliation, and deception.
          </p>
        </div>
      </div>

      {/* Duel Setup Grid */}
      <div className="arena-setup-grid">
        {/* Agent A Card */}
        <div className="hud-panel agent-card agent-card-a">
          <div className="card-top-tag">
            <span className="badge badge-cyan">AGENT ALPHA</span>
            <span className="mono text-muted">EPISODE {stratA?.episode || 1}</span>
          </div>

          <label className="input-label mono">SELECT STRATEGY</label>
          <select
            className="hud-select"
            value={stratAId}
            onChange={(e) => setStratAId(e.target.value)}
          >
            {strategies.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.archetype})
              </option>
            ))}
          </select>

          {stratA && (
            <div className="strategy-detail-box">
              <div className="strat-archetype mono gradient-text-cyan">{stratA.archetype}</div>
              <p className="strat-desc">{stratA.description}</p>
              <div className="trait-chips">
                {stratA.traits.map((t) => (
                  <span key={t} className="badge badge-cyan">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Center VS & Controls Panel */}
        <div className="hud-panel vs-controls-panel">
          <div className="vs-emblem gradient-text-fire">VS</div>

          <div className="control-group">
            <div className="control-header">
              <label className="mono input-label">ROUNDS: {rounds}</label>
            </div>
            <input
              type="range"
              min="5"
              max="50"
              step="5"
              value={rounds}
              onChange={(e) => setRounds(Number(e.target.value))}
              className="hud-slider"
            />
          </div>

          <div className="control-group">
            <div className="control-header">
              <label className="mono input-label">CHANNEL NOISE: {(noise * 100).toFixed(0)}%</label>
            </div>
            <input
              type="range"
              min="0"
              max="0.2"
              step="0.05"
              value={noise}
              onChange={(e) => setNoise(Number(e.target.value))}
              className="hud-slider"
            />
          </div>

          <button
            className="btn btn-primary btn-run-duel"
            onClick={handleRunMatch}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="pulse-indicator"></span>
                <span>SIMULATING DUEL...</span>
              </>
            ) : (
              <>
                <span>⚔️</span>
                <span>RUN SIMULATION</span>
              </>
            )}
          </button>

          {error && <div className="error-banner mono">{error}</div>}
        </div>

        {/* Agent B Card */}
        <div className="hud-panel agent-card agent-card-b">
          <div className="card-top-tag">
            <span className="badge badge-purple">AGENT BETA</span>
            <span className="mono text-muted">EPISODE {stratB?.episode || 1}</span>
          </div>

          <label className="input-label mono">SELECT STRATEGY</label>
          <select
            className="hud-select"
            value={stratBId}
            onChange={(e) => setStratBId(e.target.value)}
          >
            {strategies.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.archetype})
              </option>
            ))}
          </select>

          {stratB && (
            <div className="strategy-detail-box">
              <div className="strat-archetype mono gradient-text-gold">{stratB.archetype}</div>
              <p className="strat-desc">{stratB.description}</p>
              <div className="trait-chips">
                {stratB.traits.map((t) => (
                  <span key={t} className="badge badge-purple">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Match Result Display */}
      {matchResult && (
        <div className="hud-panel match-results-container">
          <div className="results-header">
            <h3>SIMULATION TELEMETRY REPORT</h3>
            <div className="scoreboard-pill mono">
              <span className="score-a">{matchResult.strategy_a.name}: {matchResult.score_a} pts</span>
              <span className="score-sep">|</span>
              <span className="score-b">{matchResult.strategy_b.name}: {matchResult.score_b} pts</span>
            </div>
          </div>

          {/* Quick Metrics Grid */}
          <div className="metrics-row">
            <div className="metric-box">
              <span className="metric-label mono">COOPERATION ALPHA</span>
              <span className="metric-val mono text-cyan">{(matchResult.cooperation_rate_a * 100).toFixed(1)}%</span>
            </div>
            <div className="metric-box">
              <span className="metric-label mono">COOPERATION BETA</span>
              <span className="metric-val mono text-purple">{(matchResult.cooperation_rate_b * 100).toFixed(1)}%</span>
            </div>
            <div className="metric-box">
              <span className="metric-label mono">DECEPTION RATE ALPHA</span>
              <span className="metric-val mono text-green">{(matchResult.deception_rate_a * 100).toFixed(1)}%</span>
            </div>
            <div className="metric-box">
              <span className="metric-label mono">DECEPTION RATE BETA</span>
              <span className="metric-val mono text-red">{(matchResult.deception_rate_b * 100).toFixed(1)}%</span>
            </div>
          </div>

          {/* Round-by-round strip */}
          <div className="round-strip-container">
            <div className="strip-title mono">ROUND HISTORY:</div>
            <div className="round-strip">
              {matchResult.rounds.map((r) => (
                <div key={r.round_number} className="round-cell" title={`R${r.round_number}: A(${r.action_a}) +${r.payoff_a} | B(${r.action_b}) +${r.payoff_b}`}>
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
        </div>
      )}
    </div>
  )
}
