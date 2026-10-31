/**
 * Type definitions and HTTP client for The Dilemma Experiment Simulation API.
 */

export interface StrategyMeta {
  id: string
  name: string
  archetype: string
  episode: number
  category: string
  description: string
  traits: string[]
  is_cognitive: boolean
}

export interface RoundTelemetry {
  round_number: number
  action_a: 'COOPERATE' | 'DEFECT'
  action_b: 'COOPERATE' | 'DEFECT'
  payoff_a: number
  payoff_b: number
  cumulative_a: number
  cumulative_b: number
  message_a?: string | null
  message_b?: string | null
  rationale_a?: string | null
  rationale_b?: string | null
  is_deceptive_a: boolean
  is_deceptive_b: boolean
}

export interface MatchResponse {
  strategy_a: StrategyMeta
  strategy_b: StrategyMeta
  score_a: number
  score_b: number
  cooperation_rate_a: number
  cooperation_rate_b: number
  deception_rate_a: number
  deception_rate_b: number
  rounds: RoundTelemetry[]
}

export interface MatchRequest {
  strategy_a: string
  strategy_b: string
  round_count: number
  noise?: number
  seed?: number | null
}

export interface LeaderboardRow {
  rank: number
  agent_id: string
  strategy_id: string
  strategy_name: string
  total_score: number
  average_score_per_round: number
  wins: number
  ties: number
  losses: number
  cooperation_rate: number
}

export interface TournamentResponse {
  total_agents: number
  total_matches: number
  population_cooperation_rate: number
  leaderboard: LeaderboardRow[]
}

export interface TournamentSelection {
  strategy_id: string
  count: number
}

export interface TournamentRequest {
  selections: TournamentSelection[]
  rounds_per_match: number
  noise?: number
  seed?: number | null
}

export async function fetchHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch('/api/health')
  if (!res.ok) throw new Error('API server unavailable')
  return res.json()
}

export async function fetchStrategies(): Promise<StrategyMeta[]> {
  const res = await fetch('/api/strategies')
  if (!res.ok) throw new Error('Failed to fetch strategies')
  const data = await res.json()
  return data.strategies
}

export async function simulateMatch(req: MatchRequest): Promise<MatchResponse> {
  const res = await fetch('/api/simulate/match', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Simulation failed' }))
    throw new Error(err.detail || 'Simulation failed')
  }
  return res.json()
}

export async function simulateTournament(req: TournamentRequest): Promise<TournamentResponse> {
  const res = await fetch('/api/simulate/tournament', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Tournament failed' }))
    throw new Error(err.detail || 'Tournament failed')
  }
  return res.json()
}
