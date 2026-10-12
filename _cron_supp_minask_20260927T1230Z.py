import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            t0 = float(yes_book.asks[0]['price']) + float(no_book.asks[0]['price'])
            sums.append((ya+na, t0, m.question[:55], m.liquidity))
    sums.sort()
    return priced, sums

priced, sums = asyncio.run(scan())
print(f"priced markets: {len(sums)}")
print(f"min best-ask sum: {sums[0][0]:.4f}")
print(f"top-5 best-ask sums:")
for s in sums[:5]:
    print(f"  best={s[0]:.4f} | topofbook={s[1]:.4f} | liq={s[3]} | {s[2]}")
under1 = [s for s in sums if s[0] < 1.0]
print(f"count best-ask sum < 1.00: {len(under1)}")
under1005 = [s for s in sums if s[0] <= 1.005]
print(f"count best-ask sum <= 1.005: {len(under1005)}")
