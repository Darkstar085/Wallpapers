#!/usr/bin/env bash
set -euo pipefail

DAYS="${DAYS:-30}"
DRY_RUN=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --days) DAYS="$2"; shift 2 ;;
    --execute) DRY_RUN=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "Usage: $0 [--days N] [--dry-run|--execute]"; exit 2 ;;
  esac
done

if ! [[ "$DAYS" =~ ^[1-9][0-9]*$ ]]; then
  echo "DAYS must be a positive integer."
  exit 2
fi

CUTOFF="$(date -u -d "-$DAYS days" +%s)"

runs="$(gh run list --repo Darkstar085/Wallpapers --limit 1000 --json databaseId,createdAt,name)"
while IFS=$'\t' read -r id created name; do
  [[ -z "$id" ]] && continue
  ts="$(date -u -d "$created" +%s)"
  if (( ts < CUTOFF )); then
    if (( DRY_RUN )); then
      echo "Would delete run $id: $name"
    else
      if ! gh run delete "$id" --repo Darkstar085/Wallpapers; then
        echo "Run $id is already gone or could not be deleted; continuing."
      fi
    fi
  fi
done < <(python -c 'import json,sys; [(print(r["databaseId"],r["createdAt"],r["name"],sep="\t")) for r in json.load(sys.stdin)]' <<< "$runs")

if (( DRY_RUN )); then
  echo "Would clear GitHub Actions caches after run cleanup."
else
  if ! gh cache delete --all --repo Darkstar085/Wallpapers; then
    echo "No Actions caches found or caches could not be deleted; continuing."
  fi
fi
