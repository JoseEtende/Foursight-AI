Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

param(
  [string]$ServiceName = "orchestrator"
)

function Load-DotEnv {
  param([string]$Path)
  if (-not (Test-Path $Path)) { throw ".env not found at $Path" }
  Get-Content $Path | ForEach-Object {
    if ($_ -match '^[\s#]') { return }
    if (-not $_) { return }
    $pair = $_ -split '=', 2
    if ($pair.Count -lt 2) { return }
    $key = $pair[0].Trim()
    $val = $pair[1].Trim()
    # Strip surrounding quotes
    if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Trim('"') }
    if ($key) { $env:$key = $val }
  }
}

function Require-Commands {
  $required = @('gcloud','docker')
  foreach ($cmd in $required) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "Required command not found: $cmd" }
  }
}

function Ensure-Project {
  param([string]$ProjectId)
  Write-Host "Setting gcloud project to $ProjectId"
  gcloud config set project $ProjectId | Out-Null
}

function Ensure-Apis {
  Write-Host "Ensuring required APIs are enabled"
  $apis = @(
    'run.googleapis.com',
    'artifactregistry.googleapis.com',
    'cloudbuild.googleapis.com',
    'firestore.googleapis.com'
  )
  foreach ($api in $apis) {
    gcloud services enable $api | Out-Null
  }
}

function Ensure-Repo {
  param([string]$RepoName, [string]$Location, [string]$ProjectId)
  try {
    gcloud artifacts repositories describe $RepoName --location $Location --project $ProjectId | Out-Null
    Write-Host "Artifact Registry repo '$RepoName' exists in $Location"
  }
  catch {
    Write-Host "Creating Artifact Registry repo '$RepoName' in $Location"
    gcloud artifacts repositories create $RepoName `
      --repository-format=docker `
      --location=$Location `
      --project=$ProjectId `
      --description="FourSight agents repository" | Out-Null
  }
}

function Configure-DockerAuth {
  param([string]$Region)
  $host = "$Region-docker.pkg.dev"
  Write-Host "Configuring Docker auth for $host"
  gcloud auth configure-docker $host -q | Out-Null
}

function Build-And-Push-Image {
  param([string]$RepoPath, [string]$Tag)
  $image = "$RepoPath/orchestrator:$Tag"
  Write-Host "Building orchestrator image: $image"
  docker build -f services\orchestrator\Dockerfile -t $image .
  if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }
  Write-Host "Pushing image: $image"
  docker push $image
  if ($LASTEXITCODE -ne 0) { throw "Docker push failed" }
  return $image
}

function Build-EnvVarsArg {
  # Collect env vars to pass to Cloud Run
  $keys = @(
    'GEMINI_API_KEY',
    'PROS_CONS_AGENT_URL',
    'SWOT_AGENT_URL',
    'COST_BENEFIT_AGENT_URL',
    'WEIGHTED_MATRIX_AGENT_URL',
    'FIVE_WHYS_AGENT_URL',
    'FIVE_WS_AND_H_AGENT_URL',
    'TEN_TEN_TEN_AGENT_URL',
    'DECIDE_MODEL_AGENT_URL',
    'KEPNER_TREGOE_AGENT_URL',
    'RATIONAL_DECISION_MAKING_AGENT_URL'
  )
  # Always pass project id for Firestore client
  if ($env:GCP_PROJECT_ID) { $keys += 'GOOGLE_CLOUD_PROJECT' }
  $pairs = @()
  foreach ($k in $keys) {
    $v = if ($k -eq 'GOOGLE_CLOUD_PROJECT') { $env:GCP_PROJECT_ID } else { [Environment]::GetEnvironmentVariable($k) }
    if ($null -ne $v -and $v -ne '') { $pairs += "$k=$v" }
  }
  if ($pairs.Count -eq 0) { return $null }
  return ($pairs -join ',')
}

function Validate-AgentUrls {
  $required = @(
    'PROS_CONS_AGENT_URL','SWOT_AGENT_URL','COST_BENEFIT_AGENT_URL','WEIGHTED_MATRIX_AGENT_URL',
    'FIVE_WHYS_AGENT_URL','FIVE_WS_AND_H_AGENT_URL','TEN_TEN_TEN_AGENT_URL','DECIDE_MODEL_AGENT_URL',
    'KEPNER_TREGOE_AGENT_URL','RATIONAL_DECISION_MAKING_AGENT_URL'
  )
  $missing = @()
  foreach ($k in $required) {
    $v = [Environment]::GetEnvironmentVariable($k)
    if (-not $v) { $missing += $k }
  }
  if ($missing.Count -gt 0) { throw ("Missing agent URLs in .env: " + ($missing -join ', ')) }
}

