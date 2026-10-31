#!/usr/bin/env bash
# ==============================================================================
# The Dilemma Experiment - Unified Interactive Simulation Platform Launcher
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

CYAN='\033[0;36m'
GOLD='\033[0;33m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}======================================================================${NC}"
echo -e "${GOLD}   THE DILEMMA ARENA - EVOLUTIONARY GAME THEORY SIMULATION SUITE      ${NC}"
echo -e "${CYAN}======================================================================${NC}"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}[ERROR] 'uv' is not installed or not in PATH.${NC}"
    echo "Install uv via: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Detect package manager for UI
if command -v pnpm &> /dev/null; then
    PKG_MGR="pnpm"
elif command -v bun &> /dev/null; then
    PKG_MGR="bun"
elif command -v npm &> /dev/null; then
    PKG_MGR="npm"
else
    echo -e "${RED}[ERROR] Neither pnpm, bun, nor npm was found in PATH.${NC}"
    exit 1
fi

MODE="dev"
if [[ "$1" == "--prod" || "$1" == "-p" ]]; then
    MODE="prod"
fi

if [[ "$MODE" == "prod" ]]; then
    echo -e "${GOLD}[MODE] Building and Launching Single-Port Standalone Platform...${NC}"
    echo -e "${PURPLE}[1/2] Building React frontend via $PKG_MGR...${NC}"
    $PKG_MGR --dir ui/frontend build

    echo -e "${GREEN}[2/2] Starting Standalone Engine on http://localhost:8000...${NC}"
    echo -e "${CYAN}>> Arena UI & API Core Live at: http://localhost:8000${NC}"
    echo -e "${CYAN}>> OpenAPI Documentation:       http://localhost:8000/docs${NC}"
    echo -e "${GOLD}Press Ctrl+C to terminate.${NC}\n"
    exec uv run uvicorn the_dilemma_experiment.api.app:app --host 0.0.0.0 --port 8000
fi

# Development Mode: Run FastAPI and Vite concurrently
echo -e "${GOLD}[MODE] Development Mode (FastAPI + Vite HMR)${NC}"

# Start FastAPI backend in background
echo -e "${PURPLE}[1/2] Booting FastAPI Simulation Core on http://127.0.0.1:8000...${NC}"
uv run uvicorn the_dilemma_experiment.api.app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Ensure backend terminates when script exits
cleanup() {
    echo -e "\n${RED}Shutting down simulation services...${NC}"
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Give backend a moment to bind port
sleep 1.2

echo -e "${GREEN}[2/2] Starting Cybernetic HUD Frontend via $PKG_MGR on http://localhost:5173...${NC}"
echo -e "${CYAN}----------------------------------------------------------------------${NC}"
echo -e "${GREEN}✓ Web Arena Interface:  http://localhost:5173${NC}"
echo -e "${GREEN}✓ FastAPI Backend Core: http://localhost:8000${NC}"
echo -e "${GREEN}✓ OpenAPI Documentation: http://localhost:8000/docs${NC}"
echo -e "${CYAN}----------------------------------------------------------------------${NC}"
echo -e "${GOLD}Press Ctrl+C to terminate both servers.${NC}\n"

# Run Vite dev server in foreground
$PKG_MGR --dir ui/frontend dev --host
