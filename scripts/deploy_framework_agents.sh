#!/usr/bin/env bash

# One-shot deploy script for all framework agents (excluding orchestrator)
# For Google Cloud Shell/Linux. Uses Cloud Build to build in Google infra,
# pushes to Artifact Registry, deploys to Cloud Run, captures URLs,
# updates .env, and performs health checks.

set -euo pipefail

# MANUAL INPUT NOTES:
# - Ensure you have run: `gcloud auth login` and `gcloud config set project <PROJECT_ID>`.
# - Ensure `.env` at project root has these keys:
#     GEMINI_API_KEY                 # Required for agents using Gemini
#     GCP_PROJECT_ID                 # Your GCP project ID
#     CLOUD_RUN_REGION               # Region for Cloud Run (e.g., us-central1)
#     Agents_Artifact_Repository     # Artifact Registry repository ID (e.g., four-sight-agents)
# - If your Artifact Registry is multi-region (e.g., 'us'), set REGISTRY_LOCATION below accordingly.

TAG="${1:-latest}"

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing .env at $ENV_FILE" >&2
  exit 1
fi

read_env() {
  local key="$1"
  local val
  val=$(grep -E "^${key}=" "$ENV_FILE" | head -n1 | cut -d'=' -f2- | sed 's/^\"//; s/\"$//')
  echo "$val"
}

upsert_env_var() {
  local key="$1"; shift
  local value="$1"; shift || true
  value="\"${value}\"" # keep quotes for consistency
  if grep -qE "^${key}=" "$ENV_FILE"; then
    # Replace existing line
    awk -v k="$key" -v v="$value" 'BEGIN{FS=OFS="="} $1==k{$2=v; print; next} {print}' "$ENV_FILE" > "$ENV_FILE.tmp" && mv "$ENV_FILE.tmp" "$ENV_FILE"
  else
    # Append new line
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

PROJECT="$(read_env GCP_PROJECT_ID)"
REGION="$(read_env CLOUD_RUN_REGION)"
REPO="$(read_env Agents_Artifact_Repository)"
GEMINI_API_KEY="$(read_env GEMINI_API_KEY)"

if [[ -z "$PROJECT" || -z "$REGION" || -z "$REPO" || -z "$GEMINI_API_KEY" ]]; then
  echo "One or more required .env values are missing (GCP_PROJECT_ID, CLOUD_RUN_REGION, Agents_Artifact_Repository, GEMINI_API_KEY)." >&2
  exit 1
fi

# If your Artifact Registry uses multi-region (e.g., 'us'), set this manually here:
REGISTRY_LOCATION="$REGION"  # Change to 'us' if your repo is multi-region

ensure_artifact_repo() {
  local project="$1"; local location="$2"; local repository="$3"
  echo "Ensuring Artifact Registry repo '$repository' in '$location'..."
  if ! gcloud artifacts repositories describe "$repository" --project "$project" --location "$location" >/dev/null 2>&1; then
    gcloud artifacts repositories create "$repository" \
      --repository-format=docker \
      --location="$location" \
      --project="$project" \
      --description="FourSight agents images"
  fi
}

build_push_deploy_agent() {
  local service_name="$1"
  local folder="$2"
  local dockerfile_path="$ROOT_DIR/services/$folder/Dockerfile"
  local env_key="$3"

  if [[ ! -f "$dockerfile_path" ]]; then
    echo "Dockerfile not found: $dockerfile_path" >&2
    exit 1
  fi

  local image="${REGISTRY_LOCATION}-docker.pkg.dev/${PROJECT}/${REPO}/${service_name}:${TAG}"

  # Generate a Cloud Build config to build using the agent's Dockerfile with repo root as context
  local cb_dir="$ROOT_DIR/.cloudbuild"
  local cb_cfg="$cb_dir/${service_name}.yaml"
  mkdir -p "$cb_dir"

  cat > "$cb_cfg" <<EOF
steps:
- name: 'gcr.io/cloud-builders/docker'
  args:
    - 'build'
    - '-f'
    - 'services/${folder}/Dockerfile'
    - '-t'
    - '${image}'
    - '.'
- name: 'gcr.io/cloud-builders/docker'
  args:
    - 'push'
    - '${image}'
images:
- '${image}'
EOF

  echo -e "\n=== Submitting Cloud Build for '$service_name' using config '$cb_cfg' ==="
  gcloud builds submit "$ROOT_DIR" \
    --project "$PROJECT" \
    --ignore-file "$ROOT_DIR/.gcloudignore" \
    --config "$cb_cfg"

  echo -e "\n=== Deploying Cloud Run service '$service_name' ==="
  gcloud run deploy "$service_name" \
    --image "$image" \
    --platform managed \
    --region "$REGION" \
    --project "$PROJECT" \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}"

  echo -e "\n=== Capturing service URL for '$service_name' ==="
  local url
  url=$(gcloud run services describe "$service_name" --region "$REGION" --project "$PROJECT" --format="value(status.url)")
  if [[ -z "$url" ]]; then
    echo "Failed to retrieve Cloud Run URL for $service_name" >&2
    exit 1
  fi
  echo "URL: $url"

  echo -e "\n=== Health check for '$service_name' ==="
  local healthy=0
  for path in "/healthz" "/"; do
    if curl -sS --max-time 30 -o /dev/null -w "%{http_code}" "$url$path" | grep -qE '^(2|3)'; then
      healthy=1; break
    fi
  done
  if [[ "$healthy" -eq 1 ]]; then
    echo "Health check passed for $service_name"
  else
    echo "WARNING: Health check failed for $service_name at $url" >&2
  fi

  upsert_env_var "$env_key" "$url"
}

ensure_artifact_repo "$PROJECT" "$REGISTRY_LOCATION" "$REPO"

declare -a AGENTS=(
  "pros-cons-agent:pros_cons_agent:PROS_CONS_AGENT_URL"
  "swot-agent:swot_agent:SWOT_AGENT_URL"
  "cost-benefit-agent:cost_benefit_agent:COST_BENEFIT_AGENT_URL"
  "weighted-matrix-agent:weighted_matrix_agent:WEIGHTED_MATRIX_AGENT_URL"
  "five-ws-and-h-agent:five_ws_and_h_agent:FIVE_WS_AND_H_AGENT_URL"
  "ten-ten-ten-agent:ten_ten_ten_agent:TEN_TEN_TEN_AGENT_URL"
  "decide-model-agent:decide_model_agent:DECIDE_MODEL_AGENT_URL"
  "kepner-tregoe-agent:kepner_tregoe_agent:KEPNER_TREGOE_AGENT_URL"
  "rational-decision-making-agent:rational_decision_making_agent:RATIONAL_DECISION_MAKING_AGENT_URL"
  "five-whys-agent:five_whys_agent:FIVE_WHYS_AGENT_URL"
)

for entry in "${AGENTS[@]}"; do
  IFS=':' read -r service folder envkey <<<"$entry"
  build_push_deploy_agent "$service" "$folder" "$envkey"
done

echo -e "\nAll framework agents processed."
echo "- Artifact Registry: ${REGISTRY_LOCATION}-docker.pkg.dev/${PROJECT}/${REPO}"
echo "- Tag: ${TAG}"
echo -e "\nNext steps:"
echo "- Verify each agent URL in .env opens in a browser."
echo "- Re-run script with a different tag: scripts/deploy_framework_agents.sh 2025-11-09"