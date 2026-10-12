import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not getattr(book, 'asks', None):
        return None
    return min(float(a['price']) for a in book.asks)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    brackets = []
    near = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        ya, na = best_ask(yb), best_ask(nb)
        if ya is None or na is None:
            continue
        priced += 1
        total = ya + na
        rec = (total, m.question[:50], ya, na, m.liquidity)
        if total < 1.00:
            brackets.append(rec)
        elif total <= 1.005:
            near.append(rec)
    brackets.sort()
    near.sort()
    print(f"[min-ask] markets={len(markets)} priced={priced}")
    print(f"[min-ask] TRUE brackets (sum<1.000): {len(brackets)}")
    for t, q, ya, na, liq in brackets[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"[min-ask] near-misses (1.000-1.005): {len(near)}")
    for t, q, ya, na, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
