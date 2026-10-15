import asyncio, json, logging, time
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

TS = "20261015T0845Z"

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []  # (sum, q, yes, no, liq)
    two_sided = 0
    one_sided = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        has_y = bool(yes_book and yes_book.asks)
        has_n = bool(no_book and no_book.asks)
        if has_y and has_n:
            two_sided += 1
        else:
            one_sided += 1
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))

    rows.sort()
    tiers = {
        "lt1.000": sum(1 for r in rows if r[0] < 1.000),
        "le1.005": sum(1 for r in rows if r[0] <= 1.005),
        "le1.010": sum(1 for r in rows if r[0] <= 1.010),
        "le1.020": sum(1 for r in rows if r[0] <= 1.020),
        "le1.050": sum(1 for r in rows if r[0] <= 1.050),
    }
    brackets_below_098 = [
        {"sum": r[0], "q": r[1], "yes": r[2], "no": r[3], "liq": r[4]}
        for r in rows if r[0] < 0.98
    ]
    floor_top10 = [
        {"sum": r[0], "q": r[1], "yes": r[2], "no": r[3], "liq": r[4]}
        for r in rows[:10]
    ]
    # liquid near-floor: sums <= 1.010 sorted by liquidity desc
    near = [r for r in rows if r[0] <= 1.010]
    near.sort(key=lambda r: -r[4])
    liquid_near_floor = [
        {"sum": r[0], "q": r[1], "yes": r[2], "no": r[3], "liq": r[4]}
        for r in near[:12]
    ]
    entry = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "markets": len(markets),
        "two_sided": two_sided,
        "one_sided": one_sided,
        "tiers": tiers,
        "brackets_below_098": brackets_below_098,
        "floor_top10": floor_top10,
        "liquid_near_floor": liquid_near_floor,
        "scan_time": scan_time,
    }
    return entry, rows

entry, rows = asyncio.run(scan())
out = f"runs/_tmp_cron_{TS}_supp_data.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(entry, f, ensure_ascii=False, indent=1)
print("WROTE:", out)
print("floor:", rows[0][0], rows[0][1], "| tiers:", json.dumps(entry["tiers"]))
print("two_sided:", entry["two_sided"], "one_sided:", entry["one_sided"])
print("top liquid near floor:")
for r in entry["liquid_near_floor"][:6]:
    print("  ", r["sum"], "liq", round(r["liq"]), "|", r["q"])
