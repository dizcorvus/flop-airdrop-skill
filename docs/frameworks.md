# Framework Installation Guide

This guide explains how to install and activate `technocore-agent-skill` across various AI agent frameworks and coding assistants.

---

## 1. Antigravity & Google Stitch

To make this skill globally accessible across all Antigravity agent sessions:

```powershell
# Windows
mkdir "$HOME\.gemini\config\skills\technocore-agent-skill"
Copy-Item -Recurse -Path * -Destination "$HOME\.gemini\config\skills\technocore-agent-skill"
```

```bash
# macOS & Linux
mkdir -p ~/.gemini/config/skills/technocore-agent-skill
cp -r ./* ~/.gemini/config/skills/technocore-agent-skill/
```

Once copied, trigger the agent by asking:
> "Help me set up my Technocore DID identity and position for the $FLOP airdrop."

---

## 2. Claude Code

For Claude Code CLI:

1. Clone or copy this repository into your project root:
   ```bash
   git clone https://github.com/YOUR_USERNAME/technocore-agent-skill.git .claude/skills/technocore-agent-skill
   ```
2. Claude Code will automatically detect `SKILL.md` in its skill discovery path.

---

## 3. Hermes & OpenClaw

For Hermes and OpenClaw agent environments:

1. Copy `SKILL.md` and the `scripts/` directory into your agent workspace.
2. In your agent configuration or system prompt, point the agent context to `SKILL.md`:
   ```yaml
   skills:
     - path: ./technocore-agent-skill/SKILL.md
       enabled: true
   ```

---

## 4. OpenCode

For OpenCode environments:

1. Place the folder under `.opencode/skills/technocore-agent-skill/`.
2. Ensure Python with `cryptography` is available in your shell environment.
3. OpenCode will parse `SKILL.md` frontmatter and load the commands dynamically.

---

## 5. Cursor, Windsurf & VS Code AI Extensions

For IDE-based assistants (Cursor rules, Windsurf flows, Cline, Roo-Code):

1. Copy `SKILL.md` to `.cursorrules` or `.windsurfrules`, or reference it as an active rule file.
2. The assistant can execute commands in `scripts/agent_toolkit.py` directly through its integrated terminal.
