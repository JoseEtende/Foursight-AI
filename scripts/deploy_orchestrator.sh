#!/usr/bin/env bash

# Hardened orchestrator deployment for Cloud Run (Linux/Cloud Shell)
# Mirrors validations from framework agents deploy, avoids common pitfalls.

set -euo pipefail

SERVICE_NAME=${1:-orchestrator}
TAG=${TAG:-latest}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_PATH="${PROJECT_ROOT}/.env"

require_commands() {
  for cmd in gcloud docker sed awk curl; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "Error: required command missing: $cmd"; exit 1; }
  done
}

load_dotenv() {
  if [[ ! -f "$ENV_PATH" ]]; then
    echo "Error: .env not found at $ENV_PATH"; exit 1
  fi
  set -a
  # shellcheck source=/dev/null
  . "$ENV_PATH"
  set +a
}

ensure_project() {
  local project="$1"
  echo "Setting gcloud project to $project"
  gcloud config set project "$project" >/dev/null
}

ensure_apis() {
  echo "Ensuring required APIs are enabled"
  local apis=(
    run.googleapis.com
    artifactregistry.googleapis.com
    cloudbuild.googleapis.com
    firestore.googleapis.com
  )
  for api in "${apis[@]}"; do
    gcloud services enable "$api" >/dev/null || true
  done
}

ensure_repo() {
  local project="$1" location="$2" repo="$3"
  echo "Ensuring Artifact Registry repo '$repo' in '$location'"
  if ! gcloud artifacts repositories describe "$repo" --project "$project" --location "$location" >/dev/null 2>&1; then
    gcloud artifacts repositories create "$repo" \
      --repository-format=docker \
      --location="$location" \
      --project="$project" \
      --description="FourSight agents images" >/dev/null
  fi
}

configure_docker_auth() {
  local location="$1"
  local host="${location}-docker.pkg.dev"
  echo "Configuring Docker auth for $host"
  gcloud auth configure-docker "$host" -q >/dev/null
}

