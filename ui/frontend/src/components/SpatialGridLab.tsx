import React, { useEffect, useState } from 'react'
import {
  simulateSpatial,
  type SpatialGenerationTelemetry,
  type SpatialSimResponse,
} from '../api/client'

interface SpatialGridLabProps {
  onClose?: () => void
}

export const SpatialGridLab: React.FC<SpatialGridLabProps> = ({ onClose }) => {
  const [preset, setPreset] = useState<'oasis' | 'conquest' | 'random' | 'split'>('oasis')
  const [generations, setGenerations] = useState<number>(8)
  const [width, setWidth] = useState<number>(10)
  const [height, setHeight] = useState<number>(10)
  const [loading, setLoading] = useState<boolean>(false)
  const [simData, setSimData] = useState<SpatialSimResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Playback state
  const [currentGenIdx, setCurrentGenIdx] = useState<number>(0)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)

  const runSimulation = async () => {
    setLoading(true)
    setError(null)
    setIsPlaying(false)
    try {
      const res = await simulateSpatial({
        width,
        height,
        preset,
        generations,
      })
      setSimData(res)
      setCurrentGenIdx(0)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Spatial simulation failed')
    } finally {
      setLoading(false)
    }
  }

  // Run initial simulation on mount
  useEffect(() => {
    runSimulation()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preset])

  // Playback loop
  useEffect(() => {
    if (!isPlaying || !simData || simData.generations.length === 0) return

    const timer = setInterval(() => {
      setCurrentGenIdx((prev) => {
        if (prev >= simData.generations.length - 1) {
          setIsPlaying(false)
          return prev
        }
        return prev + 1
      })
    }, 600)

    return () => clearInterval(timer)
  }, [isPlaying, simData])

  const activeGen: SpatialGenerationTelemetry | undefined = simData?.generations[currentGenIdx]

  const getCellColor = (stratName: string) => {
    if (stratName.includes('Cooperate')) return 'var(--accent-green)'
    if (stratName.includes('TitForTat')) return 'var(--accent-cyan)'
    if (stratName.includes('Defect')) return 'var(--accent-red)'
    return 'var(--accent-gold)'
  }

  const getCellLabel = (stratName: string) => {
    if (stratName.includes('Cooperate')) return 'C'
    if (stratName.includes('TitForTat')) return 'TFT'
    if (stratName.includes('Defect')) return 'D'
    return '?'
  }

  return (
    <div className="lab-modal-backdrop">
      <div className="lab-modal-panel hud-panel">
        <div className="lab-modal-header">
          <div>
            <div className="card-top-tag">
              <span className="badge badge-cyan">EPISODE 05 LABORATORY</span>
              <span className="badge badge-gold">2D TOROIDAL TOPOLOGY</span>
            </div>
            <h2 className="gradient-text-cyan">THE FORTRESS OF GEOGRAPHY</h2>
            <p className="text-secondary text-sm">
              Discover how spatial clustering shields cooperators from defector exploitation on a 2D toroidal lattice.
            </p>
          </div>
          {onClose && (
            <button className="btn btn-ghost btn-close-modal" onClick={onClose}>
              ✕
            </button>
          )}
        </div>

        {/* Controls Bar */}
        <div className="lab-controls-bar">
          <div className="preset-selector-group">
            <span className="mono text-xs text-muted">PRESET TOPOLOGY:</span>
            <div className="btn-group">
              <button
                className={`btn btn-xs ${preset === 'oasis' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setPreset('oasis')}
              >
                🛡️ Cooperator Oasis
              </button>
              <button
                className={`btn btn-xs ${preset === 'conquest' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setPreset('conquest')}
              >
                ⚔️ Reciprocal Conquest
              </button>
              <button
                className={`btn btn-xs ${preset === 'random' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setPreset('random')}
              >
                🎲 Random 50/50
              </button>
              <button
                className={`btn btn-xs ${preset === 'split' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setPreset('split')}
              >
                🌗 Split Half
              </button>
            </div>
          </div>

          <div className="grid-dim-group mono text-xs">
            <span>GRID:</span>
            <select
              className="hud-select-xs mono"
              value={width}
              onChange={(e) => {
                const s = Number(e.target.value)
                setWidth(s)
                setHeight(s)
              }}
            >
              <option value="8">8x8</option>
              <option value="10">10x10</option>
              <option value="12">12x12</option>
              <option value="15">15x15</option>
            </select>

            <span className="ml-2">GENS:</span>
            <select
              className="hud-select-xs mono"
              value={generations}
              onChange={(e) => setGenerations(Number(e.target.value))}
            >
              <option value="6">6 Gens</option>
              <option value="8">8 Gens</option>
              <option value="12">12 Gens</option>
              <option value="16">16 Gens</option>
            </select>

            <button
              className="btn btn-primary btn-xs ml-2"
              onClick={runSimulation}
              disabled={loading}
            >
              {loading ? 'SIMULATING...' : '🔄 RE-RUN'}
            </button>
          </div>
        </div>

        {error && <div className="error-banner mono">{error}</div>}

        {/* Main Grid & Telemetry Content */}
        {simData && activeGen && (
          <div className="spatial-lab-grid-layout">
            {/* Visual Toroidal Grid */}
            <div className="grid-canvas-container">
              <div
                className="toroidal-matrix-display"
                style={{
                  gridTemplateColumns: `repeat(${simData.width}, 1fr)`,
                }}
              >
                {activeGen.grid_cells.map((strat, idx) => {
                  const x = idx % simData.width
                  const y = Math.floor(idx / simData.width)
                  return (
                    <div
                      key={idx}
                      className="grid-cell-tile"
                      style={{
                        backgroundColor: `${getCellColor(strat)}22`,
                        borderColor: getCellColor(strat),
                        color: getCellColor(strat),
                      }}
                      title={`Node (${x}, ${y}): ${strat}`}
                    >
                      <span className="tile-label mono">{getCellLabel(strat)}</span>
                    </div>
                  )
                })}
              </div>

              {/* Playback Controls */}
              <div className="playback-toolbar mt-3">
                <div className="playback-btns">
                  <button
                    className="btn btn-ghost btn-playback"
                    onClick={() => {
                      setCurrentGenIdx(0)
                      setIsPlaying(false)
                    }}
                  >
                    ⏮
                  </button>
                  <button
                    className="btn btn-ghost btn-playback"
                    onClick={() => {
                      setCurrentGenIdx((p) => Math.max(0, p - 1))
                      setIsPlaying(false)
                    }}
                  >
                    ◀
                  </button>
                  <button
                    className="btn btn-primary btn-playback-play"
                    onClick={() => {
                      if (currentGenIdx >= simData.generations.length - 1) {
                        setCurrentGenIdx(0)
                      }
                      setIsPlaying(!isPlaying)
                    }}
                  >
                    {isPlaying ? '⏸ PAUSE' : '▶ PLAY GENERATIONS'}
                  </button>
                  <button
                    className="btn btn-ghost btn-playback"
                    onClick={() => {
                      setCurrentGenIdx((p) => Math.min(simData.generations.length - 1, p + 1))
                      setIsPlaying(false)
                    }}
                  >
                    ▶
                  </button>
                  <button
                    className="btn btn-ghost btn-playback"
                    onClick={() => {
                      setCurrentGenIdx(simData.generations.length - 1)
                      setIsPlaying(false)
                    }}
                  >
                    ⏭
                  </button>
                </div>

                <div className="scrub-container">
                  <input
                    type="range"
                    min="0"
                    max={simData.generations.length - 1}
                    value={currentGenIdx}
                    onChange={(e) => {
                      setCurrentGenIdx(Number(e.target.value))
                      setIsPlaying(false)
                    }}
                    className="hud-slider scrub-slider"
                  />
                </div>
              </div>
            </div>

            {/* Scientific Telemetry Panel */}
            <div className="spatial-telemetry-side">
              <div className="hud-panel telemetry-card">
                <div className="card-top-tag">
                  <span className="badge badge-cyan mono">GENERATION {activeGen.generation}</span>
                  <span className={`badge ${activeGen.is_fixated ? 'badge-gold' : 'badge-green'}`}>
                    {activeGen.is_fixated ? '🔒 FIXATED' : '⚡ EVOLVING'}
                  </span>
                </div>

                <div className="telemetry-metric-group">
                  <div className="telemetry-metric">
                    <span className="mono text-xs text-muted">DOMINANT STRATEGY</span>
                    <span className="mono font-bold text-cyan">{activeGen.dominant_strategy}</span>
                  </div>

                  <div className="telemetry-metric">
                    <span className="mono text-xs text-muted">COOPERATOR CLUSTERING RATIO (C_ratio)</span>
                    <div className="clustering-val-row mono">
                      <span className="metric-val text-green">{(activeGen.clustering_ratio * 100).toFixed(1)}%</span>
                      <span className="text-xs text-muted">
                        {activeGen.clustering_ratio >= 0.5 ? '🛡️ High Cluster Defense' : '⚠️ Vulnerable'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Population Proportion Bar */}
                <div className="population-share-section">
                  <span className="mono text-xs text-muted">POPULATION COMPOSITION:</span>
                  <div className="share-bar-container">
                    {Object.entries(activeGen.distribution).map(([strat, count]) => {
                      const pct = (count / simData.total_nodes) * 100
                      return (
                        <div
                          key={strat}
                          className="share-bar-segment"
                          style={{
                            width: `${pct}%`,
                            backgroundColor: getCellColor(strat),
                          }}
                          title={`${strat}: ${count} (${pct.toFixed(1)}%)`}
                        />
                      )
                    })}
                  </div>
                  <div className="share-legend mono text-xs mt-2">
                    {Object.entries(activeGen.distribution).map(([strat, count]) => (
                      <div key={strat} className="legend-row">
                        <span className="legend-dot" style={{ backgroundColor: getCellColor(strat) }}></span>
                        <span>{strat}: {count} ({((count / simData.total_nodes) * 100).toFixed(1)}%)</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="scientific-takeaway-box mt-3 text-xs text-secondary">
                  <strong>The Fortress Effect:</strong> In a well-mixed population (Episode 4), a 9% cooperator minority is exterminated in 3 generations. On this 2D lattice, physical proximity allows cooperators to form an impenetrable self-sustaining cluster.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
