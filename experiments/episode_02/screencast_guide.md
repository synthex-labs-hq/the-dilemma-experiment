# Screencast Recording Guide: Episode 2

Follow these simple steps to record your screen assets in under 5 minutes using Ubuntu's built-in screen recorder.

---

### Step 1: Terminal Setup for Screencast 1 (The Tournament CLI)
1. Open a fresh Terminal window.
2. Set terminal font size to **14pt or 16pt** (Ctrl + Shift + '+') for crisp, high-contrast readability.
3. Make the window roughly **1200x800** or snap it to half-screen.
4. Press the **Print Screen** key on your keyboard.
5. Select the **Video camera icon (📹)** at the bottom of the screenshot overlay.
6. Drag the selection box around the terminal window.
7. Click the **Red Record Button**.
8. In the terminal, execute:
   ```bash
   uv run python experiments/episode_02/demo_tournament_cli.py
   ```
9. Let it play through the banner, participant initialization, live match ticker, and final leaderboard reveal (~35–45 seconds).
10. Click the red stop indicator in the Ubuntu top bar.
11. The recorded webm file will be saved directly to `~/Videos/Screencasts/`.

---

### Step 2: VS Code Setup for Screencast 2 (Code Highlights)
1. In VS Code, open:
   - `src/the_dilemma_experiment/domain/tournament.py` (Focus lines 40–80)
   - `src/the_dilemma_experiment/strategies/grim_trigger.py` (Focus lines 10–25)
2. Press **Print Screen** → Select **Video (📹)**.
3. Select the code window area.
4. Record for **10–15 seconds**, slowly scrolling past `Tournament.execute()` and the `GrimTriggerStrategy` logic.
5. Stop recording.

---

### Step 3: Terminal Setup for Screencast 3 (102 Passing Tests)
1. In the terminal, prepare:
   ```bash
   uv run pytest
   ```
2. Press **Print Screen** → Select **Video (📹)**.
3. Start recording.
4. Run the command so the green `102 passed in 0.18s` is captured.
5. Stop recording (approx 5 seconds).

---

### Done!
You now have the 3 exact screencasts needed to assemble both the **Full Long-Form Video** and the **3 Shorts**!
