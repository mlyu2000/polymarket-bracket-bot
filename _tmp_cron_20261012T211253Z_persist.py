import subprocess, sys

TS = "20261012T211253Z"
files = [
    f"_tmp_cron_{TS}_scan_verbatim.py",
    f"_tmp_cron_{TS}_scan_out.txt",
    f"_tmp_cron_{TS}_scan_err.txt",
    f"_tmp_cron_{TS}_supp_minask.py",
    f"_tmp_cron_{TS}_supp_out.txt",
    f"runs/_tmp_cron_{TS}_supp_data.json",
]
for f in files:
    subprocess.run(["git", "add", "-f", f], check=True)
with open(f"_tmp_cron_{TS}_commitmsg.txt") as fh:
    msg = fh.read()
r = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
print(r.stdout)
print(r.stderr, file=sys.stderr)
sys.exit(r.returncode)
