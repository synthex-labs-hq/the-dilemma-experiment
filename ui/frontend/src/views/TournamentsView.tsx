import React, { useState } from 'react'
import { simulateTournament, type LeaderboardRow, type StrategyMeta, type TournamentResponse } from '../api/client'

interface TournamentsViewProps {
  strategies: StrategyMeta[]
}

export const TournamentsView: React.FC<TournamentsViewProps> = ({ strategies }) => {
  const [selectedCounts, setSelectedCounts] = useState<Record<string, number>>({
    tit_for_tat: 3,
    always_defect: 2,
    win_stay_lose_shift: 2,
    generous_zd: 2,
    extortioner: 2,
  })
  const [roundsPerMatch, setRoundsPerMatch] = useState<number>(10)
  const [noise, setNoise] = useState<number>(0.0)
  const [loading, setLoading] = useState<boolean>(false)
  const [result, setResult] = useState<TournamentResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleCountChange = (stratId: string, count: number) => {
    setSelectedCounts((prev) => ({
      ...prev,
      [stratId]: Math.max(0, count),
    }))
  }

  const handleRunTournament = async () => {
    const selections = Object.entries(selectedCounts)
      .filter(([_, count]) => count > 0)
      .map(([id, count]) => ({ strategy_id: id, count }))

    if (selections.reduce((acc, curr) => acc + curr.count, 0) < 2) {
      setError('Select at least 2 agents across all strategies.')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const res = await simulateTournament({
        selections,
        rounds_per_match: roundsPerMatch,
        noise,
      })
      setResult(res)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Tournament failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="gradient-text-gold">TOURNAMENT HUB: MULTI-AGENT SOCIETIES</h2>
          <p className="text-secondary">
            Compose a multi-agent society and execute a full round-robin tournament to observe evolutionary survival.
          </p>
        </div>
      </div>

      <div className="tournament-layout-grid">
        {/* Population Config Panel */}
        <div className="hud-panel population-picker-panel">
          <div className="panel-title-bar">
            <h3>SELECT POPULATION CASTE</h3>
            <span className="badge badge-gold">
              TOTAL AGENTS: {Object.values(selectedCounts).reduce((a, b) => a + b, 0)}
            </span>
          </div>

          <div className="strategy-picker-list">
            {strategies.map((s) => {
              const count = selectedCounts[s.id] || 0
              return (
                <div key={s.id} className="strat-picker-row">
                  <div className="strat-info">
                    <span className="strat-name">{s.name}</span>
                    <span className="badge badge-cyan">EP {s.episode}</span>
                    <span className="mono text-muted">{s.archetype}</span>
                  </div>
                  <div className="stepper-controls">
                    <button
                      className="btn-stepper"
                      onClick={() => handleCountChange(s.id, count - 1)}
                    >
                      -
                    </button>
                    <span className="mono stepper-val">{count}</span>
                    <button
                      className="btn-stepper"
                      onClick={() => handleCountChange(s.id, count + 1)}
                    >
                      +
                    </button>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="tournament-run-bar">
            <div className="control-group">
              <label className="mono input-label">ROUNDS / MATCH: {roundsPerMatch}</label>
              <input
                type="range"
                min="5"
                max="30"
                step="5"
                value={roundsPerMatch}
                onChange={(e) => setRoundsPerMatch(Number(e.target.value))}
                className="hud-slider"
              />
            </div>

            <div className="control-group">
              <label className="mono input-label">CHANNEL NOISE: {(noise * 100).toFixed(0)}%</label>
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
              className="btn btn-primary btn-run-tournament"
              onClick={handleRunTournament}
              disabled={loading}
            >
              {loading ? 'SIMULATING TOURNAMENT...' : '🏆 EXECUTE TOURNAMENT'}
            </button>
          </div>

          {error && <div className="error-banner mono">{error}</div>}
        </div>

        {/* Leaderboard Results Panel */}
        <div className="hud-panel leaderboard-panel">
          <div className="panel-title-bar">
            <h3>SOCIETY LEADERBOARD</h3>
            {result && (
              <span className="badge badge-cyan">
                {result.total_matches} MATCHES | COOP: {(result.population_cooperation_rate * 100).toFixed(1)}%
              </span>
            )}
          </div>

          {!result ? (
            <div className="empty-state-box mono text-muted">
              Configure your population and click "EXECUTE TOURNAMENT" to view live rankings.
            </div>
          ) : (
            <div className="leaderboard-table-container">
              <table className="hud-table">
                <thead>
                  <tr>
                    <th>RANK</th>
                    <th>AGENT</th>
                    <th>STRATEGY</th>
                    <th>SCORE</th>
                    <th>AVG / RND</th>
                    <th>W / T / L</th>
                    <th>COOP %</th>
                  </tr>
                </thead>
                <tbody>
                  {result.leaderboard.map((row: LeaderboardRow) => (
                    <tr key={row.agent_id} className={row.rank <= 3 ? 'top-rank-row' : ''}>
                      <td className="mono rank-cell">
                        {row.rank === 1 ? '🥇' : row.rank === 2 ? '🥈' : row.rank === 3 ? '🥉' : `#${row.rank}`}
                      </td>
                      <td className="mono agent-cell">{row.agent_id}</td>
                      <td>{row.strategy_name}</td>
                      <td className="mono score-cell font-bold">{row.total_score}</td>
                      <td className="mono">{row.average_score_per_round.toFixed(2)}</td>
                      <td className="mono text-muted">{row.wins}/{row.ties}/{row.losses}</td>
                      <td className="mono text-cyan">{(row.cooperation_rate * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
