#!/bin/bash

# run.sh - Setup and launch RepoSense backend and VS Code extension
#
# Designed to run on a judge's machine with minimal assumptions.
# Requirements (script will check and report what's missing):
#   - bash  (Mac/Linux: built-in; Windows: install Git for Windows / Git Bash)
#   - Python 3.11, 3.12, or 3.13  (ibm-watsonx-ai constraint)
#   - Node.js + npm
#   - VS Code with the `code` CLI in PATH (optional; will skip auto-launch if missing)

set -e

echo "=========================================="
echo "RepoSense Setup and Launch Script"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ---------------------------------------------------------------------------
# Prerequisite checks — bail fast with a clear message if something's missing
# ---------------------------------------------------------------------------
echo -e "${BLUE}Checking prerequisites...${NC}"

# Find a Python in the range 3.11-3.13 (ibm-watsonx-ai requires >=3.11,<3.14).
# Sets PYTHON_CMD to the command we'll use for `-m venv`.
PYTHON_CMD=""
PYTHON_VERSION=""

# On Windows, prefer the py launcher with an explicit minor version. The
# bare `py -3` picks the newest installed Python, which may be too new.
for v in 3.12 3.13 3.11; do
    if command -v py >/dev/null 2>&1 && py -$v --version >/dev/null 2>&1; then
        PYTHON_CMD="py -$v"
        PYTHON_VERSION=$(py -$v --version 2>&1)
        break
    fi
done

# Fall back to python3 / python and verify their version is in range.
if [ -z "$PYTHON_CMD" ]; then
    for cmd in python3 python; do
        if command -v $cmd >/dev/null 2>&1; then
            ver=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
            major=${ver%%.*}
            minor=${ver##*.}
            if [ "$major" = "3" ] && [ "$minor" -ge 11 ] 2>/dev/null && [ "$minor" -le 13 ] 2>/dev/null; then
                PYTHON_CMD="$cmd"
                PYTHON_VERSION=$($cmd --version 2>&1)
                break
            fi
        fi
    done
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}ERROR: Python 3.11, 3.12, or 3.13 not found.${NC}" >&2
    echo "  ibm-watsonx-ai==1.5.11 requires Python >=3.11,<3.14." >&2
    echo "  Install from https://www.python.org/downloads/" >&2
    echo "  (On Windows, the official installer registers the 'py' launcher used here.)" >&2
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Python: $PYTHON_VERSION  ($PYTHON_CMD)"

# Node.js + npm
if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Node.js not found.${NC}" >&2
    echo "  Install the LTS release from https://nodejs.org/" >&2
    exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}ERROR: npm not found (should ship with Node.js).${NC}" >&2
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Node.js: $(node --version), npm: $(npm --version)"

# `code` CLI — warn but don't fail; if missing we just skip auto-launch.
CODE_AVAILABLE=1
if ! command -v code >/dev/null 2>&1; then
    CODE_AVAILABLE=0
    echo -e "  ${YELLOW}⚠${NC} 'code' command not in PATH — VS Code won't be auto-launched."
    echo "    On macOS: open VS Code → Cmd+Shift+P → 'Shell Command: Install 'code' command in PATH'"
    echo "    On Windows: re-run the VS Code installer and check 'Add to PATH'"
else
    echo -e "  ${GREEN}✓${NC} code CLI: $(command -v code)"
fi

# Port 8000 — warn if something's already listening.
PORT_IN_USE=0
if command -v lsof >/dev/null 2>&1; then
    if lsof -i :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then PORT_IN_USE=1; fi
elif command -v netstat >/dev/null 2>&1; then
    if netstat -an 2>/dev/null | grep -E "[\.:]8000[[:space:]].*LISTEN" >/dev/null 2>&1; then PORT_IN_USE=1; fi
fi
if [ "$PORT_IN_USE" = "1" ]; then
    echo -e "  ${YELLOW}⚠${NC} Port 8000 is already in use — backend launch will fail."
    echo "    Stop the existing service first."
fi

