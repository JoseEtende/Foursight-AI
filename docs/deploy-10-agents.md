# FourSight Agents – End‑to‑End Cloud Run Deployment Guide

This guide documents a complete, repeatable deployment for the 10 framework agents to Google Cloud Run, including creating (or recreating) the Artifact Registry, building and pushing images, deploying services, and capturing service URLs into your `.env`.

Notes:
- Commands are shown for PowerShell on Windows.
- Replace placeholders like `<YOUR_PROJECT_ID>` with your actual values.
- All agents expose port `8080` and are started via `adk api_server` in their Dockerfiles.

---

## 1) Prerequisites and Setup

- Install and sign in to the Google Cloud CLI:
  ```powershell
  gcloud auth login
  ```
- Set your active project and verify:
  ```powershell
  $PROJECT_ID = "<YOUR_PROJECT_ID>"  # e.g., "foursighthack"
  gcloud config set project $PROJECT_ID
  gcloud config get-value project  # should print $PROJECT_ID
  ```
- Pick a region (keep it consistent across Artifact Registry and Cloud Run). The existing services use `us-central1`:
  ```powershell
  $REGION = "us-central1"
  ```
- Enable required services (only needed once per project):
  ```powershell
  gcloud services enable artifactregistry.googleapis.com
  gcloud services enable run.googleapis.com
  ```
- Make sure Docker is installed and running locally.

---

## 2) Create (or Recreate) the Artifact Registry

Repository naming used below: `foursight-agents` in `us-central1`.

### 2.1 Inspect existing repositories
```powershell
# List repositories in the chosen region
gcloud artifacts repositories list --location=$REGION
```

### 2.2 Delete an existing repository (if you want to start clean)
```powershell
# DANGER: This deletes the repository and all its images.
# If you want to skip the confirmation prompt, add --quiet.

gcloud artifacts repositories delete foursight-agents --location=$REGION
```

If deletion complains about existing images, you can remove them first:
```powershell
# List images in the repo
gcloud artifacts docker images list "$REGION-docker.pkg.dev/$PROJECT_ID/foursight-agents"

# Delete a specific image tag (repeat for each tag you want gone)
# Example: delete pros-cons-agent:latest
#gcloud artifacts docker images delete "$REGION-docker.pkg.dev/$PROJECT_ID/foursight-agents/pros-cons-agent:latest" --quiet
```

### 2.3 Create the repository
```powershell
# Create a Docker-format repository to store agent images

gcloud artifacts repositories create foursight-agents `
  --location=$REGION `
  --repository-format=docker `
  --description="FourSight agents"
```

### 2.4 Configure Docker to authenticate to Artifact Registry
```powershell
# Configure Docker for your region’s Artifact Registry domain

gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

### 2.5 Set a convenience variable for the registry path
```powershell
# Base path: REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY
$env:REPO = "$REGION-docker.pkg.dev/$PROJECT_ID/foursight-agents"
# Verify
$env:REPO
```

---

## 3) Build and Push Images for All 10 Agents

All agent directories live under `services/` and include a Dockerfile. Each agent’s image will be tagged as:
```
$env:REPO/<image-name>:<tag>
```
Recommended `<image-name>` values (use snake-case derived from folders):
- pros-cons-agent
- swot-agent
- cost-benefit-agent
- five-ws-and-h-agent
- five-whys-agent
- ten-ten-ten-agent
- kepner-tregoe-agent
- rational-decision-making-agent
- weighted-matrix-agent
- decide-model-agent

You can build and push individually, e.g.:
```powershell
# Example: pros_cons_agent
# IMPORTANT: Build from the repo root so the Docker context includes the top-level `scripts/` folder.
# The Dockerfile contains `COPY scripts/ /scripts/`, which requires `scripts/` to be present in the build context.

# From the project root:
docker build -f services\pros_cons_agent\Dockerfile -t "$env:REPO/pros-cons-agent:latest" .

# If you encounter PyPI read timeouts during the install step, the Dockerfiles
# set a higher pip timeout and disable the version check to reduce flakiness.
# If issues persist, retry the build, ensure a stable network, or consider
# temporarily using `--network host` on Linux.

# Then push the image
docker push "$env:REPO/pros-cons-agent:latest"
```

