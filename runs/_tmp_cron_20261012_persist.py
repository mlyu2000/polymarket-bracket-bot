import json, subprocess, datetime

ts = "20261012T0306Z"
with open('runs/_tmp_cron_20261012_supp_data.json') as f:
    d = json.load(f)

msg = f"""cron floor scan 2026-10-12 0306Z: scan verbatim (500 mkts, 56.3s, 0 brackets, 0 near-miss asks[0] worst-ask artifact); supp min-ask TRUE FLOOR 1.0030 HOLDS ~9+ scans (was 1.0030 @0253Z). Band (<=1.005) n=3: Valladolid O/U 7.5 TIES floor at 1.0030 (was 1.0050, improved, Y@0.008 N@0.995 liq=6465), BTC >$90k Oct14 1.0030 HOLDING solo-floor now tied (Y@0.015 N@0.988 liq=40345), NEW ETH $3,000-3,100 1.0050 (Y@0.006 N@0.999 liq=3442) replaces NH-02 House seat (dropped out, was 1.0050). TIERS: <=1.005 n=3, <=1.010 n=15 (was 17), <=1.020 n=23 (was 24), <=1.030 n=25. Structural: 57 two_sided / 429 yes_only / 1 no_only / 13 empty of 500 (~86% NOT bracket-able — NO can't be acquired via YES bids; ask-only bracket check complete). Floor history: 1.0010 all-time low 2200Z 10-10; 1.0030 since 2226Z 10-11, now holding 9+ scans incl two-market tie. BEST GROSS EDGE -0.0030, 0.023 above 0.98 actionable threshold; 0 detector opps, 0 executions. Artifacts committed here (unpushed)."""

subprocess.run(['git', 'add', '-A'], check=True)
subprocess.run(['git', 'commit', '-m', msg], check=True)
print("committed:", msg[:80], "...")
