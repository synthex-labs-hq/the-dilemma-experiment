import React, { useMemo, useState } from 'react'
import {
  simulateTournament,
  type LeaderboardRow,
  type StrategyMeta,
  type TournamentResponse,
} from '../api/client'
import { CrossTableMatrix } from '../components/CrossTableMatrix'

interface TournamentsViewProps {
  strategies: StrategyMeta[]
}

type SortField = 'rank' | 'agent_id' | 'strategy_name' | 'total_score' | 'average_score_per_round' | 'wins' | 'cooperation_rate'

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

  // Sub-view toggle & drilldown
  const [viewMode, setViewMode] = useState<'leaderboard' | 'cross-table'>('leaderboard')
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)

  // Sorting
  const [sortField, setSortField] = useState<SortField>('rank')
  const [sortAsc, setSortAsc] = useState<boolean>(true)

  const handleCountChange = (stratId: string, count: number) => {
    setSelectedCounts((prev) => ({
      ...prev,
      [stratId]: Math.max(0, count),
    }))
  }

  const applyPreset = (preset: 'axelrod' | 'forgiveness' | 'zd' | 'clear') => {
    if (preset === 'clear') {
      setSelectedCounts({})
      return
    }
    if (preset === 'axelrod') {
      setSelectedCounts({
        tit_for_tat: 3,
        always_defect: 2,
        grim_trigger: 2,
        always_cooperate: 2,
        random: 2,
      })
      return
    }
    if (preset === 'forgiveness') {
      setSelectedCounts({
        generous_tit_for_tat: 3,
        win_stay_lose_shift: 3,
        tit_for_two_tats: 2,
        always_defect: 2,
      })
      return
    }
    if (preset === 'zd') {
      setSelectedCounts({
        extortioner: 3,
        generous_zd: 3,
        equalizer: 2,
        tit_for_tat: 2,
      })
      return
    }
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
      if (res.leaderboard.length > 0) {
        setSelectedAgentId(res.leaderboard[0].agent_id)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Tournament failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc)
    } else {
      setSortField(field)
      setSortAsc(field === 'rank' || field === 'agent_id')
    }
  }

  const sortedLeaderboard = useMemo(() => {
    if (!result) return []
    const list = [...result.leaderboard]
    list.sort((a, b) => {
      const valA = a[sortField]
      const valB = b[sortField]
      if (typeof valA === 'string' && typeof valB === 'string') {
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA)
      }
      return sortAsc ? (valA as number) - (valB as number) : (valB as number) - (valA as number)
    })
    return list
  }, [result, sortField, sortAsc])

  // Head-to-head matches for the selected agent
  const selectedAgentMatches = useMemo(() => {
    if (!result || !result.pairwise_matches || !selectedAgentId) return []
    return result.pairwise_matches.filter(
      (m) => m.first_agent_id === selectedAgentId || m.second_agent_id === selectedAgentId
    )
  }, [result, selectedAgentId])

  const selectedAgentRow = result?.leaderboard.find((r) => r.agent_id === selectedAgentId)

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="gradient-text-gold">TOURNAMENT HUB: MULTI-AGENT SOCIETIES</h2>
          <p className="text-secondary">
            Compose a multi-agent society and execute a full round-robin tournament. Inspect leaderboard rankings and head-to-head cross-table matrices.
          </p>
        </div>
      </div>

      <div className="tournament-layout-grid">
        {/* Population Config Panel */}
        <div className="hud-panel population-picker-panel">
          <div className="panel-title-bar">
            <h3>SELECT POPULATION CASTE</h3>
            <span className="badge badge-gold">
              AGENTS: {Object.values(selectedCounts).reduce((a, b) => a + b, 0)}
            </span>
          </div>

          {/* Quick Preset Buttons */}
          <div className="preset-btn-bar">
            <span className="mono text-muted text-xs">PRESETS:</span>
            <button className="btn btn-ghost btn-xs" onClick={() => applyPreset('axelrod')}>
              Axelrod Classic
            </button>
            <button className="btn btn-ghost btn-xs" onClick={() => applyPreset('forgiveness')}>
              Forgiving Society
            </button>
            <button className="btn btn-ghost btn-xs" onClick={() => applyPreset('zd')}>
              ZD Gauntlet
            </button>
            <button className="btn btn-ghost btn-xs" onClick={() => applyPreset('clear')}>
              Clear All
            </button>
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
              {loading ? (
                <>
                  <span className="pulse-indicator"></span>
                  <span>SIMULATING TOURNAMENT...</span>
                </>
              ) : (
                '🏆 EXECUTE TOURNAMENT'
              )}
            </button>
          </div>

          {error && <div className="error-banner mono">{error}</div>}
        </div>

        {/* Leaderboard & Cross-Table Results Panel */}
        <div className="hud-panel leaderboard-panel">
          <div className="panel-title-bar">
            <div>
              <h3>SOCIETY RESULTS</h3>
              {result && (
                <span className="badge badge-cyan">
                  {result.total_matches} MATCHES | COOP: {(result.population_cooperation_rate * 100).toFixed(1)}%
                </span>
              )}
            </div>

            {result && (
              <div className="view-mode-toggle">
                <button
                  className={`btn btn-xs ${viewMode === 'leaderboard' ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setViewMode('leaderboard')}
                >
                  Leaderboard
                </button>
                <button
                  className={`btn btn-xs ${viewMode === 'cross-table' ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setViewMode('cross-table')}
                >
                  Cross-Table Matrix
                </button>
              </div>
            )}
          </div>

          {!result ? (
            <div className="empty-state-box mono text-muted">
              Configure your population and click "EXECUTE TOURNAMENT" to view live rankings and pairwise matrices.
            </div>
          ) : viewMode === 'cross-table' ? (
            <CrossTableMatrix
              leaderboard={result.leaderboard}
              pairwiseMatches={result.pairwise_matches || []}
              selectedAgentId={selectedAgentId}
              onSelectAgent={(id) => setSelectedAgentId(id)}
            />
          ) : (
            <div className="leaderboard-table-container">
              <table className="hud-table">
                <thead>
                  <tr>
                    <th onClick={() => handleSort('rank')} style={{ cursor: 'pointer' }}>
                      RANK {sortField === 'rank' ? (sortAsc ? '▲' : '▼') : ''}
                    </th>
                    <th onClick={() => handleSort('agent_id')} style={{ cursor: 'pointer' }}>
                      AGENT {sortField === 'agent_id' ? (sortAsc ? '▲' : '▼') : ''}
                    </th>
                    <th onClick={() => handleSort('strategy_name')} style={{ cursor: 'pointer' }}>
                      STRATEGY {sortField === 'strategy_name' ? (sortAsc ? '▲' : '▼') : ''}
                    </th>
                    <th onClick={() => handleSort('total_score')} style={{ cursor: 'pointer' }}>
                      TOTAL SCORE {sortField === 'total_score' ? (sortAsc ? '▲' : '▼') : ''}
                    </th>
                    <th onClick={() => handleSort('average_score_per_round')} style={{ cursor: 'pointer' }}>
                      AVG / RND {sortField === 'average_score_per_round' ? (sortAsc ? '▲' : '▼') : ''}
                    </th>
                    <th onClick={() => handleSort('wins')} style={{ cursor: 'pointer' }}>
                      W / T / L {sortField === 'wins' ? (sortAsc ? '▲' : '▼') : ''}
                    </th>
                    <th onClick={() => handleSort('cooperation_rate')} style={{ cursor: 'pointer' }}>
                      COOP % {sortField === 'cooperation_rate' ? (sortAsc ? '▲' : '▼') : ''}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {sortedLeaderboard.map((row: LeaderboardRow) => {
                    const isSelected = selectedAgentId === row.agent_id
                    return (
                      <tr
                        key={row.agent_id}
                        className={`${row.rank <= 3 ? 'top-rank-row' : ''} ${isSelected ? 'row-selected' : ''}`}
                        onClick={() => setSelectedAgentId(row.agent_id)}
                        style={{ cursor: 'pointer' }}
                      >
                        <td className="mono rank-cell">
                          {row.rank === 1 ? '🥇' : row.rank === 2 ? '🥈' : row.rank === 3 ? '🥉' : `#${row.rank}`}
                        </td>
                        <td className="mono agent-cell">
                          <span className="font-bold">{row.agent_id}</span>
                        </td>
                        <td>{row.strategy_name}</td>
                        <td className="mono score-cell font-bold text-cyan">{row.total_score}</td>
                        <td className="mono">{row.average_score_per_round.toFixed(2)}</td>
                        <td className="mono text-muted">
                          {row.wins}/{row.ties}/{row.losses}
                        </td>
                        <td className="mono text-gold">{(row.cooperation_rate * 100).toFixed(1)}%</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Selected Agent Performance Drilldown Card */}
          {result && selectedAgentRow && (
            <div className="agent-detail-drawer hud-panel">
              <div className="drawer-header">
                <div>
                  <span className="badge badge-gold">INSPECTED AGENT: {selectedAgentRow.agent_id}</span>
                  <span className="mono text-muted ml-2">({selectedAgentRow.strategy_name})</span>
                </div>
                <div className="mono text-xs text-muted">
                  RANK #{selectedAgentRow.rank} | TOTAL: {selectedAgentRow.total_score} PTS | COOP: {(selectedAgentRow.cooperation_rate * 100).toFixed(1)}%
                </div>
              </div>

              <div className="rival-match-cards-grid">
                {selectedAgentMatches.map((m, idx) => {
                  const isFirst = m.first_agent_id === selectedAgentRow.agent_id
                  const rivalId = isFirst ? m.second_agent_id : m.first_agent_id
                  const myScore = isFirst ? m.first_score : m.second_score
                  const rivalScore = isFirst ? m.second_score : m.first_score
                  const myCoop = isFirst ? m.first_cooperation_rate : m.second_cooperation_rate
                  const rivalCoop = isFirst ? m.second_cooperation_rate : m.first_cooperation_rate

                  let outcomeBadge = <span className="badge badge-green">🏆 WIN</span>
                  if (myScore < rivalScore) {
                    outcomeBadge = <span className="badge badge-fire">❌ LOSS</span>
                  } else if (myScore === rivalScore) {
                    outcomeBadge = <span className="badge badge-gold">🤝 TIE</span>
                  }

                  return (
                    <div key={idx} className="rival-match-card">
                      <div className="rival-card-top">
                        <span className="mono font-bold">VS {rivalId}</span>
                        {outcomeBadge}
                      </div>
                      <div className="rival-scores mono">
                        <span className="text-cyan font-bold">{myScore} pts</span>
                        <span className="text-muted"> - </span>
                        <span className="text-muted">{rivalScore} pts</span>
                      </div>
                      <div className="rival-coop mono text-xs text-muted">
                        Coop: {(myCoop * 100).toFixed(0)}% vs {(rivalCoop * 100).toFixed(0)}%
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
