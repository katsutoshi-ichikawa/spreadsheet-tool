#!/bin/bash
set -e

PROJECT=spreadsheet-tool-495211
REGION=asia-northeast1
IMAGE=asia-northeast1-docker.pkg.dev/${PROJECT}/spreadsheet-tool/summary-report:latest
SA=995722960236-compute@developer.gserviceaccount.com

echo "=== Step 1: イメージをビルド＆プッシュ ==="
gcloud builds submit \
  --tag="${IMAGE}" \
  /home/ichikawa/spreadsheet-tool \
  --project="${PROJECT}"

echo "=== Step 2: Secret Managerのアクセス権付与 ==="
gcloud secrets add-iam-policy-binding spreadsheet-sa-key \
  --member="serviceAccount:${SA}" \
  --role="roles/secretmanager.secretAccessor" \
  --project="${PROJECT}" 2>/dev/null || true

echo "=== Step 3: Cloud Run デプロイ ==="
gcloud run deploy summary-report \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --set-secrets="/secrets/sa-key.json=spreadsheet-sa-key:latest" \
  --set-env-vars="SA_KEY_PATH=/secrets/sa-key.json,APP_PASSWORD=8016,SECRET_KEY=563cc0d16f7a13ab31130c00d2ccf05df0b900f1ce280ad43201d8dd908743b8" \
  --project="${PROJECT}"

echo "=== デプロイ完了 ==="
