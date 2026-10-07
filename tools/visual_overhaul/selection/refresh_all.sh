#!/usr/bin/env bash
# Re-derive everything that does not need donor checkouts: curation status, groups, all ledgers, queue, status, validation.
# Evidence files (evidence_*.py) need donor checkouts and are regenerated separately.
set -euo pipefail
cd "$(dirname "$0")/../../.."
D=docs/visual_overhaul
ARGS=()
LEDGERS=(--ledger A=$D/LANE_A_RECOVERED_CURATION.json --ledger B=$D/LANE_B_RECOVERED_CURATION.json --ledger CDE=$D/LANE_CDE_RECOVERED_CURATION.json)
for id in $(python3 -c "import json;print(' '.join(e['id'] for e in json.load(open('$D/catalog_extensions/MANIFEST.json'))['extensions']))"); do
  ARGS+=(--catalog-extension $D/catalog_extensions/$id/CATALOG.json)
  LEDGERS+=(--ledger X_$id=$D/catalog_extensions/$id/CURATION.json)
done
python3 tools/visual_overhaul/build_donor_curation_status.py --catalog $D/DONOR_ASSET_CATALOG.json "${ARGS[@]}" "${LEDGERS[@]}" \
  --write-json $D/DONOR_CURATION_STATUS.json --write-md $D/DONOR_CURATION_STATUS.md
S=tools/visual_overhaul/selection
python3 $S/build_candidate_groups.py > /dev/null
for s in $(python3 -c "import json;print(' '.join(json.load(open('$D/selection/SUBSYSTEMS.json'))['subsystems']))"); do
  python3 $S/select_subsystem.py --subsystem "$s" > /dev/null
done
python3 $S/build_outcomes.py > /dev/null
python3 $S/build_opportunities.py > /dev/null
python3 $S/build_queue.py
python3 $S/build_status.py > /dev/null
python3 $S/validate_selection.py
