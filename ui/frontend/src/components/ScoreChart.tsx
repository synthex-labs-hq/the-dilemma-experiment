import React from 'react'
import type { RoundTelemetry } from '../api/client'

interface ScoreChartProps {
  rounds: RoundTelemetry[]
  currentRoundIndex: number
  onSelectRound?: (index: number) => void
  nameA: string
  nameB: string
}

export const ScoreChart: React.FC<ScoreChartProps> = ({
  rounds,
  currentRoundIndex,
  onSelectRound,
  nameA,
  nameB,
}) => {
  if (!rounds || rounds.length === 0) return null

  const width = 640
  const height = 180
  const padding = { top: 20, right: 30, bottom: 30, left: 45 }

  const innerWidth = width - padding.left - padding.right
  const innerHeight = height - padding.top - padding.bottom

  // Calculate maximum score
  const maxScore = Math.max(
    ...rounds.map((r) => Math.max(r.cumulative_a, r.cumulative_b)),
    10
  )

  const xScale = (roundNum: number) => {
    if (rounds.length <= 1) return padding.left
    return padding.left + ((roundNum - 1) / (rounds.length - 1)) * innerWidth
  }

  const yScale = (score: number) => {
    return padding.top + innerHeight - (score / maxScore) * innerHeight
  }

  // Generate SVG path for Agent A
  const pathA = rounds.reduce((acc, r, i) => {
    const x = xScale(r.round_number)
    const y = yScale(r.cumulative_a)
    return i === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`
  }, '')

  // Generate SVG path for Agent B
  const pathB = rounds.reduce((acc, r, i) => {
    const x = xScale(r.round_number)
    const y = yScale(r.cumulative_b)
    return i === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`
  }, '')

  // Active round coordinates
  const activeRound = rounds[currentRoundIndex] || rounds[rounds.length - 1]
  const activeX = xScale(activeRound.round_number)
  const activeYA = yScale(activeRound.cumulative_a)
  const activeYB = yScale(activeRound.cumulative_b)

  return (
    <div className="score-chart-wrapper">
      <div className="chart-legend mono">
        <span className="legend-item text-cyan">
          <span className="legend-line line-cyan"></span>
          {nameA} ({activeRound.cumulative_a} pts)
        </span>
        <span className="legend-item text-gold">
          <span className="legend-line line-gold"></span>
          {nameB} ({activeRound.cumulative_b} pts)
        </span>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="score-chart-svg"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <linearGradient id="gradCyan" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent-cyan)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="var(--accent-cyan)" stopOpacity="0.0" />
          </linearGradient>
          <linearGradient id="gradGold" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent-gold)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="var(--accent-gold)" stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal gridlines */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
          const y = padding.top + innerHeight * (1 - pct)
          const val = Math.round(maxScore * pct)
          return (
            <g key={pct}>
              <line
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                stroke="var(--border-subtle)"
                strokeDasharray="3 3"
              />
              <text
                x={padding.left - 8}
                y={y + 4}
                textAnchor="end"
                className="chart-axis-text mono"
              >
                {val}
              </text>
            </g>
          )
        })}

        {/* Vertical active round cursor */}
        <line
          x1={activeX}
          y1={padding.top}
          x2={activeX}
          y2={padding.top + innerHeight}
          stroke="rgba(255, 255, 255, 0.4)"
          strokeWidth="1.5"
          strokeDasharray="2 2"
        />

        {/* Path for Agent B */}
        <path
          d={pathB}
          fill="none"
          stroke="var(--accent-gold)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Path for Agent A */}
        <path
          d={pathA}
          fill="none"
          stroke="var(--accent-cyan)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {rounds.map((r, i) => {
          const x = xScale(r.round_number)
          const isSelected = i === currentRoundIndex
          return (
            <g
              key={r.round_number}
              onClick={() => onSelectRound && onSelectRound(i)}
              style={{ cursor: 'pointer' }}
            >
              <circle
                cx={x}
                cy={yScale(r.cumulative_a)}
                r={isSelected ? 5 : 2.5}
                fill={isSelected ? '#FFFFFF' : 'var(--accent-cyan)'}
                stroke="var(--bg-primary)"
                strokeWidth="1.5"
              />
              <circle
                cx={x}
                cy={yScale(r.cumulative_b)}
                r={isSelected ? 5 : 2.5}
                fill={isSelected ? '#FFFFFF' : 'var(--accent-gold)'}
                stroke="var(--bg-primary)"
                strokeWidth="1.5"
              />
            </g>
          )
        })}

        {/* Active round halo rings */}
        <circle
          cx={activeX}
          cy={activeYA}
          r="7"
          fill="none"
          stroke="var(--accent-cyan)"
          strokeWidth="2"
          className="pulse-halo"
        />
        <circle
          cx={activeX}
          cy={activeYB}
          r="7"
          fill="none"
          stroke="var(--accent-gold)"
          strokeWidth="2"
          className="pulse-halo"
        />

        {/* X-axis round indicators */}
        {rounds
          .filter((_, idx) => idx === 0 || idx === rounds.length - 1 || idx % Math.ceil(rounds.length / 5) === 0)
          .map((r) => (
            <text
              key={r.round_number}
              x={xScale(r.round_number)}
              y={height - 8}
              textAnchor="middle"
              className="chart-axis-text mono"
            >
              R{r.round_number}
            </text>
          ))}
      </svg>
    </div>
  )
}
