#!/bin/bash
set -e

PROJECT=spreadsheet-tool-495211
REGION=asia-northeast1
IMAGE=asia-northeast1-docker.pkg.dev/${PROJECT}/spreadsheet-tool/summary-report:latest
SA=995722960236-compute@developer.gserviceaccount.com

echo "=== Step 1: Secret Managerのアクセス権付与 ==="
gcloud secrets add-iam-policy-binding spreadsheet-sa-key \
  --member="serviceAccount:${SA}" \
  --role="roles/secretmanager.secretAccessor" \
  --project="${PROJECT}"

echo "=== Step 2: Cloud Run デプロイ ==="
gcloud run deploy summary-report \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --platform=managed \
  --no-allow-unauthenticated \
  --set-secrets="/secrets/sa-key.json=spreadsheet-sa-key:latest" \
  --set-env-vars="SA_KEY_PATH=/secrets/sa-key.json" \
  --project="${PROJECT}"

echo "=== デプロイ完了 ==="
