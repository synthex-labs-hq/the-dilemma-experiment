import React, { useEffect, useState } from 'react'
import {
  simulateCommons,
  type CommonsAgentLeaderboard,
  type CommonsRoundTelemetry,
  type CommonsSimResponse,
} from '../api/client'

interface CommonsResourceLabProps {
  onClose?: () => void
}

export const CommonsResourceLab: React.FC<CommonsResourceLabProps> = ({ onClose }) => {
  const [sustainableCount, setSustainableCount] = useState<number>(3)
  const [overharvesterCount, setOverharvesterCount] = useState<number>(2)
  const [sanctionerCount, setSanctionerCount] = useState<number>(3)
  const [bystanderCount, setBystanderCount] = useState<number>(1)
  const [sanctionsEnabled, setSanctionsEnabled] = useState<boolean>(true)
  const [rounds, setRounds] = useState<number>(10)
  const [initialStock, setInitialStock] = useState<number>(80)
  const [capacity, setCapacity] = useState<number>(100)
  const [loading, setLoading] = useState<boolean>(false)
  const [simData, setSimData] = useState<CommonsSimResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleRunSimulation = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await simulateCommons({
        sustainable_count: sustainableCount,
        overharvester_count: overharvesterCount,
        sanctioner_count: sanctionerCount,
        freerider_bystander_count: bystanderCount,
        rounds,
        initial_stock: initialStock,
        capacity,
        regeneration_rate: 0.15,
        sanctions_enabled: sanctionsEnabled,
      })
      setSimData(res)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Commons simulation failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    handleRunSimulation()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sanctionsEnabled])

  // Helper for CPR Stock SVG Curve
  const renderStockCurve = (history: CommonsRoundTelemetry[]) => {
    if (!history || history.length === 0) return null

    const width = 560
    const height = 180
    const pad = { top: 20, right: 20, bottom: 30, left: 45 }
    const innerW = width - pad.left - pad.right
    const innerH = height - pad.top - pad.bottom

    const maxStock = Math.max(capacity, ...history.map((h) => h.stock), 10)

    const xScale = (roundNum: number) => {
      if (history.length <= 1) return pad.left
      return pad.left + ((roundNum - 1) / (history.length - 1)) * innerW
    }

    const yScale = (val: number) => {
      return pad.top + innerH - (val / maxStock) * innerH
    }

    const pathData = history.reduce((acc, h, i) => {
      const x = xScale(h.round)
      const y = yScale(h.stock)
      return i === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`
    }, '')

    // Area fill path
    const lastX = xScale(history[history.length - 1].round)
    const firstX = xScale(history[0].round)
    const baseY = yScale(0)
    const areaPath = `${pathData} L ${lastX} ${baseY} L ${firstX} ${baseY} Z`

    const isDepleted = history[history.length - 1].stock <= 0

    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="stock-chart-svg">
        <defs>
          <linearGradient id="stockAreaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={isDepleted ? 'var(--accent-red)' : 'var(--accent-green)'} stopOpacity="0.35" />
            <stop offset="100%" stopColor={isDepleted ? 'var(--accent-red)' : 'var(--accent-green)'} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Capacity Guideline */}
        <line
          x1={pad.left}
          y1={yScale(capacity)}
          x2={width - pad.right}
          y2={yScale(capacity)}
          stroke="rgba(255, 255, 255, 0.25)"
          strokeDasharray="3 3"
        />
        <text x={pad.left - 6} y={yScale(capacity) + 4} textAnchor="end" className="chart-axis-text mono">
          K={capacity}
        </text>

        {/* Baseline 0 */}
        <line
          x1={pad.left}
          y1={baseY}
          x2={width - pad.right}
          y2={baseY}
          stroke="var(--border-subtle)"
        />

        {/* Area fill */}
        <path d={areaPath} fill="url(#stockAreaGrad)" />

        {/* Stroke Line */}
        <path
          d={pathData}
          fill="none"
          stroke={isDepleted ? 'var(--accent-red)' : 'var(--accent-green)'}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Points */}
        {history.map((h) => (
          <circle
            key={h.round}
            cx={xScale(h.round)}
            cy={yScale(h.stock)}
            r="3.5"
            fill={isDepleted ? 'var(--accent-red)' : 'var(--accent-green)'}
            stroke="var(--bg-primary)"
            strokeWidth="1.5"
          />
        ))}

        {/* X labels */}
        {history.map((h, i) => {
          if (i === 0 || i === history.length - 1 || i % 2 === 0) {
            return (
              <text key={h.round} x={xScale(h.round)} y={height - 8} textAnchor="middle" className="chart-axis-text mono">
                R{h.round}
              </text>
            )
          }
          return null
        })}
      </svg>
    )
  }

  return (
    <div className="lab-modal-backdrop">
      <div className="lab-modal-panel hud-panel">
        <div className="lab-modal-header">
          <div>
            <div className="card-top-tag">
              <span className="badge badge-gold">EPISODE 08 LABORATORY</span>
              <span className="badge badge-cyan">OSTROM INSTITUTIONAL ANALYSIS</span>
            </div>
            <h2 className="gradient-text-gold">THE TRAGEDY OF THE COMMONS & SANCTIONS</h2>
            <p className="text-secondary text-sm">
              Explore how peer sanctions solve the second-order free-rider dilemma and sustain finite common-pool resources.
            </p>
          </div>
          {onClose && (
            <button className="btn btn-ghost btn-close-modal" onClick={onClose}>
              ✕
            </button>
          )}
        </div>

        <div className="commons-lab-grid-layout">
          {/* Config Panel */}
          <div className="hud-panel commons-config-panel">
            <div className="panel-title-bar">
              <h3>POPULATION & OSTROM RULES</h3>
            </div>

            <div className="caste-stepper-list">
              <div className="stepper-item">
                <div className="stepper-meta">
                  <span className="font-bold text-green">Sustainable Harvesters</span>
                  <span className="mono text-xs text-muted">Harvests sustainably, shares goods</span>
                </div>
                <div className="stepper-controls">
                  <button className="btn-stepper" onClick={() => setSustainableCount(Math.max(0, sustainableCount - 1))}>
                    -
                  </button>
                  <span className="mono stepper-val">{sustainableCount}</span>
                  <button className="btn-stepper" onClick={() => setSustainableCount(sustainableCount + 1)}>
                    +
                  </button>
                </div>
              </div>

              <div className="stepper-item">
                <div className="stepper-meta">
                  <span className="font-bold text-red">Greedy Over-Harvesters</span>
                  <span className="mono text-xs text-muted">Depletes pool, free-rides</span>
                </div>
                <div className="stepper-controls">
                  <button className="btn-stepper" onClick={() => setOverharvesterCount(Math.max(0, overharvesterCount - 1))}>
                    -
                  </button>
                  <span className="mono stepper-val">{overharvesterCount}</span>
                  <button className="btn-stepper" onClick={() => setOverharvesterCount(overharvesterCount + 1)}>
                    +
                  </button>
                </div>
              </div>

              <div className="stepper-item">
                <div className="stepper-meta">
                  <span className="font-bold text-cyan">Ostrom Sanctioners</span>
                  <span className="mono text-xs text-muted">Altruistic punisher (incurs costs to fine)</span>
                </div>
                <div className="stepper-controls">
                  <button className="btn-stepper" onClick={() => setSanctionerCount(Math.max(0, sanctionerCount - 1))}>
                    -
                  </button>
                  <span className="mono stepper-val">{sanctionerCount}</span>
                  <button className="btn-stepper" onClick={() => setSanctionerCount(sanctionerCount + 1)}>
                    +
                  </button>
                </div>
              </div>

              <div className="stepper-item">
                <div className="stepper-meta">
                  <span className="font-bold text-gold">2nd-Order Free-Riders</span>
                  <span className="mono text-xs text-muted">Cooperates, but avoids enforcement costs</span>
                </div>
                <div className="stepper-controls">
                  <button className="btn-stepper" onClick={() => setBystanderCount(Math.max(0, bystanderCount - 1))}>
                    -
                  </button>
                  <span className="mono stepper-val">{bystanderCount}</span>
                  <button className="btn-stepper" onClick={() => setBystanderCount(bystanderCount + 1)}>
                    +
                  </button>
                </div>
              </div>
            </div>

            {/* Ostrom Sanctions Toggle */}
            <div className="sanction-toggle-box mt-3">
              <label className="mono input-label">OSTROM SANCTION REGIME</label>
              <div className="toggle-btn-group">
                <button
                  className={`btn ${sanctionsEnabled ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setSanctionsEnabled(true)}
                >
                  ⚖️ SANCTIONS ACTIVE
                </button>
                <button
                  className={`btn ${!sanctionsEnabled ? 'btn-destructive' : 'btn-ghost'}`}
                  onClick={() => setSanctionsEnabled(false)}
                >
                  🚫 LAISSEZ-FAIRE (NONE)
                </button>
              </div>
            </div>

            <div className="control-group mt-3">
              <label className="mono input-label">ROUNDS: {rounds}</label>
              <input
                type="range"
                min="5"
                max="25"
                step="5"
                value={rounds}
                onChange={(e) => setRounds(Number(e.target.value))}
                className="hud-slider"
              />
            </div>

            <div className="control-group mt-2">
              <label className="mono input-label">INITIAL STOCK: {initialStock}</label>
              <input
                type="range"
                min="20"
                max="150"
                step="10"
                value={initialStock}
                onChange={(e) => setInitialStock(Number(e.target.value))}
                className="hud-slider"
              />
            </div>

            <div className="control-group mt-2">
              <label className="mono input-label">CARRYING CAPACITY (K): {capacity}</label>
              <input
                type="range"
                min="50"
                max="200"
                step="25"
                value={capacity}
                onChange={(e) => setCapacity(Number(e.target.value))}
                className="hud-slider"
              />
            </div>

            <button
              className="btn btn-primary w-full mt-3"
              onClick={handleRunSimulation}
              disabled={loading}
            >
              {loading ? 'SIMULATING COMMONS...' : '🌾 SIMULATE CPR POOL'}
            </button>

            {error && <div className="error-banner mono mt-2">{error}</div>}
          </div>

          {/* Results Panel */}
          {simData && (
            <div className="commons-results-column">
              {/* Stock Trajectory Graph */}
              <div className="hud-panel stock-graph-panel">
                <div className="panel-title-bar">
                  <div>
                    <h3>COMMON POOL RESOURCE STOCK (R_t)</h3>
                    <span className="mono text-muted text-xs">
                      INITIAL: {simData.initial_stock} | FINAL: {simData.final_stock}
                    </span>
                  </div>
                  <span className={`badge ${simData.is_depleted ? 'badge-fire' : 'badge-green'}`}>
                    {simData.is_depleted ? '⚠️ COMMONS COLLAPSED' : '🌲 SUSTAINABLE HARVEST'}
                  </span>
                </div>

                <div className="stock-chart-container">
                  {renderStockCurve(simData.history)}
                </div>

                <div className="commons-summary-row mt-2">
                  <div className="metric-box">
                    <span className="metric-label mono">TOTAL SANCTIONS</span>
                    <span className="metric-val mono text-cyan">{simData.total_sanctions}</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-label mono">FINES IMPOSED</span>
                    <span className="metric-val mono text-red">${simData.total_fines_imposed.toFixed(1)}</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-label mono">ENFORCEMENT COSTS</span>
                    <span className="metric-val mono text-gold">${simData.total_sanction_costs.toFixed(1)}</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-label mono">COOPERATION RATE</span>
                    <span className="metric-val mono text-green">{(simData.overall_contribution_rate * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>

              {/* Leaderboard Table */}
              <div className="hud-panel mt-3">
                <div className="panel-title-bar">
                  <h3>HARVESTER AGENT AUDIT</h3>
                </div>
                <div className="leaderboard-table-container">
                  <table className="hud-table">
                    <thead>
                      <tr>
                        <th>RANK</th>
                        <th>AGENT</th>
                        <th>STRATEGY</th>
                        <th>NET SCORE</th>
                        <th>CONTRIB</th>
                        <th>FINES PAID</th>
                        <th>COSTS</th>
                      </tr>
                    </thead>
                    <tbody>
                      {simData.leaderboard.map((row: CommonsAgentLeaderboard) => (
                        <tr key={row.agent_id} className={row.rank <= 3 ? 'top-rank-row' : ''}>
                          <td className="mono rank-cell">#{row.rank}</td>
                          <td className="mono agent-cell font-bold">{row.agent_id}</td>
                          <td>{row.strategy_name}</td>
                          <td className="mono score-cell font-bold">{row.total_score.toFixed(1)}</td>
                          <td className="mono text-green">{row.total_contribution.toFixed(1)}</td>
                          <td className="mono text-red">{row.fines_received > 0 ? `-$${row.fines_received.toFixed(1)}` : '$0'}</td>
                          <td className="mono text-gold">{row.costs_paid > 0 ? `-$${row.costs_paid.toFixed(1)}` : '$0'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
