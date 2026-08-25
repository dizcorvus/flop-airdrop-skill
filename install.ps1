# FLOP Airdrop Skill - Official Windows 1-Liner Installer
# Usage: irm https://raw.githubusercontent.com/dizcorvus/flop-airdrop-skill/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "      FLOP Airdrop Skill - Agent Setup Installer      " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python installation
Write-Host "[1/4] Checking Python environment..." -ForegroundColor Yellow
$PythonCmd = $null

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCmd = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
}

if (-not $PythonCmd) {
    Write-Host "[-] Python is not detected in PATH. Please install Python 3.10+ from python.org" -ForegroundColor Red
    exit 1
}

$PythonVersion = & $PythonCmd --version 2>&1
Write-Host "[+] Found: $PythonVersion" -ForegroundColor Green

# 2. Install cryptography dependency
Write-Host "[2/4] Verifying required cryptography module..." -ForegroundColor Yellow
try {
    & $PythonCmd -c "import cryptography" 2>$null
    Write-Host "[+] Module 'cryptography' is already installed." -ForegroundColor Green
} catch {
    Write-Host "[*] Installing 'cryptography' via pip..." -ForegroundColor Yellow
    & $PythonCmd -m pip install --quiet --upgrade cryptography
    Write-Host "[+] 'cryptography' installed successfully." -ForegroundColor Green
}

# 3. Setup Skill Target Locations
Write-Host "[3/4] Installing skill to AI agent environments..." -ForegroundColor Yellow

$RepoUrl = "https://github.com/dizcorvus/flop-airdrop-skill.git"
$TempDir = Join-Path $env:TEMP "flop-airdrop-skill-temp"

if (Test-Path $TempDir) {
    Remove-Item -Recurse -Force $TempDir
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    git clone --depth 1 $RepoUrl $TempDir 2>$null
} else {
    Write-Host "[*] Downloading skill archive..." -ForegroundColor Yellow
    $ZipPath = Join-Path $env:TEMP "flop-airdrop-skill.zip"
    Invoke-WebRequest -Uri "https://github.com/dizcorvus/flop-airdrop-skill/archive/refs/heads/main.zip" -OutFile $ZipPath
    Expand-Archive -Path $ZipPath -DestinationPath (Join-Path $env:TEMP "flop_zip_extracted") -Force
    Move-Item (Join-Path $env:TEMP "flop_zip_extracted\flop-airdrop-skill-main") $TempDir
}

# Define target paths
$Targets = @(
    (Join-Path $HOME ".gemini\config\skills\flop-airdrop-skill"),
    (Join-Path (Get-Location) ".claude\skills\flop-airdrop-skill"),
    (Join-Path (Get-Location) ".agents\skills\flop-airdrop-skill"),
    (Join-Path (Get-Location) ".opencode\skills\flop-airdrop-skill")
)

# Always install to global Antigravity / Gemini config
$GlobalGemini = Join-Path $HOME ".gemini\config\skills\flop-airdrop-skill"
if (-not (Test-Path $GlobalGemini)) {
    New-Item -ItemType Directory -Path $GlobalGemini -Force | Out-Null
}
Copy-Item -Path "$TempDir\*" -Destination $GlobalGemini -Recurse -Force
Write-Host "[+] Installed to Global Antigravity Agent: $GlobalGemini" -ForegroundColor Green

# If inside a workspace, install locally as well
$LocalClaude = Join-Path (Get-Location) ".claude\skills\flop-airdrop-skill"
$LocalAgents = Join-Path (Get-Location) ".agents\skills\flop-airdrop-skill"

New-Item -ItemType Directory -Path $LocalClaude -Force | Out-Null
Copy-Item -Path "$TempDir\*" -Destination $LocalClaude -Recurse -Force
Write-Host "[+] Installed to Local Claude Code Agent: $LocalClaude" -ForegroundColor Green

New-Item -ItemType Directory -Path $LocalAgents -Force | Out-Null
Copy-Item -Path "$TempDir\*" -Destination $LocalAgents -Recurse -Force
Write-Host "[+] Installed to Local Workspace Agents: $LocalAgents" -ForegroundColor Green

# Cleanup
Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue

# 4. Completion
Write-Host ""
Write-Host "[4/4] Installation Complete!" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Now, simply open your AI agent chat and type:" -ForegroundColor White
Write-Host ""
Write-Host '  "Help me with the $FLOP airdrop"' -ForegroundColor Yellow -NoNewline
Write-Host " or " -NoNewline
Write-Host '"Set up my Technocore DID"' -ForegroundColor Yellow
Write-Host ""
Write-Host "Your agent will guide you autonomously through the setup." -ForegroundColor White
Write-Host "======================================================" -ForegroundColor Cyan
