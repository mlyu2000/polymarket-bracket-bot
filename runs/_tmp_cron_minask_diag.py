import asyncio, json, time
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    two_sided = 0
    brackets = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        two_sided += 1
        y_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        n_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp, np_ = float(y_ask["price"]), float(n_ask["price"])
        total = yp + np_
        rows.append((round(total, 3), m.question[:60], yp, np_, m.liquidity))
        if detector.detect(m, yes_book, no_book):
            brackets += 1

    rows.sort(key=lambda r: (r[0], -r[4]))
    floor = rows[0][0] if rows else None
    top12 = rows[:12]
    tiers = {
        "le1.005": sum(1 for r in rows if r[0] <= 1.005),
        "le1.010": sum(1 for r in rows if r[0] <= 1.010),
        "le1.020": sum(1 for r in rows if r[0] <= 1.020),
        "le1.050": sum(1 for r in rows if r[0] <= 1.050),
        "lt1.000": sum(1 for r in rows if r[0] < 1.000),
    }
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ")
    supp = {
        "run_ts_utc": ts,
        "markets": len(markets),
        "scan_time_s": round(scan_time, 1),
        "brackets": brackets,
        "near_miss_count": len(rows[:12]),
        "near_misses_top": [{"sum": r[0], "q": r[1], "yes": r[2], "no": r[3], "liq": r[4]} for r in top12[:5]],
        "floor": floor,
        "tiers": tiers,
        "bracketable": two_sided,
        "not_bracketable": len(markets) - two_sided,
        "asks0_near_miss_artifact": 0,
        "method": "min(all asks) - detector-equivalent; asks[0] is worst ask (DESC sort)",
    }
    tier_rec = {"ts": ts, "brackets": brackets, "markets": len(markets),
                "two_sided": two_sided,
                "pct_not_bracketable": round((len(markets) - two_sided) / len(markets) * 100, 1),
                "tiers": tiers, "floor": floor,
                "top12": [{"total": r[0], "q": r[1], "yes": r[2], "no": r[3], "liq": r[4]} for r in top12],
                "scan_time_verbatim": round(scan_time, 1)}
    with open(f"runs/_tmp_cron_{ts}_supp_data.json", "w") as f:
        json.dump({"near_misses": [], "diag": {"min_asks": [list(r) for r in top12]}, **supp}, f, indent=1)
    with open(f"runs/_tmp_cron_{ts}_tiers.json", "w") as f:
        json.dump(tier_rec, f, indent=1)
    with open("results/cron_scan_history.jsonl", "a") as f:
        f.write(json.dumps(tier_rec) + "\n")
    print(f"TS={ts} | markets={len(markets)} | scan={scan_time:.1f}s | brackets={brackets}")
    print(f"FLOOR={floor} | two_sided={two_sided} ({supp['pct_not_bracketable'] if 'pct_not_bracketable' in supp else ''})")
    print(f"tiers: {tiers}")
    print("TOP12 (total | Yes@x No@y | liq | question):")
    for r in top12:
        print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq {r[4]:.0f} | {r[1]}")
    return ts, tier_rec

asyncio.run(scan())
