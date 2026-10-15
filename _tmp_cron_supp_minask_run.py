import asyncio, logging, time, json, datetime
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    floors = []
    two_sided = 0
    one_sided = 0
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
            floors.append((s, m.question[:55], yp, np_, m.liquidity))
        else:
            one_sided += 1

    floors.sort()

    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            if yp + np_ <= 0.980:
                brackets.append((round(yp + np_, 4), m.question[:55], yp, np_, m.liquidity))

    return {
        "ts_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "markets": len(markets), "two_sided": two_sided, "one_sided": one_sided,
        "tiers": tiers, "brackets_below_098": brackets,
        "floor_top10": [
            {"sum": round(s, 4), "q": q, "yes": y, "no": n, "liq": l}
            for s, q, y, n, l in floors[:10]
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

result = asyncio.run(scan())
print(json.dumps(result, indent=2))
print("=== SUMMARY ===")
print(f"markets={result['markets']} two_sided={result['two_sided']} one_sided={result['one_sided']} ({100*result['one_sided']/result['markets']:.1f}% unbracketable)")
print("tiers:", result['tiers'])
print(f"brackets below 0.980 (net_edge>=0.01): {len(result['brackets_below_098'])}")
for b in result['brackets_below_098']:
    print("  BRACKET", b)
print("floor top10:")
for f in result['floor_top10']:
    print(f"  {f['sum']:.3f} | Y@{f['yes']:.3f} N@{f['no']:.3f} | liq={f['liq']} | {f['q']}")
print("liquid near floor (liq>=10k):")
for f in result['liquid_near_floor']:
    print(f"  {f['sum']:.3f} | Y@{f['yes']:.3f} N@{f['no']:.3f} | liq={f['liq']} | {f['q']}")