validate_agent_urls() {
  local keys=(
    PROS_CONS_AGENT_URL SWOT_AGENT_URL COST_BENEFIT_AGENT_URL WEIGHTED_MATRIX_AGENT_URL
    FIVE_WHYS_AGENT_URL FIVE_WS_AND_H_AGENT_URL TEN_TEN_TEN_AGENT_URL DECIDE_MODEL_AGENT_URL
    KEPNER_TREGOE_AGENT_URL RATIONAL_DECISION_MAKING_AGENT_URL
  )
  local missing=()
  for k in "${keys[@]}"; do
    if [[ -z "${!k:-}" ]]; then missing+=("$k"); fi
  done
  if (( ${#missing[@]} > 0 )); then
    echo "Error: missing agent URLs in .env: ${missing[*]}"; exit 1
  fi
}

build_push_image() {
  local image="$1"
  echo "Building orchestrator image: $image"
  docker build -f services/orchestrator/Dockerfile -t "$image" .
  echo "Pushing image: $image"
  docker push "$image"
}

build_env_vars_arg() {
  local kv=()
  # Required
  [[ -n "${GEMINI_API_KEY:-}" ]] && kv+=("GEMINI_API_KEY=${GEMINI_API_KEY}")
  kv+=("PROS_CONS_AGENT_URL=${PROS_CONS_AGENT_URL}")
  kv+=("SWOT_AGENT_URL=${SWOT_AGENT_URL}")
  kv+=("COST_BENEFIT_AGENT_URL=${COST_BENEFIT_AGENT_URL}")
  kv+=("WEIGHTED_MATRIX_AGENT_URL=${WEIGHTED_MATRIX_AGENT_URL}")
  kv+=("FIVE_WHYS_AGENT_URL=${FIVE_WHYS_AGENT_URL}")
  kv+=("FIVE_WS_AND_H_AGENT_URL=${FIVE_WS_AND_H_AGENT_URL}")
  kv+=("TEN_TEN_TEN_AGENT_URL=${TEN_TEN_TEN_AGENT_URL}")
  kv+=("DECIDE_MODEL_AGENT_URL=${DECIDE_MODEL_AGENT_URL}")
  kv+=("KEPNER_TREGOE_AGENT_URL=${KEPNER_TREGOE_AGENT_URL}")
  kv+=("RATIONAL_DECISION_MAKING_AGENT_URL=${RATIONAL_DECISION_MAKING_AGENT_URL}")
  # Firestore client project hint
  kv+=("GOOGLE_CLOUD_PROJECT=${GCP_PROJECT_ID}")
  (IFS=","; echo "${kv[*]}")
}

deploy_cloud_run() {
  local service="$1" image="$2" region="$3" project="$4" env_vars="$5"
  local args=(
    run deploy "$service"
    --image "$image"
    --region "$region"
    --project "$project"
    --platform managed
    --allow-unauthenticated
    --port 8080
    --ingress all
    --memory 1Gi
    --cpu 1
    --timeout 900
    --concurrency 10
    --min-instances 0
    --set-env-vars "$env_vars"
  )
  if [[ -n "${CLOUD_RUN_SERVICE_ACCOUNT:-}" ]]; then
    args+=(--service-account "$CLOUD_RUN_SERVICE_ACCOUNT")
  fi
  echo "Deploying Cloud Run service '$service' in $region"
  gcloud "${args[@]}" >/dev/null
}

get_service_url() {
  local service="$1" region="$2" project="$3"
  gcloud run services describe "$service" --region "$region" --project "$project" --format="value(status.url)"
}

write_orchestrator_url_to_env() {
  local url="$1"
  if grep -q '^ORCHESTRATOR_URL=' "$ENV_PATH"; then
    sed -i "s|^ORCHESTRATOR_URL=.*|ORCHESTRATOR_URL=\"$url\"|" "$ENV_PATH"
  else
    echo "ORCHESTRATOR_URL=\"$url\"" >> "$ENV_PATH"
  fi
}

smoke_test() {
  local url="$1"
  # Try POST /run with health_check, tolerate 2xx-4xx
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
    -d '{"input":{"action":"health_check"}}' "$url/run" || true)
  if [[ -z "$code" || "$code" -eq 000 ]]; then
    code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
      -d '{"input":{}}' "$url/run" || true)
  fi
  if [[ "$code" -ge 200 && "$code" -lt 500 ]]; then
    echo "Smoke test passed for orchestrator ($code)"
  else
    echo "Warning: smoke test failed for orchestrator ($code)" >&2
  fi
}

main() {
  require_commands
  load_dotenv

  # Required envs
  : "${GCP_PROJECT_ID:?GCP_PROJECT_ID missing in .env}"
  : "${CLOUD_RUN_REGION:?CLOUD_RUN_REGION missing in .env}"
  : "${Agents_Artifact_Repository:?Agents_Artifact_Repository missing in .env}"
  validate_agent_urls

  local REGISTRY_LOCATION
  REGISTRY_LOCATION="${REGISTRY_LOCATION:-$CLOUD_RUN_REGION}"
  local REPO_PATH="${REGISTRY_LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${Agents_Artifact_Repository}"
  local IMAGE="${REPO_PATH}/${SERVICE_NAME}:${TAG}"

  ensure_project "$GCP_PROJECT_ID"
  ensure_apis
  ensure_repo "$GCP_PROJECT_ID" "$REGISTRY_LOCATION" "$Agents_Artifact_Repository"
  configure_docker_auth "$REGISTRY_LOCATION"
  build_push_image "$IMAGE"

  local ENV_VARS
  ENV_VARS="$(build_env_vars_arg)"
  deploy_cloud_run "$SERVICE_NAME" "$IMAGE" "$CLOUD_RUN_REGION" "$GCP_PROJECT_ID" "$ENV_VARS"

  local URL
  URL="$(get_service_url "$SERVICE_NAME" "$CLOUD_RUN_REGION" "$GCP_PROJECT_ID")"
  echo "Orchestrator URL: $URL"
  write_orchestrator_url_to_env "$URL"
  echo "ORCHESTRATOR_URL written to .env"
  smoke_test "$URL"
}

main "$@"