# .env with placeholders — would suppress the setup wizard.
if [ -f "backend/.env" ] && grep -qE "your-(orchestrate|watsonx)-(api-key|project)-here|your_watsonx_(api_key|project_id)_here" backend/.env 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} backend/.env contains placeholder values from .env.example."
    echo "    These non-empty placeholders make /config/status report configured=true,"
    echo "    which suppresses the setup wizard and then analysis fails on bogus creds."
    echo "    Fix: delete backend/.env (the wizard will run on first launch) or fill in real values."
fi

echo ""

# ---------------------------------------------------------------------------
# Step 1: Create virtual environment if it doesn't exist
# ---------------------------------------------------------------------------
echo -e "${BLUE}[1/4] Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# ---------------------------------------------------------------------------
# Step 2: Activate virtual environment
# ---------------------------------------------------------------------------
echo -e "${BLUE}[2/4] Activating virtual environment...${NC}"
# Layout depends on which python created the venv, not the OS:
# python.org installer on Windows → venv/Scripts/activate
# Unix-style python (msys2, Mac, Linux)      → venv/bin/activate
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo -e "${RED}ERROR: venv activation script not found.${NC}" >&2
    echo "  Try deleting the venv/ directory and re-running." >&2
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# ---------------------------------------------------------------------------
# Step 3: Install Python dependencies
# ---------------------------------------------------------------------------
echo -e "${BLUE}[3/4] Installing Python dependencies (this may take a minute)...${NC}"
# Use 'python -m pip' for the self-upgrade — on Windows, pip can't replace
# its own running .exe, so a direct 'pip install --upgrade pip' errors out.
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# ---------------------------------------------------------------------------
# Step 4: Install Node.js dependencies
# ---------------------------------------------------------------------------
echo -e "${BLUE}[4/4] Installing Node.js dependencies...${NC}"
cd vscode-extension
npm install
cd ..
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Note: watsonx credentials are configured via the setup wizard${NC}"
echo -e "${YELLOW}      that appears in the RepoSense sidebar on first launch.${NC}"

echo ""
echo "=========================================="
echo "Starting RepoSense Services"
echo "=========================================="

# ---------------------------------------------------------------------------
# Start uvicorn backend server in background
# ---------------------------------------------------------------------------
echo -e "${BLUE}Starting backend server on http://localhost:8000...${NC}"
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to actually respond — not just "process exists".
# uvicorn can crash post-fork (e.g. port collision) and the bare ps check
# would still report success.
BACKEND_READY=0
for i in 1 2 3 4 5 6 7 8 9 10; do
    sleep 1
    if command -v curl >/dev/null 2>&1; then
        if curl -s -m 2 http://localhost:8000/ >/dev/null 2>&1; then
            BACKEND_READY=1
            break
        fi
    else
        # No curl — fall back to ps check only.
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            BACKEND_READY=1
            break
        fi
    fi
done

if [ "$BACKEND_READY" = "1" ]; then
    echo -e "${GREEN}✓ Backend server started (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}⚠ Backend did not respond after 10s — check the uvicorn output above.${NC}"
    echo "  Common causes: port 8000 already in use, missing Python deps, syntax error."
fi

# ---------------------------------------------------------------------------
# Launch VS Code with the extension
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}Compiling extension...${NC}"
cd vscode-extension
npm run compile
if [ "$CODE_AVAILABLE" = "1" ]; then
    echo -e "${BLUE}Launching VS Code extension development host...${NC}"
    code --extensionDevelopmentPath="$(pwd)" ..
else
    echo -e "${YELLOW}Skipping VS Code auto-launch ('code' not in PATH).${NC}"
    echo -e "${YELLOW}To run manually: open the vscode-extension folder in VS Code and press F5.${NC}"
fi
cd ..

echo ""
echo "=========================================="
echo "RepoSense is now running!"
echo "=========================================="
echo -e "Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "API Docs:    ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "To stop the backend server, run:"
echo -e "${YELLOW}kill $BACKEND_PID${NC}"
echo ""
echo "Press Ctrl+C to exit this script (backend will continue running)"
echo "=========================================="

# Block on the background uvicorn so Ctrl+C is intuitive
wait

# Made with Bob
