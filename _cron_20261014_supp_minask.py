import asyncio, json, logging, time
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

    two_sided = 0
    yes_only = 0
    no_both = 0
    brackets = []
    tiers = {"le1.050": 0, "le1.020": 0, "le1.010": 0, "le1.005": 0, "lt1.000": 0}
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        yasks = [float(a['price']) for a in yes_book.asks] if yes_book and yes_book.asks else []
        nasks = [float(a['price']) for a in no_book.asks] if no_book and no_book.asks else []
        if not yasks or not nasks:
            yes_only += 1
            continue
        two_sided += 1
        if min(nasks) >= 0.99:
            no_both += 1
        ymin = min(yasks)
        nmin = min(nasks)
        total = ymin + nmin
        if total < 1.0:
            brackets.append((total, m.question[:60], ymin, nmin, m.liquidity))
        if total <= 1.050: tiers["le1.050"] += 1
        if total <= 1.020: tiers["le1.020"] += 1
        if total <= 1.010: tiers["le1.010"] += 1
        if total <= 1.005: tiers["le1.005"] += 1
        if total < 1.000: tiers["lt1.000"] += 1
        if total <= 1.10:
            rows.append({
                "total": round(total, 4), "q": m.question[:70],
                "yes_min": ymin, "no_min": nmin, "liq": m.liquidity,
            })

    brackets.sort()
    rows.sort(key=lambda r: r["total"])
    return {
        "scan_time": scan_time,
        "markets": len(markets),
        "two_sided": two_sided,
        "yes_only": yes_only,
        "no_both": no_both,
        "brackets": brackets,
        "tiers": tiers,
        "rows": rows,
    }

result = asyncio.run(scan())
print(f"🔬 TRUE-FLOOR SCAN (min-all-asks): {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"two-sided={result['two_sided']} yes-only={result['yes_only']} no>=0.99={result['no_both']}")
print(f"BRACKETS (<1.000): {len(result['brackets'])}")
for b in result['brackets'][:20]:
    print(f"  🔴 {b[0]:.4f} | Y{b[2]:.4f} N{b[3]:.4f} | liq {b[4]} | {b[1]}")
print("TIERS:", json.dumps(result['tiers']))
print("CLOSEST (<=1.100):")
for r in result['rows'][:12]:
    print(f"  {r['total']:.4f} | Y{r['yes_min']:.4f} N{r['no_min']:.4f} | liq {r['liq']} | {r['q']}")
print("JSON_START")
print(json.dumps(result))
print("JSON_END")
