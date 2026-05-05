#!/bin/bash
gcloud run services add-iam-policy-binding summary-report --region=asia-northeast1 --member="user:katsutoshi.ichikawa@yamahiro.tokyo" --role="roles/run.invoker" --project=spreadsheet-tool-495211
