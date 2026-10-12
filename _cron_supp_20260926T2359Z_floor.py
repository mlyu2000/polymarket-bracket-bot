import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    totals = []
    minask = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        a0 = float(yb.asks[0]['price']) + float(nb.asks[0]['price'])
        am = min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks)
        totals.append((a0, m.question[:60]))
        minask.append((am, m.question[:60]))
    totals.sort(); minask.sort()
    print(f"priced markets: {len(totals)}")
    print("TOP5 best ask[0] sums:")
    for t, q in totals[:5]:
        print(f"  {t:.4f} | {q}")
    print("TOP5 best min-ask sums:")
    for t, q in minask[:5]:
        print(f"  {t:.4f} | {q}")

asyncio.run(floor())
