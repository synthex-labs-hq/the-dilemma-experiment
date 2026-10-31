import React from 'react'
import type { LeaderboardRow, PairwiseMatchSummary } from '../api/client'

interface CrossTableMatrixProps {
  leaderboard: LeaderboardRow[]
  pairwiseMatches: PairwiseMatchSummary[]
  selectedAgentId: string | null
  onSelectAgent: (agentId: string) => void
}

export const CrossTableMatrix: React.FC<CrossTableMatrixProps> = ({
  leaderboard,
  pairwiseMatches,
  selectedAgentId,
  onSelectAgent,
}) => {
  if (!leaderboard || leaderboard.length === 0) return null

  // Helper to find match between two agents
  const getMatch = (idA: string, idB: string) => {
    return pairwiseMatches.find(
      (m) =>
        (m.first_agent_id === idA && m.second_agent_id === idB) ||
        (m.first_agent_id === idB && m.second_agent_id === idA)
    )
  }

  return (
    <div className="cross-table-container">
      <div className="cross-table-header-info">
        <span className="mono text-muted">
          HEAD-TO-HEAD CROSS MATRIX (ROWS = PERSPECTIVE AGENT, COLS = OPPONENTS)
        </span>
      </div>

      <div className="table-responsive-scroll">
        <table className="cross-matrix-table hud-table">
          <thead>
            <tr>
              <th className="sticky-corner mono">AGENT</th>
              {leaderboard.map((col) => (
                <th
                  key={col.agent_id}
                  className={`col-header mono ${selectedAgentId === col.agent_id ? 'col-selected' : ''}`}
                  title={`${col.agent_id} (${col.strategy_name})`}
                >
                  <div className="col-header-text">{col.agent_id}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((row) => {
              const isRowSelected = selectedAgentId === row.agent_id
              return (
                <tr key={row.agent_id} className={isRowSelected ? 'row-selected' : ''}>
                  <td
                    className="sticky-left mono row-header-cell"
                    onClick={() => onSelectAgent(row.agent_id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <span className="agent-tag font-bold">{row.agent_id}</span>
                    <span className="strat-subtag text-muted">{row.strategy_name}</span>
                  </td>

                  {leaderboard.map((col) => {
                    if (row.agent_id === col.agent_id) {
                      return (
                        <td key={col.agent_id} className="cross-cell cell-diagonal mono">
                          —
                        </td>
                      )
                    }

                    const match = getMatch(row.agent_id, col.agent_id)
                    if (!match) {
                      return (
                        <td key={col.agent_id} className="cross-cell cell-empty mono">
                          ?
                        </td>
                      )
                    }

                    const isFirst = match.first_agent_id === row.agent_id
                    const myScore = isFirst ? match.first_score : match.second_score
                    const oppScore = isFirst ? match.second_score : match.first_score
                    const myCoop = isFirst ? match.first_cooperation_rate : match.second_cooperation_rate
                    const oppCoop = isFirst ? match.second_cooperation_rate : match.first_cooperation_rate

                    let outcomeClass = 'cell-tie'
                    let outcomeSymbol = '🤝'
                    if (myScore > oppScore) {
                      outcomeClass = 'cell-win'
                      outcomeSymbol = 'W'
                    } else if (myScore < oppScore) {
                      outcomeClass = 'cell-loss'
                      outcomeSymbol = 'L'
                    }

                    return (
                      <td
                        key={col.agent_id}
                        className={`cross-cell ${outcomeClass} mono`}
                        title={`${row.agent_id} vs ${col.agent_id}: ${myScore} - ${oppScore} (${outcomeSymbol}) | Coop: ${(myCoop * 100).toFixed(0)}% vs ${(oppCoop * 100).toFixed(0)}%`}
                        onClick={() => onSelectAgent(row.agent_id)}
                      >
                        <div className="cell-score">
                          {myScore}-{oppScore}
                        </div>
                        <div className="cell-badge-symbol">{outcomeSymbol}</div>
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
