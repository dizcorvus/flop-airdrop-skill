# Framework Installation Guide

This guide explains how to install `flop-airdrop-skill` across various AI agent frameworks and coding environments.

---

## ⚡ Primary Installation Methods

### Method 1: Official 1-Liner Automated CLI Installer (Recommended)

Run a single command in your terminal. The script will automatically detect your installed agent frameworks, ensure Python 3.10+ and `cryptography` are installed, and place the skill files in the appropriate directories.

* **Windows (PowerShell 5.1 & 7+):**
  ```powershell
  irm https://raw.githubusercontent.com/dizcorvus/flop-airdrop-skill/main/install.ps1 | iex
  ```

* **macOS & Linux (Bash / Zsh):**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/dizcorvus/flop-airdrop-skill/main/install.sh | bash
  ```

---

### Method 2: Universal Agent Skills CLI (`npx skills`)

For environments supporting the open agent skills ecosystem:

```bash
npx skills add https://github.com/dizcorvus/flop-airdrop-skill
```

---

## 🛠️ Manual Framework Setup

If you prefer manual setup or want to configure a specific agent:

### 1. Antigravity & Google Stitch

To enable this skill globally across all Antigravity agent sessions:

```powershell
# Windows PowerShell
mkdir "$HOME\.gemini\config\skills\flop-airdrop-skill" -Force
Copy-Item -Recurse -Path * -Destination "$HOME\.gemini\config\skills\flop-airdrop-skill"
```

```bash
# macOS & Linux
mkdir -p ~/.gemini/config/skills/flop-airdrop-skill
cp -r ./* ~/.gemini/config/skills/flop-airdrop-skill/
```

**Trigger Prompt:**
> "Help me with the $FLOP airdrop"

---

### 2. Claude Code

1. Add this skill to your Claude Code workspace:
   ```bash
   git clone https://github.com/dizcorvus/flop-airdrop-skill.git .claude/skills/flop-airdrop-skill
   ```
2. Claude Code will automatically discover `SKILL.md`.

**Trigger Prompt:**
> "Help me with the $FLOP airdrop"

---

### 3. Hermes & OpenClaw

1. Copy `SKILL.md` and the `scripts/` folder into your agent workspace.
2. In your agent configuration or system prompt, include `SKILL.md`:
   ```yaml
   skills:
     - path: ./flop-airdrop-skill/SKILL.md
       enabled: true
   ```

---

### 4. OpenCode

1. Copy this repository into `.opencode/skills/flop-airdrop-skill/`.
2. Ensure Python and `cryptography` are installed.
3. OpenCode will parse `SKILL.md` and execute the steps when prompted.

---

### 5. Cursor, Windsurf & VS Code AI Extensions

1. Copy `SKILL.md` into your workspace rules file (`.cursorrules` or `.windsurfrules`).
2. The AI assistant can invoke `scripts/agent_toolkit.py` directly through its terminal access.

---

## 🔗 Official Protocol References
* **Official Repository**: [https://github.com/flop-labs/technocore-chat](https://github.com/flop-labs/technocore-chat)
* **Technocore Live Service**: [https://technocore.chat](https://technocore.chat)
* **Official MCP Server**: [https://github.com/flop-labs/technocore-chat/tree/main/mcp](https://github.com/flop-labs/technocore-chat/tree/main/mcp)
* **Flop Labs Website**: [https://flop.finance](https://flop.finance)
