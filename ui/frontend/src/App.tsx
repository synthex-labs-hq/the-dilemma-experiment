import { useEffect, useState } from 'react'
import { fetchHealth, fetchStrategies, type StrategyMeta } from './api/client'
import { Navbar } from './components/Navbar'
import { NavigationTabs, type TabId } from './components/NavigationTabs'
import { ArenaView } from './views/ArenaView'
import { TournamentsView } from './views/TournamentsView'
import { EpisodesView } from './views/EpisodesView'
import { SandboxView } from './views/SandboxView'
import './App.css'

const FALLBACK_STRATEGIES: StrategyMeta[] = [
  {
    id: 'tit_for_tat',
    name: 'Tit-for-Tat',
    archetype: 'Reciprocal',
    episode: 2,
    category: 'Classic',
    description: 'Cooperates on round 1, then mimics opponent\'s previous action. The bedrock of evolutionary reciprocity.',
    traits: ['Nice', 'Retaliatory', 'Forgiving', 'Clear'],
    is_cognitive: false,
  },
  {
    id: 'always_defect',
    name: 'Always Defect',
    archetype: 'Exploiter',
    episode: 1,
    category: 'Classic',
    description: 'Defects unconditionally on every turn. Nash equilibrium in single-shot Prisoner\'s Dilemma.',
    traits: ['Malicious', 'Exploitative'],
    is_cognitive: false,
  },
  {
    id: 'always_cooperate',
    name: 'Always Cooperate',
    archetype: 'Altruist',
    episode: 1,
    category: 'Classic',
    description: 'Cooperates unconditionally on every round regardless of opponent betrayal.',
    traits: ['Naive', 'Vulnerable'],
    is_cognitive: false,
  },
  {
    id: 'win_stay_lose_shift',
    name: 'Win-Stay, Lose-Shift (Pavlov)',
    archetype: 'Adaptive',
    episode: 3,
    category: 'Noise-Resilient',
    description: 'Repeats action if round payoff was high (T or R); switches action if payoff was low (P or S). Corrects noise.',
    traits: ['Noise-Tolerant', 'Exploits Saps'],
    is_cognitive: false,
  },
  {
    id: 'generous_tit_for_tat',
    name: 'Generous Tit-for-Tat',
    archetype: 'Forgiving Reciprocal',
    episode: 3,
    category: 'Noise-Resilient',
    description: 'Mimics opponent but forgives defection with p=1/3 probability, breaking infinite retaliation loops.',
    traits: ['Stochastic', 'Forgiving', 'Vendetta-Breaker'],
    is_cognitive: false,
  },
  {
    id: 'grim_trigger',
    name: 'Grim Trigger',
    archetype: 'Unforgiving',
    episode: 2,
    category: 'Classic',
    description: 'Cooperates until the opponent defects even once, then defects forever without remorse.',
    traits: ['Punitive', 'Unforgiving'],
    is_cognitive: false,
  },
  {
    id: 'extortioner',
    name: 'Extortioner (ZD)',
    archetype: 'Asymmetric Dictator',
    episode: 9,
    category: 'Zero-Determinant',
    description: 'Unilaterally enforces an unfair 3:1 surplus sharing ratio using Press-Dyson linear constraints.',
    traits: ['Mathematical Dictator', 'Coercive'],
    is_cognitive: false,
  },
  {
    id: 'generous_zd',
    name: 'Generous ZD',
    archetype: 'Generous Dictator',
    episode: 9,
    category: 'Zero-Determinant',
    description: 'Ensures the co-player receives an advantage over the baseline, fostering cooperative evolutionary clusters.',
    traits: ['Generous', 'Evolutionary Robust'],
    is_cognitive: false,
  },
]

export function App() {
  const [activeTab, setActiveTab] = useState<TabId>('arena')
  const [speed, setSpeed] = useState<'1x' | '5x' | 'max'>('1x')
  const [isOnline, setIsOnline] = useState<boolean>(false)
  const [strategies, setStrategies] = useState<StrategyMeta[]>(FALLBACK_STRATEGIES)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    let mounted = true

    const checkServer = async () => {
      try {
        await fetchHealth()
        if (mounted) setIsOnline(true)

        const strats = await fetchStrategies()
        if (mounted && strats && strats.length > 0) {
          setStrategies(strats)
        }
      } catch {
        if (mounted) setIsOnline(false)
      } finally {
        if (mounted) setLoading(false)
      }
    }

    checkServer()
    const timer = setInterval(checkServer, 6000)

    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [])

  return (
    <div className="app-shell">
      {/* Top Cybernetic HUD Navbar */}
      <Navbar speed={speed} setSpeed={setSpeed} isOnline={isOnline} />

      {/* Main Tab Bar */}
      <NavigationTabs activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* Primary Workspace View Area */}
      <main className="main-content-area">
        {loading && strategies.length === 0 ? (
          <div className="loading-container mono">
            <span className="pulse-indicator"></span>
            <span>INITIALIZING SIMULATION MATRIX...</span>
          </div>
        ) : (
          <>
            {activeTab === 'arena' && <ArenaView strategies={strategies} speed={speed} />}
            {activeTab === 'tournaments' && <TournamentsView strategies={strategies} />}
            {activeTab === 'episodes' && <EpisodesView />}
            {activeTab === 'sandbox' && <SandboxView />}
          </>
        )}
      </main>

      {/* Cybernetic HUD Footer */}
      <footer className="footer-hud mono">
        <div className="footer-inner">
          <div className="footer-left">
            <span>THE DILEMMA EXPERIMENT</span>
            <span className="footer-sep">/</span>
            <span className="text-muted">10-EPISODE EVOLUTIONARY GAME THEORY SUITE</span>
          </div>
          <div className="footer-center text-cyan">
            {isOnline ? 'SIMULATION CORE: CONNECTED' : 'STANDBY MODE (LOCAL WORKSPACE)'}
          </div>
          <div className="footer-right text-muted">
            <span>24+ STRATEGIES</span>
            <span className="footer-sep">/</span>
            <span>PYTHON 3.12 + FASTAPI + REACT 19</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
