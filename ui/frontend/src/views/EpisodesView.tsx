import React from 'react'

interface EpisodeSummary {
  number: number
  title: string
  subtitle: string
  paradox: string
  keyStrategies: string[]
  status: 'Ready' | 'Lab Module'
}

export const EpisodesView: React.FC = () => {
  const episodes: EpisodeSummary[] = [
    {
      number: 1,
      title: 'Building the Laboratory',
      subtitle: 'The Payoff Matrix & The Prisoner\'s Dilemma',
      paradox: 'Why individual rationality leads to collective ruin (T > R > P > S).',
      keyStrategies: ['Always Cooperate', 'Always Defect'],
      status: 'Ready',
    },
    {
      number: 2,
      title: 'The Tournament',
      subtitle: 'Axelrod\'s Society of Reciprocity',
      paradox: 'Nice, retaliatory, and forgiving agents outperform purely selfish exploiters.',
      keyStrategies: ['Tit-For-Tat', 'Grim Trigger', 'Random'],
      status: 'Ready',
    },
    {
      number: 3,
      title: 'Noise & Forgiveness',
      subtitle: 'The Fragility of Pure Reciprocity',
      paradox: 'When communication is imperfect, pure reciprocity descends into infinite vendettas.',
      keyStrategies: ['Generous TFT', 'Tit-For-Two-Tats', 'Pavlov (WSLS)'],
      status: 'Ready',
    },
    {
      number: 4,
      title: 'Natural Selection & Evolution',
      subtitle: 'Replicator Dynamics & Evolutionary Stability',
      paradox: 'Cooperation can emerge from a tiny cluster and drive defectors into extinction.',
      keyStrategies: ['Darwinian Selection', 'Frequency-Dependent Fitness'],
      status: 'Ready',
    },
    {
      number: 5,
      title: 'Spatial Networks & Topologies',
      subtitle: 'The Fortress of Geography',
      paradox: 'Physical proximity allows cooperators to shield each other on 2D toroidal grids.',
      keyStrategies: ['Toroidal Grid 2D', 'Moore Neighborhoods'],
      status: 'Lab Module',
    },
    {
      number: 6,
      title: 'Indirect Reciprocity & Reputation',
      subtitle: 'Public Ledgers & Moral Systems',
      paradox: 'Cooperation flourishes among strangers through image scoring and stern judging gossip.',
      keyStrategies: ['Image Scorer', 'Stern Judger', 'Hypocrite'],
      status: 'Ready',
    },
    {
      number: 7,
      title: 'Tags, Tribalism & Green Beards',
      subtitle: 'In-Group Favoritism & False Beards',
      paradox: 'Arbitrary markers allow recognition without memory, but invite parasitic chameleons.',
      keyStrategies: ['Strict Tribal', 'Riolo Tolerance', 'False Beard'],
      status: 'Ready',
    },
    {
      number: 8,
      title: 'The Tragedy of the Commons & Sanctions',
      subtitle: 'Elinor Ostrom\'s 8 Principles',
      paradox: 'Altruistic peer punishment solves the second-order free-rider dilemma.',
      keyStrategies: ['Sustainable Harvester', 'Ostrom Sanctioner', 'Antisocial Punisher'],
      status: 'Lab Module',
    },
    {
      number: 9,
      title: 'Zero-Determinant Strategies',
      subtitle: 'Press-Dyson Asymmetric Power',
      paradox: 'An extortioner unilaterally dictates the co-player\'s surplus ratio, but fails at scale.',
      keyStrategies: ['Extortioner (χ=3.0)', 'Equalizer (c=2.0)', 'Generous ZD'],
      status: 'Lab Module',
    },
    {
      number: 10,
      title: 'The Cognitive Revolution',
      subtitle: 'LLM Multi-Agent Societies & Cheap Talk',
      paradox: 'In accountable societies, strategic deception is an evolutionary dead end.',
      keyStrategies: ['Honest Diplomat', 'Machiavellian', 'Pragmatic Contractor', 'Skeptical Realist'],
      status: 'Lab Module',
    },
  ]

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="gradient-text-cyan">THE 10-EPISODE LABORATORY CURRICULUM</h2>
          <p className="text-secondary">
            Explore the complete scientific progression of The Dilemma Experiment across all ten milestones.
          </p>
        </div>
      </div>

      <div className="episodes-grid">
        {episodes.map((ep) => (
          <div key={ep.number} className="hud-panel episode-card">
            <div className="card-top-tag">
              <span className="badge badge-cyan">EPISODE {ep.number < 10 ? `0${ep.number}` : ep.number}</span>
              <span className={`badge ${ep.status === 'Ready' ? 'badge-green' : 'badge-gold'}`}>
                {ep.status}
              </span>
            </div>

            <h3 className="ep-card-title">{ep.title}</h3>
            <div className="ep-card-subtitle mono text-muted">{ep.subtitle}</div>

            <p className="ep-paradox">{ep.paradox}</p>

            <div className="trait-chips">
              {ep.keyStrategies.map((strat) => (
                <span key={strat} className="badge badge-purple">
                  {strat}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