Or use a loop to process all agents in one go:
```powershell
# From the repo root
cd "$PSScriptRoot"  # optional; ensure you’re in the project root

$agents = @(
  @{ dir = "pros_cons_agent"; image = "pros-cons-agent" },
  @{ dir = "swot_agent"; image = "swot-agent" },
  @{ dir = "cost_benefit_agent"; image = "cost-benefit-agent" },
  @{ dir = "five_ws_and_h_agent"; image = "five-ws-and-h-agent" },
  @{ dir = "five_whys_agent"; image = "five-whys-agent" },
  @{ dir = "ten_ten_ten_agent"; image = "ten-ten-ten-agent" },
  @{ dir = "kepner_tregoe_agent"; image = "kepner-tregoe-agent" },
  @{ dir = "rational_decision_making_agent"; image = "rational-decision-making-agent" },
  @{ dir = "weighted_matrix_agent"; image = "weighted-matrix-agent" },
  @{ dir = "decide_model_agent"; image = "decide-model-agent" }
)

foreach ($a in $agents) {
  $path = "services/" + $a.dir
  Write-Host "Building and pushing $($a.image) using Dockerfile at $path/Dockerfile"
  # Build from the repo root (context is '.') so the top-level `scripts/` folder is available.
  docker build -f "$path/Dockerfile" -t "$env:REPO/$($a.image):latest" .
  if ($LASTEXITCODE -ne 0) { throw "Docker build failed for $($a.image)" }
  docker push "$env:REPO/$($a.image):latest"
  if ($LASTEXITCODE -ne 0) { throw "Docker push failed for $($a.image)" }
}
```

---

## 4) Deploy Services to Cloud Run

Each service runs on port `8080`. Required env vars for agents:
- `GOOGLE_API_KEY` (mapped from `GEMINI_API_KEY` in code)
- `LOG_LEVEL` (e.g., `INFO`, `DEBUG`)

Deploy one agent (example: pros-cons-agent):
```powershell
$SERVICE = "pros-cons-agent"
$IMAGE   = "$env:REPO/pros-cons-agent:latest"
$GEMINI  = "<YOUR_GEMINI_API_KEY>"  # required for model access

# Deploy to Cloud Run (fully managed)
gcloud run deploy $SERVICE `
  --image $IMAGE `
  --region $REGION `
  --allow-unauthenticated `
  --port 8080 `
  --set-env-vars "GOOGLE_API_KEY=$GEMINI,LOG_LEVEL=INFO"
```

Batch deploy all agents after pushing images:
```powershell
$gcpEnv = "GOOGLE_API_KEY=<YOUR_GEMINI_API_KEY>,LOG_LEVEL=INFO"

$services = @(
  "pros-cons-agent",
  "swot-agent",
  "cost-benefit-agent",
  "five-ws-and-h-agent",
  "five-whys-agent",
  "ten-ten-ten-agent",
  "kepner-tregoe-agent",
  "rational-decision-making-agent",
  "weighted-matrix-agent",
  "decide-model-agent"
)

foreach ($s in $services) {
  Write-Host "Deploying $s"
  gcloud run deploy $s `
    --image "$env:REPO/$s:latest" `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --set-env-vars $gcpEnv

  if ($LASTEXITCODE -ne 0) { throw "Deploy failed for $s" }
}
```

---

## 5) Capture Cloud Run URLs and Update `.env`

Query each service URL:
```powershell
function Get-ServiceUrl($name) {
  gcloud run services describe $name `
    --region $REGION `
    --format "value(status.url)"
}

$urls = @{
  "PROS_CONS_AGENT_URL"                 = Get-ServiceUrl "pros-cons-agent"
  "SWOT_AGENT_URL"                       = Get-ServiceUrl "swot-agent"
  "COST_BENEFIT_AGENT_URL"               = Get-ServiceUrl "cost-benefit-agent"
  "FIVE_WS_AND_H_AGENT_URL"              = Get-ServiceUrl "five-ws-and-h-agent"
  "FIVE_WHYS_AGENT_URL"                  = Get-ServiceUrl "five-whys-agent"
  "TEN_TEN_TEN_AGENT_URL"                = Get-ServiceUrl "ten-ten-ten-agent"
  "KEPNER_TREGOE_AGENT_URL"              = Get-ServiceUrl "kepner-tregoe-agent"
  "RATIONAL_DECISION_MAKING_AGENT_URL"   = Get-ServiceUrl "rational-decision-making-agent"
  "WEIGHTED_MATRIX_AGENT_URL"            = Get-ServiceUrl "weighted-matrix-agent"
  "DECIDE_MODEL_AGENT_URL"               = Get-ServiceUrl "decide-model-agent"
}

