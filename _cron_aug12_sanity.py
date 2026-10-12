import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    empty = 0
    sums = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yp = float(yb.asks[0]['price']); np = float(nb.asks[0]['price'])
            sums.append(yp + np)
        else:
            empty += 1
    sums.sort()
    print(f"markets={len(markets)} empty_books={empty}")
    print(f"valid={len(sums)} min_sum={sums[0]:.3f} max_sum={sums[-1]:.3f} median={sums[len(sums)//2]:.3f}")
    print("5 closest to 1.0:", [round(s,3) for s in sums[:5]])

asyncio.run(main())
