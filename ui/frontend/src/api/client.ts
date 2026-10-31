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

export interface PairwiseMatchSummary {
  first_agent_id: string
  second_agent_id: string
  first_score: number
  second_score: number
  winner_id: string | null
  rounds_played: number
  first_cooperation_rate: number
  second_cooperation_rate: number
}

export interface TournamentResponse {
  total_agents: number
  total_matches: number
  population_cooperation_rate: number
  leaderboard: LeaderboardRow[]
  pairwise_matches?: PairwiseMatchSummary[]
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

// --- Spatial Simulation Types ---

export interface SpatialGenerationTelemetry {
  generation: number
  distribution: Record<string, number>
  proportions: Record<string, number>
  grid_cells: string[]
  clustering_ratio: number
  is_fixated: boolean
  dominant_strategy: string
}

export interface SpatialSimResponse {
  width: number
  height: number
  total_nodes: number
  preset: string
  generations: SpatialGenerationTelemetry[]
}

export interface SpatialSimRequest {
  width?: number
  height?: number
  preset: string
  generations?: number
  coop_strategy?: string
  defect_strategy?: string
}

export async function simulateSpatial(req: SpatialSimRequest): Promise<SpatialSimResponse> {
  const res = await fetch('/api/simulate/spatial', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Spatial simulation failed' }))
    throw new Error(err.detail || 'Spatial simulation failed')
  }
  return res.json()
}

// --- Commons Simulation Types ---

export interface CommonsRoundTelemetry {
  round: number
  stock: number
  mean_contribution: number
  cooperation_rate: number
  sanctions_applied: number
}

export interface CommonsAgentLeaderboard {
  rank: number
  agent_id: string
  strategy_name: string
  total_score: number
  average_score: number
  total_contribution: number
  sanctions_inflicted: number
  fines_received: number
  costs_paid: number
}

export interface CommonsSimResponse {
  total_rounds: number
  initial_stock: number
  final_stock: number
  is_depleted: boolean
  overall_contribution_rate: number
  total_sanctions: number
  total_fines_imposed: number
  total_sanction_costs: number
  history: CommonsRoundTelemetry[]
  leaderboard: CommonsAgentLeaderboard[]
}

export interface CommonsSimRequest {
  sustainable_count?: number
  overharvester_count?: number
  sanctioner_count?: number
  freerider_bystander_count?: number
  rounds?: number
  initial_stock?: number
  capacity?: number
  regeneration_rate?: number
  sanctions_enabled?: boolean
  graduated_sanctions?: boolean
}

export async function simulateCommons(req: CommonsSimRequest): Promise<CommonsSimResponse> {
  const res = await fetch('/api/simulate/commons', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Commons simulation failed' }))
    throw new Error(err.detail || 'Commons simulation failed')
  }
  return res.json()
}

// --- The Gauntlet Simulation Types ---

export interface GauntletRequest {
  name: string
  opening_move: 'COOPERATE' | 'DEFECT'
  retaliation: string
  forgiveness: number
  rounds_per_opponent?: number
}

export interface GauntletDuelResult {
  opponent_id: string
  opponent_name: string
  opponent_archetype: string
  custom_score: number
  opponent_score: number
  outcome: 'WIN' | 'TIE' | 'LOSS'
  custom_coop_rate: number
  opponent_coop_rate: number
  rounds: RoundTelemetry[]
}

export interface GauntletScorecard {
  niceness: number
  retaliation: number
  forgiveness: number
  exploitation_resistance: number
  total_score: number
  max_possible_score: number
  overall_win_rate: number
  archetype_badge: string
  verdict: string
}

export interface GauntletResponse {
  custom_name: string
  scorecard: GauntletScorecard
  duels: GauntletDuelResult[]
}

export async function simulateGauntlet(req: GauntletRequest): Promise<GauntletResponse> {
  const res = await fetch('/api/simulate/gauntlet', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Gauntlet simulation failed' }))
    throw new Error(err.detail || 'Gauntlet simulation failed')
  }
  return res.json()
}


