import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []
    brackets_best = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        if total < 1.0:
            brackets_best.append((total, m.question[:60], ya, na, m.liquidity))
        if total <= 1.005:
            best.append((total, m.question[:50], ya, na, m.liquidity))

    best.sort()
    brackets_best.sort()
    print(f"Supp best-ask recalc over {len(markets)} markets")
    print(f"BRACKETS via best asks (sum<1.0): {len(brackets_best)}")
    for t, q, ya, na, liq in brackets_best[:10]:
        print(f"  sum={t:.4f} Yes@{ya:.3f} No@{na:.3f} liq={liq} | {q}")
    print(f"Near-misses via best asks (<=1.005): {len(best)}")
    for t, q, ya, na, liq in best[:10]:
        print(f"  sum={t:.4f} Yes@{ya:.3f} No@{na:.3f} liq={liq} | {q}")

asyncio.run(scan())
