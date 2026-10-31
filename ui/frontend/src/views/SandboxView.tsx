import React, { useState } from 'react'

export const SandboxView: React.FC = () => {
  const [strategyName, setStrategyName] = useState<string>('MyCustomAgent')
  const [openingMove, setOpeningMove] = useState<'COOPERATE' | 'DEFECT'>('COOPERATE')
  const [forgiveness, setForgiveness] = useState<number>(0.15)
  const [retaliationSeverity, setRetaliationSeverity] = useState<string>('one_to_one')

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="gradient-text-fire">STRATEGY SANDBOX: CREATE YOUR AGENT</h2>
          <p className="text-secondary">
            Design a custom game-theoretic strategy using behavioral trait sliders or Python logic.
          </p>
        </div>
      </div>

      <div className="sandbox-layout-grid">
        {/* Visual Builder Card */}
        <div className="hud-panel sandbox-builder-panel">
          <div className="panel-title-bar">
            <h3>VISUAL TRAIT BUILDER</h3>
            <span className="badge badge-cyan">NO-CODE MODE</span>
          </div>

          <div className="control-group">
            <label className="mono input-label">STRATEGY IDENTIFIER</label>
            <input
              type="text"
              value={strategyName}
              onChange={(e) => setStrategyName(e.target.value)}
              className="hud-input mono"
              placeholder="e.g., AdaptiveGuardian"
            />
          </div>

          <div className="control-group">
            <label className="mono input-label">FIRST ROUND POLICY</label>
            <div className="toggle-btn-group">
              <button
                className={`btn ${openingMove === 'COOPERATE' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setOpeningMove('COOPERATE')}
              >
                🤝 ALWAYS COOPERATE
              </button>
              <button
                className={`btn ${openingMove === 'DEFECT' ? 'btn-destructive' : 'btn-ghost'}`}
                onClick={() => setOpeningMove('DEFECT')}
              >
                🗡️ FIRST-STRIKE DEFECT
              </button>
            </div>
          </div>

          <div className="control-group">
            <label className="mono input-label">RETALIATION POLICY</label>
            <select
              className="hud-select"
              value={retaliationSeverity}
              onChange={(e) => setRetaliationSeverity(e.target.value)}
            >
              <option value="one_to_one">Tit-for-Tat (1 Round Retaliation)</option>
              <option value="patient">Tit-for-Two-Tats (Forgive 1st, Retaliate on 2nd)</option>
              <option value="grim">Grim Trigger (Permanent Defection Lockout)</option>
              <option value="pavlov">Win-Stay, Lose-Shift (Adaptive State Machine)</option>
            </select>
          </div>

          <div className="control-group">
            <div className="control-header">
              <label className="mono input-label">FORGIVENESS PROBABILITY: {(forgiveness * 100).toFixed(0)}%</label>
            </div>
            <input
              type="range"
              min="0"
              max="0.5"
              step="0.05"
              value={forgiveness}
              onChange={(e) => setForgiveness(Number(e.target.value))}
              className="hud-slider"
            />
          </div>

          <div className="preview-summary-box">
            <span className="mono text-muted">AGENT PROFILE:</span>
            <div className="mono font-bold text-cyan">{strategyName}</div>
            <p className="text-secondary text-sm">
              Opens with {openingMove}. When provoked, applies {retaliationSeverity} defense with a {(forgiveness * 100).toFixed(0)}% chance of unilateral pardon.
            </p>
          </div>
        </div>

        {/* Python Sandbox Preview */}
        <div className="hud-panel code-sandbox-panel">
          <div className="panel-title-bar">
            <h3>CODE SANDBOX (PREVIEW)</h3>
            <span className="badge badge-gold">PYTHON 3.12 CONTRACT</span>
          </div>

          <p className="text-secondary text-sm mb-3">
            In Phase UI-5, you will be able to execute custom Python strategy functions directly against the live tournament engine.
          </p>

          <pre className="code-editor-mock mono">
            {`from the_dilemma_experiment import Strategy, Action, DecisionContext

class ${strategyName}(Strategy):
    def choose_action(self, context: DecisionContext) -> Action:
        # Custom logic goes here
        if not context.opponent_history:
            return Action.${openingMove}
        
        last_move = context.opponent_history[-1]
        if last_move == Action.DEFECT:
            return Action.DEFECT
        return Action.COOPERATE
`}
          </pre>

          <div className="sandbox-footer">
            <button className="btn btn-ghost" disabled>
              🧪 TEST IN THE GAUNTLET (PHASE UI-5)
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
