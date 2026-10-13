import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    two_sided = 0
    totals = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            totals.append((y + n, m.question[:55], y, n, len(yb.asks), len(nb.asks)))
            two_sided += 1

    totals.sort()
    bands = {1.000: 0, 1.005: 0, 1.010: 0, 1.020: 0, 1.030: 0}
    for t, *_ in totals:
        for b in sorted(bands):
            if t <= b:
                bands[b] += 1
                break
    median = totals[len(totals)//2][0] if totals else None
    print(f"two-sided markets: {two_sided}/{len(markets)} ({100*two_sided/len(markets):.1f}% not bracketable)")
    print(f"median 2-sided min-ask floor: {median:.4f}")
    for b in sorted(bands):
        print(f"  <= {b:.3f}: n={bands[b]}")
    print("lowest 5:")
    for t, q, y, n, ay, an in totals[:5]:
        print(f"  {t:.4f} | Y@{y:.4f} ({ay} asks) N@{n:.4f} ({an} asks) | {q}")

asyncio.run(floor())
