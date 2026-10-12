import json, os, subprocess
TS = "${TS}"
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
msg = (f"cron {TS}: scan verbatim (500 mkts, 63.2s, 0 brackets, 0 near-miss asks[0]); "
       f"supp min-ask floor 1.0030 (BTC >90k Y@0.015 N@0.988 liq=40.4k; ETH 3-3.1k Y@0.004 N@0.999 liq=3.9k); "
       f"<=1.005 n=4; <=1.010 n=15; structural 60/424/2/14")
r = subprocess.run(["git", "commit", "-m", msg], cwd=".", capture_output=True, text=True)
print(r.stdout[-500:] if r.stdout else "", r.stderr[-500:] if r.stderr else "")
