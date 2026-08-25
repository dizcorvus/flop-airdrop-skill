#!/usr/bin/env bash
# FLOP Airdrop Skill - Official Linux/macOS 1-Liner Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/dizcorvus/flop-airdrop-skill/main/install.sh | bash

set -e

echo -e "\033[1;36m======================================================\033[0m"
echo -e "\033[1;36m      FLOP Airdrop Skill - Agent Setup Installer      \033[0m"
echo -e "\033[1;36m======================================================\033[0m"
echo ""

# 1. Check Python installation
echo -e "\033[1;33m[1/4] Checking Python environment...\033[0m"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "\033[1;31m[-] Python 3 is not found. Please install Python 3.10+.\033[0m"
    exit 1
fi

PY_VER=$($PYTHON_CMD --version)
echo -e "\033[1;32m[+] Found: $PY_VER\033[0m"

# 2. Check cryptography
echo -e "\033[1;33m[2/4] Verifying required cryptography module...\033[0m"
if $PYTHON_CMD -c "import cryptography" &>/dev/null; then
    echo -e "\033[1;32m[+] Module 'cryptography' is already installed.\033[0m"
else
    echo -e "\033[1;33m[*] Installing 'cryptography' via pip...\033[0m"
    $PYTHON_CMD -m pip install --quiet --upgrade cryptography
    echo -e "\033[1;32m[+] 'cryptography' installed successfully.\033[0m"
fi

# 3. Download & Install Skill
echo -e "\033[1;33m[3/4] Installing skill to AI agent environments...\033[0m"
REPO_URL="https://github.com/dizcorvus/flop-airdrop-skill.git"
TEMP_DIR=$(mktemp -d)

if command -v git &>/dev/null; then
    git clone --depth 1 "$REPO_URL" "$TEMP_DIR" &>/dev/null
else
    echo -e "\033[1;33m[*] Downloading skill archive via curl...\033[0m"
    curl -fsSL "https://github.com/dizcorvus/flop-airdrop-skill/archive/refs/heads/main.tar.gz" | tar -xz -C "$TEMP_DIR" --strip-components=1
fi

# Global Gemini / Antigravity skill directory
GLOBAL_GEMINI="$HOME/.gemini/config/skills/flop-airdrop-skill"
mkdir -p "$GLOBAL_GEMINI"
cp -r "$TEMP_DIR/"* "$GLOBAL_GEMINI/"
echo -e "\033[1;32m[+] Installed to Global Antigravity Agent: $GLOBAL_GEMINI\033[0m"

# Local workspace directories
LOCAL_CLAUDE="./.claude/skills/flop-airdrop-skill"
LOCAL_AGENTS="./.agents/skills/flop-airdrop-skill"
mkdir -p "$LOCAL_CLAUDE" "$LOCAL_AGENTS"
cp -r "$TEMP_DIR/"* "$LOCAL_CLAUDE/"
cp -r "$TEMP_DIR/"* "$LOCAL_AGENTS/"
echo -e "\033[1;32m[+] Installed to Local Claude Code Agent: $LOCAL_CLAUDE\033[0m"
echo -e "\033[1;32m[+] Installed to Local Workspace Agents: $LOCAL_AGENTS\033[0m"

# Clean up
rm -rf "$TEMP_DIR"

# 4. Completion
echo ""
echo -e "\033[1;36m[4/4] Installation Complete!\033[0m"
echo -e "\033[1;36m======================================================\033[0m"
echo -e "Now, simply open your AI agent chat and type:"
echo -e "\033[1;33m  \"Help me with the \$FLOP airdrop\"\033[0m or \033[1;33m\"Set up my Technocore DID\"\033[0m"
echo ""
echo -e "Your agent will guide you autonomously through the setup."
echo -e "\033[1;36m======================================================\033[0m"
