# Framework Installation Guide

This guide explains how to install `flop-airdrop-skill` across various AI agent frameworks and coding environments.

---

## 1. Antigravity & Google Stitch

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

**Trigger:**
Ask your Antigravity agent:
> "Help me with the $FLOP airdrop"

---

## 2. Claude Code

1. Add this skill to your Claude Code workspace:
   ```bash
   git clone https://github.com/YOUR_USERNAME/flop-airdrop-skill.git .claude/skills/flop-airdrop-skill
   ```
2. Claude Code will automatically discover `SKILL.md`.

**Trigger:**
> "Help me with the $FLOP airdrop"

---

## 3. Hermes & OpenClaw

1. Copy `SKILL.md` and the `scripts/` folder into your agent workspace.
2. In your agent configuration or system prompt, include `SKILL.md`:
   ```yaml
   skills:
     - path: ./flop-airdrop-skill/SKILL.md
       enabled: true
   ```

---

## 4. OpenCode

1. Copy this repository into `.opencode/skills/flop-airdrop-skill/`.
2. Ensure Python and `cryptography` are installed.
3. OpenCode will parse `SKILL.md` and execute the steps when prompted.

---

## 5. Cursor, Windsurf & VS Code AI Extensions

1. Copy `SKILL.md` into your workspace rules file (`.cursorrules` or `.windsurfrules`).
2. The AI assistant can invoke `scripts/agent_toolkit.py` directly through its terminal access.
