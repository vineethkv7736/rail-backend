# Google Cloud Run Deployment Guide

This guide documents the successful deployment method used for the `momhood` backend. You can use this exact same approach for any other **Python** or **Node.js** project.

## 1. Prerequisites
Before deploying a new project, ensure you have:

1.  **Google Cloud CLI** installed and authenticated (`gcloud auth login`).
2.  **Billing Enabled** on your Google Cloud Project.
3.  **Docker** is *optional* (Cloud Run can build remotely), but a `Dockerfile` in your project folder is highly recommended for control.

## 2. Project Setup
Ensure your new project folder has these essential files:

### A. Dockerfile
Define how your app runs.
*Example (Python):*
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Cloud Run injects $PORT (default 8080)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
```

### B. .dockerignore & .gcloudignore
Prevent uploading garbage files (like `venv`, `.git`, or local secrets).
*Content:*
```text
.git
.gitignore
venv/
__pycache__/
*.pyc
.env
```

### C. .env (Local Secrets)
Your local configuration file. **Do not commit this to Git.**
```properties
DATABASE_URL=...
API_KEY=...
```

## 3. The Deployment Script
Save this PowerShell script as `deploy.ps1` in your new project's root folder. It automatically reads your local `.env` file and deploys the app.

```powershell
# deploy.ps1
# Usage: .\deploy.ps1
$ErrorActionPreference = "Stop"

# --- CONFIGURATION ---
$ProjectId = "your-project-id"   # <--- CHANGE THIS
$ServiceName = "your-service-name" # <--- CHANGE THIS (e.g., my-backend)
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
    "--allow-unauthenticated",  # Remove this if you want private access only
    "--region", $Region
)

if (-not [string]::IsNullOrEmpty($envString)) {
    $deployArgs += "--set-env-vars"
    $deployArgs += $envString
}

# Execute
& gcloud $deployArgs
```

## 4. How to Deploy
1.  Open your terminal in the new project folder.
2.  Run the script:
    ```powershell
    .\deploy.ps1
    ```
3.  **First Run:** You might be asked to create a repository or enable APIs. Type `y` to proceed.

## Summary of "What Worked"
The method that succeeded was **Source-based Deployment**.
- **We did NOT** need to build a Docker image locally. We sent the *source code* to Google (Cloud Build), which built the container for us using the `Dockerfile`.
- **We DID** need to explicitly pass environment variables (`--set-env-vars`) because Cloud Run does not read `.env` files automatically.
