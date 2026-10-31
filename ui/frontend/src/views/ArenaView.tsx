import React, { useEffect, useState } from 'react'
import { simulateMatch, type MatchResponse, type StrategyMeta } from '../api/client'
import { ScoreChart } from '../components/ScoreChart'

interface ArenaViewProps {
  strategies: StrategyMeta[]
  speed: '1x' | '5x' | 'max'
}

export const ArenaView: React.FC<ArenaViewProps> = ({ strategies, speed }) => {
  const [stratAId, setStratAId] = useState<string>('tit_for_tat')
  const [stratBId, setStratBId] = useState<string>('extortioner')
  const [rounds, setRounds] = useState<number>(15)
  const [noise, setNoise] = useState<number>(0.0)
  const [loading, setLoading] = useState<boolean>(false)
  const [matchResult, setMatchResult] = useState<MatchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Playback & Animation states
  const [currentRoundIndex, setCurrentRoundIndex] = useState<number>(0)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)

  const stratA = strategies.find((s) => s.id === stratAId) || strategies[0]
  const stratB = strategies.find((s) => s.id === stratBId) || strategies[1]

  const handleRunMatch = async () => {
    if (!stratA || !stratB) return
    setLoading(true)
    setError(null)
    setIsPlaying(false)
    try {
      const res = await simulateMatch({
        strategy_a: stratA.id,
        strategy_b: stratB.id,
        round_count: rounds,
        noise: noise,
      })
      setMatchResult(res)
      setCurrentRoundIndex(0)
      setIsPlaying(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Simulation failed')
    } finally {
      setLoading(false)
    }
  }

  // Playback timer ticker
  useEffect(() => {
    if (!isPlaying || !matchResult || matchResult.rounds.length === 0) return

    const intervalMs = speed === 'max' ? 40 : speed === '5x' ? 160 : 650

    const timer = setInterval(() => {
      setCurrentRoundIndex((prev) => {
        if (prev >= matchResult.rounds.length - 1) {
          setIsPlaying(false)
          return prev
        }
        return prev + 1
      })
    }, intervalMs)

    return () => clearInterval(timer)
  }, [isPlaying, matchResult, speed])

  const activeRound = matchResult?.rounds[currentRoundIndex]

  const getPayoffMeta = (actA: string, actB: string) => {
    if (actA === 'COOPERATE' && actB === 'COOPERATE') {
      return {
        label: 'MUTUAL COOPERATION (R=3, R=3)',
        tagClass: 'badge-cyan',
        desc: 'Symmetric reciprocal reward.',
      }
    }
    if (actA === 'DEFECT' && actB === 'COOPERATE') {
      return {
        label: "TEMPTATION EXPLOITATION (T=5, S=0)",
        tagClass: 'badge-fire',
        desc: 'Agent Alpha exploited Agent Beta.',
      }
    }
    if (actA === 'COOPERATE' && actB === 'DEFECT') {
      return {
        label: "SUCKER'S PAYOFF (S=0, T=5)",
        tagClass: 'badge-gold',
        desc: 'Agent Beta exploited Agent Alpha.',
      }
    }
    return {
      label: 'MUTUAL DEFECT / PUNISHMENT (P=1, P=1)',
      tagClass: 'badge-purple',
      desc: 'Conflict lock / defection trap.',
    }
  }

  return (
    <div className="view-container">
      {/* Top Banner */}
      <div className="view-header">
        <div>
          <h2 className="gradient-text-cyan">THE ARENA: PAIRWISE STRATEGIC DUEL</h2>
          <p className="text-secondary">
            Pit any two game-theoretic strategies against each other. Inspect round-by-round dynamics, pre-play dialogue, and score trajectories.
          </p>
        </div>
      </div>

      {/* Duel Setup Grid */}
      <div className="arena-setup-grid">
        {/* Agent Alpha Card */}
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

        {/* Agent Beta Card */}
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
      {matchResult && activeRound && (
        <div className="hud-panel match-results-container">
          <div className="results-header">
            <div>
              <h3>SIMULATION TELEMETRY & PLAYBACK</h3>
              <span className="mono text-muted">
                {matchResult.strategy_a.name} VS {matchResult.strategy_b.name}
              </span>
            </div>

            <div className="scoreboard-pill mono">
              <span className="score-a font-bold text-cyan">
                {matchResult.strategy_a.name}: {matchResult.score_a} pts
              </span>
              <span className="score-sep">|</span>
              <span className="score-b font-bold text-gold">
                {matchResult.strategy_b.name}: {matchResult.score_b} pts
              </span>
            </div>
          </div>

          {/* Turn-by-Turn Focus Theater */}
          <div className="round-theater-box">
            <div className="theater-top-bar">
              <div className="round-counter-badge mono">
                ROUND {activeRound.round_number} OF {matchResult.rounds.length}
              </div>
              <div className="payoff-classification">
                <span className={`badge ${getPayoffMeta(activeRound.action_a, activeRound.action_b).tagClass}`}>
                  {getPayoffMeta(activeRound.action_a, activeRound.action_b).label}
                </span>
              </div>
            </div>

            <div className="theater-arena-duo">
              {/* Alpha Action Card */}
              <div className={`action-card-theater ${activeRound.action_a === 'COOPERATE' ? 'action-theater-coop' : 'action-theater-defect'}`}>
                <div className="theater-agent-label mono text-cyan">ALPHA: {matchResult.strategy_a.name}</div>
                <div className="theater-action-name">
                  {activeRound.action_a === 'COOPERATE' ? '🤝 COOPERATE' : '🗡️ DEFECT'}
                </div>
                <div className="theater-payoff-chip mono">
                  +{activeRound.payoff_a} pts <span className="text-muted">(Total: {activeRound.cumulative_a})</span>
                </div>

                {activeRound.message_a && (
                  <div className="dialogue-bubble dialogue-alpha mono">
                    <span className="dialogue-speaker">Alpha:</span> "{activeRound.message_a}"
                  </div>
                )}

                {activeRound.rationale_a && (
                  <div className="rationale-box mono">
                    <span className="text-muted">Thought:</span> {activeRound.rationale_a}
                  </div>
                )}

                {activeRound.is_deceptive_a && (
                  <div className="deception-alert badge-fire mono">
                    ⚠️ BETRAYAL: Promised cooperation in dialogue, but defected!
                  </div>
                )}
              </div>

              {/* Theater VS Center */}
              <div className="theater-vs-divider mono">
                <span className="gradient-text-fire">⚡</span>
                <span className="round-payoff-diff mono">
                  +{activeRound.payoff_a} vs +{activeRound.payoff_b}
                </span>
              </div>

              {/* Beta Action Card */}
              <div className={`action-card-theater ${activeRound.action_b === 'COOPERATE' ? 'action-theater-coop' : 'action-theater-defect'}`}>
                <div className="theater-agent-label mono text-gold">BETA: {matchResult.strategy_b.name}</div>
                <div className="theater-action-name">
                  {activeRound.action_b === 'COOPERATE' ? '🤝 COOPERATE' : '🗡️ DEFECT'}
                </div>
                <div className="theater-payoff-chip mono">
                  +{activeRound.payoff_b} pts <span className="text-muted">(Total: {activeRound.cumulative_b})</span>
                </div>

                {activeRound.message_b && (
                  <div className="dialogue-bubble dialogue-beta mono">
                    <span className="dialogue-speaker">Beta:</span> "{activeRound.message_b}"
                  </div>
                )}

                {activeRound.rationale_b && (
                  <div className="rationale-box mono">
                    <span className="text-muted">Thought:</span> {activeRound.rationale_b}
                  </div>
                )}

                {activeRound.is_deceptive_b && (
                  <div className="deception-alert badge-fire mono">
                    ⚠️ BETRAYAL: Promised cooperation in dialogue, but defected!
                  </div>
                )}
              </div>
            </div>

            {/* Playback Control Toolbar */}
            <div className="playback-toolbar">
              <div className="playback-btns">
                <button
                  className="btn btn-ghost btn-playback"
                  onClick={() => {
                    setCurrentRoundIndex(0)
                    setIsPlaying(false)
                  }}
                  title="First Round"
                >
                  ⏮
                </button>
                <button
                  className="btn btn-ghost btn-playback"
                  onClick={() => {
                    setCurrentRoundIndex((p) => Math.max(0, p - 1))
                    setIsPlaying(false)
                  }}
                  title="Previous Round"
                >
                  ◀
                </button>
                <button
                  className="btn btn-primary btn-playback-play"
                  onClick={() => {
                    if (currentRoundIndex >= matchResult.rounds.length - 1) {
                      setCurrentRoundIndex(0)
                    }
                    setIsPlaying(!isPlaying)
                  }}
                >
                  {isPlaying ? '⏸ PAUSE' : '▶ PLAY'}
                </button>
                <button
                  className="btn btn-ghost btn-playback"
                  onClick={() => {
                    setCurrentRoundIndex((p) => Math.min(matchResult.rounds.length - 1, p + 1))
                    setIsPlaying(false)
                  }}
                  title="Next Round"
                >
                  ▶
                </button>
                <button
                  className="btn btn-ghost btn-playback"
                  onClick={() => {
                    setCurrentRoundIndex(matchResult.rounds.length - 1)
                    setIsPlaying(false)
                  }}
                  title="Last Round"
                >
                  ⏭
                </button>
              </div>

              {/* Scrub Slider */}
              <div className="scrub-container">
                <input
                  type="range"
                  min="0"
                  max={matchResult.rounds.length - 1}
                  value={currentRoundIndex}
                  onChange={(e) => {
                    setCurrentRoundIndex(Number(e.target.value))
                    setIsPlaying(false)
                  }}
                  className="hud-slider scrub-slider"
                />
              </div>
            </div>
          </div>

          {/* Cumulative Score Trajectory Chart */}
          <div className="score-chart-section">
            <div className="section-title mono text-muted">
              CUMULATIVE SCORE TRAJECTORY (CLICK ANY POINT TO JUMP)
            </div>
            <ScoreChart
              rounds={matchResult.rounds}
              currentRoundIndex={currentRoundIndex}
              onSelectRound={(idx) => {
                setCurrentRoundIndex(idx)
                setIsPlaying(false)
              }}
              nameA={matchResult.strategy_a.name}
              nameB={matchResult.strategy_b.name}
            />
          </div>

          {/* Quick Metrics Grid */}
          <div className="metrics-row">
            <div className="metric-box">
              <span className="metric-label mono">COOPERATION ALPHA</span>
              <span className="metric-val mono text-cyan">{(matchResult.cooperation_rate_a * 100).toFixed(1)}%</span>
            </div>
            <div className="metric-box">
              <span className="metric-label mono">COOPERATION BETA</span>
              <span className="metric-val mono text-gold">{(matchResult.cooperation_rate_b * 100).toFixed(1)}%</span>
            </div>
            <div className="metric-box">
              <span className="metric-label mono">DECEPTION RATE ALPHA</span>
              <span className={`metric-val mono ${matchResult.deception_rate_a > 0 ? 'text-red' : 'text-green'}`}>
                {(matchResult.deception_rate_a * 100).toFixed(1)}%
              </span>
            </div>
            <div className="metric-box">
              <span className="metric-label mono">DECEPTION RATE BETA</span>
              <span className={`metric-val mono ${matchResult.deception_rate_b > 0 ? 'text-red' : 'text-green'}`}>
                {(matchResult.deception_rate_b * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Round-by-round interactive strip */}
          <div className="round-strip-container">
            <div className="strip-title mono">ROUND NAVIGATION STRIP (CLICK TO INSPECT):</div>
            <div className="round-strip">
              {matchResult.rounds.map((r, idx) => {
                const isSelected = idx === currentRoundIndex
                return (
                  <div
                    key={r.round_number}
                    className={`round-cell ${isSelected ? 'round-cell-active' : ''}`}
                    onClick={() => {
                      setCurrentRoundIndex(idx)
                      setIsPlaying(false)
                    }}
                    title={`Round ${r.round_number}: Alpha(${r.action_a}) +${r.payoff_a} | Beta(${r.action_b}) +${r.payoff_b}`}
                  >
                    <div className={`action-badge ${r.action_a === 'COOPERATE' ? 'action-c' : 'action-d'}`}>
                      {r.action_a === 'COOPERATE' ? 'C' : 'D'}
                    </div>
                    <div className="round-num mono">{r.round_number}</div>
                    <div className={`action-badge ${r.action_b === 'COOPERATE' ? 'action-c' : 'action-d'}`}>
                      {r.action_b === 'COOPERATE' ? 'C' : 'D'}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
