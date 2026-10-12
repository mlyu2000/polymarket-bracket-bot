#!/usr/bin/env bash
# Combined 2026-09-29 cron runner: verbatim scan + min-ask floor supplement
set -uo pipefail
cd /home/ml/projects/polymarket-bracket-bot
source venv/bin/activate
TS=20260929T_run$(date -u +%H%M)
mkdir -p runs
python _cron_20260929_scan_verbatim.py > runs/scan_${TS}_out.txt 2> runs/scan_${TS}_err.txt
echo "VERBATIM_EXIT=$?"
python _cron_20260929_supp_minask.py > runs/supp_${TS}_out.txt 2> runs/supp_${TS}_err.txt
echo "SUPP_EXIT=$?"
echo "TS=$TS"
echo "--- verbatim out ---"
cat runs/scan_${TS}_out.txt
echo "--- verbatim err tail ---"
tail -5 runs/scan_${TS}_err.txt
echo "--- supp out ---"
cat runs/supp_${TS}_out.txt
echo "--- supp err tail ---"
tail -5 runs/supp_${TS}_err.txt
