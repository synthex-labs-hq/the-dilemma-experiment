# Screencast Recording Guide: Episode 2

Follow these simple steps to record your screen assets in under 5 minutes using Ubuntu's built-in screen recorder.

---

### Step 1: Screencast 1 — The Tournament CLI (Terminal)
- **Target Duration:** **35 to 45 seconds**
- **Action Required:**
  1. Open a fresh Terminal window.
  2. Set terminal font size to **14pt or 16pt** (`Ctrl + Shift + +`) for crisp, high-contrast readability.
  3. Size the window to roughly **1200x800** (or snap to half-screen).
  4. Press **Print Screen** → Select **Video Camera (📹)** → Drag selection box around the terminal window.
  5. Click the **Red Record Button**.
  6. **Move your mouse pointer outside the recording frame** so the cursor doesn't distract the viewer.
  7. In the terminal, type and press Enter:
     ```bash
     uv run python experiments/episode_02/demo_tournament_cli.py
     ```
  8. **Hands off!** Do not type or scroll. The script auto-animates:
     - The centered cyan `THE DILEMMA` banner.
     - Multi-agent population initialization.
     - Live match ticker (10 duels with color-coded outcomes).
     - Final tournament podium with medals (🥇 GrimTrigger, 🥈 AlwaysDefect, 🥉 TitForTat) and the Axelrod Paradox summary.
  9. Wait ~3 seconds after the final summary prints, then click the **Red Stop Indicator** in the Ubuntu top bar.
- **Output File:** Automatically saved to `~/Videos/Screencasts/`.

---

### Step 2: Screencast 2 — Architecture & Grim Trigger Code (VS Code)
- **Target Duration:** **12 to 15 seconds**
- **Action Required:**
  1. In VS Code, open:
     - `src/the_dilemma_experiment/domain/tournament.py` (Focus on lines 40–80: `Tournament.execute()`)
     - Or split-screen with `src/the_dilemma_experiment/strategies/grim_trigger.py` (Focus on lines 10–25: `observe()` and `choose_action()`).
  2. Hide the file explorer sidebar (`Ctrl + B`) to maximize code view.
  3. Press **Print Screen** → Select **Video Camera (📹)** → Select the code editor area.
  4. Click **Record**.
  5. **Action:** Slowly and smoothly scroll down 15–20 lines, or pause for 4 seconds on `Tournament.execute()` and then switch tabs to `grim_trigger.py` to highlight `has_opponent_defected`.
  6. Stop recording after ~12–15 seconds.

---

### Step 3: Screencast 3 — 102 Passing Tests (Terminal)
- **Target Duration:** **5 to 8 seconds**
- **Action Required:**
  1. In your terminal, pre-type the command (do not press Enter yet):
     ```bash
     uv run pytest
     ```
  2. Press **Print Screen** → Select **Video Camera (📹)** → Drag over the terminal window.
  3. Click **Record**.
  4. Press **Enter** to run the command.
  5. Let the tests run and show the crisp green output:
     `==================== 102 passed in 0.16s ====================`
  6. Pause on the green success line for 2–3 seconds, then click **Stop**.

---

### Done! What to do next:
Once recorded, the three `.webm` files will be in `~/Videos/Screencasts/`.
We can use our automated FFmpeg renderer (`render_short.py`) to stitch them with voiceover and vertical framing for Shorts/Reels, or import them into your video editor (Clipchamp, DaVinci Resolve, or CapCut) for the long-form YouTube video.