function Deploy-CloudRun {
  param([string]$ServiceName, [string]$Image, [string]$Region, [string]$ProjectId)
  $envArg = Build-EnvVarsArg
  $cmd = @(
    'run','deploy', $ServiceName,
    '--image', $Image,
    '--region', $Region,
    '--project', $ProjectId,
    '--platform','managed',
    '--allow-unauthenticated',
    '--port','8080',
    '--ingress','all',
    '--memory','1Gi',
    '--cpu','1',
    '--timeout','900s',
    '--concurrency','10',
    '--min-instances','0'
  )
  if ($env:CLOUD_RUN_SERVICE_ACCOUNT) { $cmd += @('--service-account', $env:CLOUD_RUN_SERVICE_ACCOUNT) }
  if ($envArg) { $cmd += @('--set-env-vars', $envArg) }
  Write-Host "Deploying Cloud Run service '$ServiceName' in $Region"
  gcloud @cmd | Out-Null
}

function Get-ServiceUrl {
  param([string]$ServiceName, [string]$Region)
  return (gcloud run services describe $ServiceName --region $Region --format 'value(status.url)')
}

function Write-OrchestratorUrlToEnv {
  param([string]$Path, [string]$Url)
  if (-not (Test-Path $Path)) { return }
  $content = Get-Content $Path
  $hasKey = $false
  for ($i=0; $i -lt $content.Length; $i++) {
    if ($content[$i] -match '^ORCHESTRATOR_URL=') { $content[$i] = "ORCHESTRATOR_URL="$Url""; $hasKey = $true }
  }
  if (-not $hasKey) { $content += "ORCHESTRATOR_URL="$Url"" }
  Set-Content -Path $Path -Value $content
}

function Smoke-TestOrchestrator {
  param([string]$Url)
  $ok = $false
  try {
    $resp = Invoke-WebRequest -Uri ("$Url/run") -Method POST -ContentType 'application/json' -Body '{"input":{"action":"health_check"}}' -TimeoutSec 30 -UseBasicParsing
    if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) { $ok = $true }
  } catch {
    try {
      $resp2 = Invoke-WebRequest -Uri ("$Url/run") -Method POST -ContentType 'application/json' -Body '{"input":{}}' -TimeoutSec 30 -UseBasicParsing
      if ($resp2.StatusCode -ge 200 -and $resp2.StatusCode -lt 500) { $ok = $true }
    } catch {}
  }
  if (-not $ok) { Write-Warning "Smoke test failed for orchestrator at $Url" } else { Write-Host "Smoke test passed for orchestrator" }
}

#
# Main
#
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $root
$envPath = Join-Path $projectRoot '.env'
Load-DotEnv -Path $envPath
Require-Commands

if (-not $env:GCP_PROJECT_ID) { throw 'GCP_PROJECT_ID missing in .env' }
if (-not $env:CLOUD_RUN_REGION) { throw 'CLOUD_RUN_REGION missing in .env' }
if (-not $env:Agents_Artifact_Repository) { throw 'Agents_Artifact_Repository missing in .env' }
Validate-AgentUrls

$REGISTRY_LOCATION = if ($env:REGISTRY_LOCATION) { $env:REGISTRY_LOCATION } else { $env:CLOUD_RUN_REGION }
$repoPath = "$REGISTRY_LOCATION-docker.pkg.dev/$env:GCP_PROJECT_ID/$env:Agents_Artifact_Repository"
Ensure-Project -ProjectId $env:GCP_PROJECT_ID
Ensure-Apis
Ensure-Repo -RepoName $env:Agents_Artifact_Repository -Location $REGISTRY_LOCATION -ProjectId $env:GCP_PROJECT_ID
Configure-DockerAuth -Region $REGISTRY_LOCATION
$image = Build-And-Push-Image -RepoPath $repoPath -Tag 'latest'

Deploy-CloudRun -ServiceName $ServiceName -Image $image -Region $env:CLOUD_RUN_REGION -ProjectId $env:GCP_PROJECT_ID
$url = Get-ServiceUrl -ServiceName $ServiceName -Region $env:CLOUD_RUN_REGION
Write-Host "Orchestrator URL: $url"
Write-OrchestratorUrlToEnv -Path $envPath -Url $url
Write-Host "ORCHESTRATOR_URL written to .env"
Smoke-TestOrchestrator -Url $url