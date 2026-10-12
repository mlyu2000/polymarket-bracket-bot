import json, os, subprocess
TS = "20261011T2328Z"
# Copy artifacts into runs/ (gitignored tmp naming, unpushed per convention)
os.makedirs("runs", exist_ok=True)
for src, dst in [
    (f"_tmp_cron_{TS}_scan_out.txt", f"runs/_tmp_cron_{TS}_scan_out.txt"),
    (f"_tmp_cron_{TS}_supp_out.txt", f"runs/_tmp_cron_{TS}_supp_minask_out.txt"),
    (f"_tmp_cron_{TS}_supp_out.txt", f"runs/_tmp_cron_{TS}_supp_data.json"),
]:
    if os.path.exists(src):
        with open(src) as f: data = f.read()
        with open(dst, "w") as f: f.write(data)
        print("copied", src, "->", dst)
subprocess.run(["git", "add", "runs/"], cwd=".")
msg = (f"cron {TS}: scan verbatim (500 mkts, 54.4s, 0 brackets, 0 near-miss asks[0] worst-ask artifact); "
       f"supp min-ask TRUE FLOOR 1.0030 HOLDS 2313Z (BTC >$90k Oct14 Y@0.015 N@0.988 liq=40738; "
       f"ETH $3,000-3,100 Y@0.006 N@0.999 liq=4330; Valladolid O/U 7.5 1.0050; Viking FK (-1.5) 1.0050; "
       f"band<=1.005 n=4 unchanged composition); tiers<=1.010 n=13, <=1.020 n=21 unchanged; "
       f"structural 57/425/3/15 (~89% NOT bracket-able). Floor 1.0030, best gross edge -0.0030, "
       f"0.023 above 0.98 threshold; all-time low 1.0010 (2200Z 10-10) unchanged. "
       f"0 detector opps, 0 executions. Artifacts committed here (unpushed).")
r = subprocess.run(["git", "commit", "-m", msg], cwd=".", capture_output=True, text=True)
print(r.stdout[-500:] if r.stdout else "", r.stderr[-500:] if r.stderr else "")
