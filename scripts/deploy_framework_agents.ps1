# One-shot deploy script for all framework agents (excluding orchestrator)
# Builds Docker images, pushes to Artifact Registry, deploys to Cloud Run,
# captures service URLs, updates .env, and performs health checks.

<#
MANUAL INPUT NOTES:
- Ensure you have run: `gcloud auth login`, `gcloud config set project <PROJECT_ID>`.
- Ensure `.env` at project root has these keys:
  - `GEMINI_API_KEY`            # Required for agents using Gemini
  - `GCP_PROJECT_ID`           # Your GCP project ID
  - `CLOUD_RUN_REGION`         # Region for Cloud Run (e.g., us-central1)
  - `Agents_Artifact_Repository` # Artifact Registry repository ID (e.g., four-sight-agents)
- If your Artifact Registry is multi-region (e.g., `us`), set `$REGISTRY_LOCATION` below accordingly.
#>

param(
  [string]$Tag = "latest"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Load-DotEnv {
  param([string]$Path)
  $envMap = @{}
  if (-not (Test-Path $Path)) { throw "Missing .env at $Path" }
  Get-Content -Path $Path | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq '' -or $line.StartsWith('#')) { return }
    $split = $line.Split('=',2)
    if ($split.Count -eq 2) {
      $key = $split[0].Trim()
      $val = $split[1].Trim()
      # strip surrounding quotes if present
      if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Trim('"') }
      $envMap[$key] = $val
    }
  }
  return $envMap
}

function Save-DotEnv {
  param(
    [string]$Path,
    [hashtable]$EnvMap
  )
  $lines = @()
  foreach ($k in $EnvMap.Keys) {
    $v = $EnvMap[$k]
    # Quote values to keep consistency for URLs and keys
    $lines += ('{0}="{1}"' -f $k, $v)
  }
  Set-Content -Path $Path -Value $lines -Encoding UTF8
}

function Ensure-Artifact-Repo {
  param(
    [string]$Project,
    [string]$Location,
    [string]$Repository
  )
  Write-Host "Ensuring Artifact Registry repo '$Repository' in '$Location'..."
  $exists = $false
  try {
    $repoInfo = gcloud artifacts repositories describe $Repository --project $Project --location $Location --format=json 2>$null
    if ($LASTEXITCODE -eq 0 -and $repoInfo) { $exists = $true }
  } catch {}
  if (-not $exists) {
    gcloud artifacts repositories create $Repository `
      --repository-format=docker `
      --location=$Location `
      --project=$Project `
      --description="FourSight agents images" | Out-Host
  }
}

