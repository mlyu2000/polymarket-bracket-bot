import asyncio, logging
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    npriced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        s = ya + na
        npriced += 1
        if s <= 1.005:
            rows.append((s, ya, na, m.question[:55], m.liquidity))
    rows.sort()
    print(f"priced={npriced}")
    if rows:
        for s, ya, na, q, liq in rows[:10]:
            print(f"  {s:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq} | {q}")
    else:
        all_sums = []
        for m, (yb, nb) in zip(markets, books):
            if not yb or not nb or not yb.asks or not nb.asks:
                continue
            all_sums.append(min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks))
        print(f"none <=1.005; true floor={min(all_sums):.4f}")

asyncio.run(main())
