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

    totals = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a["price"]) for a in yes_book.asks)
        np = min(float(a["price"]) for a in no_book.asks)
        total = yp + np
        totals.append(total)
        if total <= 1.005:
            near.append((total, yp, np, m.question[:70], m.liquidity))

    totals.sort()
    print(f"🔍 Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"📊 min-ask totals: min={min(totals):.4f} median={totals[len(totals)//2]:.4f} max={max(totals):.4f}")
    print(f"📈 Distribution:")
    from collections import Counter
    def bucket(t):
        if t < 1.000: return "<1.000 (arbitrage)"
        if t <= 1.005: return "1.000-1.005"
        if t <= 1.010: return "1.006-1.010"
        if t <= 1.020: return "1.011-1.020"
        if t <= 1.050: return "1.021-1.050"
        return ">1.050"
    bc = Counter(bucket(t) for t in totals)
    for k in ["<1.000 (arbitrage)","1.000-1.005","1.006-1.010","1.011-1.020","1.021-1.050",">1.050"]:
        print(f"  {k:22s}: {bc.get(k,0)}")
    print(f"📊 Near-misses (≤1.005): {len(near)}")
    for total, yp, np, q, liq in near[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