function Build-Push-Deploy-Agent {
  param(
    [string]$ServiceName,
    [string]$FolderName,
    [string]$DockerfilePath,
    [string]$EnvKey,
    [string]$Project,
    [string]$Region,
    [string]$RegistryLocation,
    [string]$Repository,
    [hashtable]$EnvMap
  )
  $image = ('{0}-docker.pkg.dev/{1}/{2}/{3}:{4}' -f $RegistryLocation, $Project, $Repository, $ServiceName, $Tag)

  Write-Host "\n=== Building '$ServiceName' from '$DockerfilePath' ==="
  docker build -f $DockerfilePath -t $image . | Out-Host

  Write-Host "\n=== Pushing image '$image' ==="
  docker push $image | Out-Host

  # Prepare env vars for Cloud Run
  $gemini = $EnvMap['GEMINI_API_KEY']
  if (-not $gemini) { throw "GEMINI_API_KEY missing in .env" }

  Write-Host "\n=== Deploying Cloud Run service '$ServiceName' ==="
  gcloud run deploy $ServiceName `
    --image $image `
    --platform managed `
    --region $Region `
    --project $Project `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --set-env-vars GEMINI_API_KEY=$gemini | Out-Host

  Write-Host "\n=== Capturing service URL for '$ServiceName' ==="
  $url = gcloud run services describe $ServiceName --region $Region --project $Project --format="value(status.url)"
  if (-not $url) { throw "Failed to retrieve Cloud Run URL for $ServiceName" }
  Write-Host "URL: $url"

  # Health check: try /healthz then /
  $healthy = $false
  foreach ($path in @('/healthz','/')) {
    try {
      $resp = Invoke-WebRequest -Uri ("$url$path") -TimeoutSec 30 -UseBasicParsing
      if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) { $healthy = $true; break }
    } catch {}
  }
  if (-not $healthy) { Write-Warning "Health check failed for $ServiceName at $url" } else { Write-Host "Health check passed for $ServiceName" }

  # Update .env value
  $EnvMap[$EnvKey] = $url
}

# Script root
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $root
$envPath = Join-Path $projectRoot ".env"
$envMap = Load-DotEnv -Path $envPath

$PROJECT = $envMap['GCP_PROJECT_ID']
if (-not $PROJECT) { throw "GCP_PROJECT_ID missing in .env" }
$REGION = $envMap['CLOUD_RUN_REGION']
if (-not $REGION) { throw "CLOUD_RUN_REGION missing in .env" }
$REPO = $envMap['Agents_Artifact_Repository']
if (-not $REPO) { throw "Agents_Artifact_Repository missing in .env" }

# If your Artifact Registry uses multi-region (e.g., 'us'), set this manually here:
$REGISTRY_LOCATION = $REGION  # Change to 'us' if your repo is multi-region

Ensure-Artifact-Repo -Project $PROJECT -Location $REGISTRY_LOCATION -Repository $REPO

# Define agents: folder, service name and .env key
$agents = @(
  @{ Folder='pros_cons_agent';             Service='pros-cons-agent';             EnvKey='PROS_CONS_AGENT_URL' },
  @{ Folder='swot_agent';                  Service='swot-agent';                  EnvKey='SWOT_AGENT_URL' },
  @{ Folder='cost_benefit_agent';          Service='cost-benefit-agent';          EnvKey='COST_BENEFIT_AGENT_URL' },
  @{ Folder='weighted_matrix_agent';       Service='weighted-matrix-agent';       EnvKey='WEIGHTED_MATRIX_AGENT_URL' },
  @{ Folder='five_ws_and_h_agent';         Service='five-ws-and-h-agent';         EnvKey='FIVE_WS_AND_H_AGENT_URL' },
  @{ Folder='ten_ten_ten_agent';           Service='ten-ten-ten-agent';           EnvKey='TEN_TEN_TEN_AGENT_URL' },
  @{ Folder='decide_model_agent';          Service='decide-model-agent';          EnvKey='DECIDE_MODEL_AGENT_URL' },
  @{ Folder='kepner_tregoe_agent';         Service='kepner-tregoe-agent';         EnvKey='KEPNER_TREGOE_AGENT_URL' },
  @{ Folder='rational_decision_making_agent'; Service='rational-decision-making-agent'; EnvKey='RATIONAL_DECISION_MAKING_AGENT_URL' },
  @{ Folder='five_whys_agent';             Service='five-whys-agent';             EnvKey='FIVE_WHYS_AGENT_URL' },
  @{ Folder='five_whys_agent';             Service='five-whys-agent';             EnvKey='FIVE_WHYS_AGENT_URL' }
)

foreach ($a in $agents) {
  $folder = $a.Folder
  $service = $a.Service
  $envKey = $a.EnvKey
  $dockerfile = Join-Path $projectRoot ("services/$folder/Dockerfile")
  if (-not (Test-Path $dockerfile)) { throw "Dockerfile not found: $dockerfile" }

  Build-Push-Deploy-Agent `
    -ServiceName $service `
    -FolderName $folder `
    -DockerfilePath $dockerfile `
    -EnvKey $envKey `
    -Project $PROJECT `
    -Region $REGION `
    -RegistryLocation $REGISTRY_LOCATION `
    -Repository $REPO `
    -EnvMap $envMap
}

Write-Host "\n=== Writing updated URLs to .env ==="
Save-DotEnv -Path $envPath -EnvMap $envMap

Write-Host "\nAll framework agents processed."
Write-Host "- Artifact Registry: $REGISTRY_LOCATION-docker.pkg.dev/$PROJECT/$REPO"
Write-Host "- Tag: $Tag"

Write-Host "\nNext steps:"
Write-Host "- Verify each agent URL in .env opens in a browser."
Write-Host "- Re-run script with a different -Tag to version images if desired."