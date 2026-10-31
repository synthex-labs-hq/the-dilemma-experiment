import React from 'react'

export type TabId = 'arena' | 'tournaments' | 'episodes' | 'sandbox'

interface NavigationTabsProps {
  activeTab: TabId
  onSelectTab: (tab: TabId) => void
}

export const NavigationTabs: React.FC<NavigationTabsProps> = ({ activeTab, onSelectTab }) => {
  const tabs: { id: TabId; label: string; icon: string; badge?: string }[] = [
    { id: 'arena', label: 'The Arena (Pairwise Duel)', icon: '⚔️' },
    { id: 'tournaments', label: 'Tournament Hub', icon: '🏆', badge: 'Societies' },
    { id: 'episodes', label: 'Episode Laboratories', icon: '🧪', badge: '10 Ep' },
    { id: 'sandbox', label: 'Custom Agent Sandbox', icon: '🛠️', badge: 'New' },
  ]

  return (
    <nav className="nav-tabs-bar">
      <div className="nav-tabs-inner">
        {tabs.map((t) => {
          const isActive = activeTab === t.id
          return (
            <button
              key={t.id}
              className={`nav-tab-btn ${isActive ? 'nav-tab-btn-active' : ''}`}
              onClick={() => onSelectTab(t.id)}
            >
              <span className="tab-icon">{t.icon}</span>
              <span className="tab-label">{t.label}</span>
              {t.badge && (
                <span className={`badge ${isActive ? 'badge-cyan' : 'badge-gold'}`}>
                  {t.badge}
                </span>
              )}
            </button>
          )
        })}
      </div>
    </nav>
  )
}
