import json, datetime, subprocess, sys

# Re-run the min-ask scan and persist structured data to runs/
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    floors = []
    two_sided = one_sided = 0
    tiers = {"lt1.000": 0, "le1.005": 0, "le1.010": 0, "le1.020": 0, "le1.050": 0}
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            two_sided += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            s = yp + np_
            if s < 1.000: tiers["lt1.000"] += 1
            if s <= 1.005: tiers["le1.005"] += 1
            if s <= 1.010: tiers["le1.010"] += 1
            if s <= 1.020: tiers["le1.020"] += 1
            if s <= 1.050: tiers["le1.050"] += 1
            floors.append((s, m.question[:60], round(yp, 4), round(np_, 4), m.liquidity))
        else:
            one_sided += 1
    floors.sort()
    return {
        "ts_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "markets": len(markets), "two_sided": two_sided, "one_sided": one_sided,
        "tiers": tiers,
        "floor_leaders": [
            {"sum": round(s, 4), "q": q, "yes": y, "no": n, "liq": l}
            for s, q, y, n, l in floors[:8]
        ],
        "liquid_near_floor": [
            {"sum": round(s, 4), "q": q, "yes": y, "no": n, "liq": l}
            for s, q, y, n, l in sorted(
                [f for f in floors if f[4] is not None and f[4] >= 10000],
                key=lambda f: f[0]
            )[:8]
        ],
        "scan_time": round(scan_time, 1),
    }

data = asyncio.run(scan())
ts = datetime.datetime.now(datetime.timezone.utc)
stamp = ts.strftime("_tmp_cron_%Y%m%d_%H%MZ")
out = f"runs/{stamp}_supp_data.json"
with open(out, "w") as f:
    json.dump(data, f, indent=2)
print("WROTE", out)
print(json.dumps(data, indent=2))