# Append to .env (keeps existing values intact)
$envPath = ".env"
foreach ($k in $urls.Keys) {
  $line = "$k=\"$($urls[$k])\""
  Add-Content -Path $envPath -Value $line
  Write-Host "Wrote $line"
}
```

Your `.env` should end up with entries like:
```env
PROS_CONS_AGENT_URL="https://pros-cons-agent-<suffix>.run.app"
SWOT_AGENT_URL="https://swot-agent-<suffix>.run.app"
# ... and so on for all 10
```

---

## 6) Validation and Health Checks

- Confirm services are running:
  ```powershell
  gcloud run services list --region $REGION
  ```
- Open a service URL in the browser to verify it responds.
- For agents using ADK’s API server, a basic health endpoint is usually available at `/` or `/health` depending on your implementation.

---

## 7) Troubleshooting & Pitfalls

- `--location` must be a region (e.g., `us-central1`), not a multi-region (`us`).
- Use the same region for Artifact Registry and Cloud Run to reduce egress and simplify configs.
- Ensure `GOOGLE_API_KEY` is set for each service; missing keys cause model calls to fail.
- If `gcloud` prompts for confirmation, add `--quiet` for non-interactive flows.
- Docker must be running locally for builds and pushes.
- If deploy fails with image permission issues, re-run:
  ```powershell
  gcloud auth configure-docker "$REGION-docker.pkg.dev"
  ```
- Tag names: prefer stable tags like `:latest` or semantic versions (e.g., `:v1.0.0`).

---

## 8) Optional Hardening

- Restrict unauthenticated access (remove `--allow-unauthenticated` and set IAM bindings).
- Set service memory/CPU:
  ```powershell
  gcloud run services update <service> --region $REGION --memory 512Mi --cpu 1
  ```
- Add labels to services for easier filtering:
  ```powershell
  gcloud run services update <service> --region $REGION --update-labels app=foursight,agent=<name>
  ```

---

## 9) One‑Shot Bootstrap Script (Optional)

The following script ties together creation of the repo, building, pushing, deploying, and writing URLs to `.env`.

```powershell
param(
  [string]$ProjectId = "<YOUR_PROJECT_ID>",
  # The Region is now read from the .env file automatically.
  [string]$RepoName   = "foursight-agents",
  [string]$GeminiKey  = "<YOUR_GEMINI_API_KEY>"
)

# Read CLOUD_RUN_REGION from .env
$regionLine = Get-Content .\.env | Select-String -Pattern "^CLOUD_RUN_REGION="
if (-not $regionLine) { throw "CLOUD_RUN_REGION not found in .env" }
$Region = ($regionLine.ToString() -split '=')[1].Trim()
Write-Host "Using Region: $Region"

# Set project and enable services
gcloud config set project $ProjectId
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com

# Create repo (idempotent – ignore error if exists)
try {
  gcloud artifacts repositories create $RepoName --location=$Region --repository-format=docker --description="FourSight agents"
} catch { Write-Host "Repo may already exist: $RepoName" }

# Auth Docker to Artifact Registry
gcloud auth configure-docker "$Region-docker.pkg.dev"

# Registry path and env
$env:REPO = "$Region-docker.pkg.dev/$ProjectId/$RepoName"
$EnvVars  = "GOOGLE_API_KEY=$GeminiKey,LOG_LEVEL=INFO"

# Build & push
$agents = @(
  @{ dir = "pros_cons_agent"; image = "pros-cons-agent" },
  @{ dir = "swot_agent"; image = "swot-agent" },
  @{ dir = "cost_benefit_agent"; image = "cost-benefit-agent" },
  @{ dir = "five_ws_and_h_agent"; image = "five-ws-and-h-agent" },
  @{ dir = "five_whys_agent"; image = "five-whys-agent" },
  @{ dir = "ten_ten_ten_agent"; image = "ten-ten-ten-agent" },
  @{ dir = "kepner_tregoe_agent"; image = "kepner-tregoe-agent" },
  @{ dir = "rational_decision_making_agent"; image = "rational-decision-making-agent" },
  @{ dir = "weighted_matrix_agent"; image = "weighted-matrix-agent" },
  @{ dir = "decide_model_agent"; image = "decide-model-agent" }
)

foreach ($a in $agents) {
  $path = "services/" + $a.dir
  docker build -t "$env:REPO/$($a.image):latest" $path
  docker push "$env:REPO/$($a.image):latest"
}

# Deploy & collect URLs
$envPath = ".env"
foreach ($a in $agents) {
  $service = $a.image
  gcloud run deploy $service --image "$env:REPO/$service:latest" --region $Region --allow-unauthenticated --port 8080 --set-env-vars $EnvVars
  $url = gcloud run services describe $service --region $Region --format "value(status.url)"

  switch ($service) {
    "pros-cons-agent"                { $key = "PROS_CONS_AGENT_URL" }
    "swot-agent"                     { $key = "SWOT_AGENT_URL" }
    "cost-benefit-agent"             { $key = "COST_BENEFIT_AGENT_URL" }
    "five-ws-and-h-agent"            { $key = "FIVE_WS_AND_H_AGENT_URL" }
    "five-whys-agent"                { $key = "FIVE_WHYS_AGENT_URL" }
    "ten-ten-ten-agent"              { $key = "TEN_TEN_TEN_AGENT_URL" }
    "kepner-tregoe-agent"            { $key = "KEPNER_TREGOE_AGENT_URL" }
    "rational-decision-making-agent" { $key = "RATIONAL_DECISION_MAKING_AGENT_URL" }
    "weighted-matrix-agent"          { $key = "WEIGHTED_MATRIX_AGENT_URL" }
    "decide-model-agent"             { $key = "DECIDE_MODEL_AGENT_URL" }
  }

  if ($key) { Add-Content -Path $envPath -Value "$key=\"$url\""; Write-Host "$key -> $url" }
}
```

---

With this guide, you can fully reset the Artifact Registry, build/push all agent images, deploy them to Cloud Run, and populate your `.env` with the resulting service URLs.