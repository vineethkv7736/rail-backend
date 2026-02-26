# deploy.ps1
# Usage: .\deploy.ps1
$ErrorActionPreference = "Stop"

# --- CONFIGURATION ---
$ProjectId = "railpro-484903"   
$ServiceName = "railpro-backend" 
$Region = "us-central1"
# ---------------------

Write-Host "🚀 Starting deployment for $ServiceName..." -ForegroundColor Cyan
gcloud config set project $ProjectId

# 1. Read .env file to inject variables
$envFile = "$PSScriptRoot\.env"
$envString = ""

if (Test-Path $envFile) {
    Write-Host "🔍 Reading .env configuration..." -ForegroundColor Yellow
    $lines = Get-Content $envFile
    $vars = @()
    foreach ($line in $lines) {
        $line = $line.Trim()
        # Parse non-empty, non-comment lines
        if ($line.Length -gt 0 -and -not $line.StartsWith("#")) {
            $parts = $line.Split("=", 2)
            if ($parts.Count -eq 2) {
                $k = $parts[0].Trim()
                $v = $parts[1].Trim()
                # Remove quotes around values
                $v = $v -replace '^"|"$', "" -replace "^'|'$", ""
                if (-not [string]::IsNullOrWhiteSpace($v)) {
                    # Special handling for GOOGLE_APPLICATION_CREDENTIALS
                    if ($k -eq "GOOGLE_APPLICATION_CREDENTIALS") {
                        # Extract just the filename and prepend /app/
                        $fileName = Split-Path $v -Leaf
                        $v = "/app/$fileName"
                        Write-Host "🔧 Rewrote $k to $v for container" -ForegroundColor Gray
                    }
                    $vars += "$k=$v"
                }
            }
        }
    }
    if ($vars.Count -gt 0) {
        $envString = $vars -join ","
        Write-Host "✅ Sourced $($vars.Count) environment variables." -ForegroundColor Green
    }
} else {
    Write-Warning "⚠️ No .env file found. Deploying without environment variables."
}

# 2. Deploy Command
Write-Host "📦 Deploying to Cloud Run..." -ForegroundColor Cyan

$deployArgs = @(
    "run", "deploy", $ServiceName,
    "--source", ".",
    "--platform", "managed",
    "--allow-unauthenticated",
    "--region", $Region
)

if (-not [string]::IsNullOrEmpty($envString)) {
    $deployArgs += "--set-env-vars"
    $deployArgs += $envString
}

# Execute
& gcloud $deployArgs
