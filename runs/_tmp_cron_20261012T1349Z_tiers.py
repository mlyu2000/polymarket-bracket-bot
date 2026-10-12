import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    floors = []
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        ya = [float(a['price']) for a in (yb.asks if yb and yb.asks else [])]
        na = [float(a['price']) for a in (nb.asks if nb and nb.asks else [])]
        if ya and na:
            two_sided += 1
            floors.append((min(ya) + min(na), m.question[:60], min(ya), min(na), m.liquidity))
        elif ya:
            yes_only += 1
        elif na:
            no_only += 1
        else:
            empty += 1

    floors.sort()
    for t in (1.000, 1.005, 1.010, 1.020, 1.030, 1.040):
        n = sum(1 for f in floors if f[0] <= t)
        print(f"le{t:.3f}: {n}")
    print(f"band<=1.005 members: {[(round(f[0],4), f[1], f[2], f[3], round(f[4],1)) for f in floors if f[0] <= 1.005]}")
    print(f"structural: two_sided={two_sided} yes_only={yes_only} no_only={no_only} empty={empty}")

asyncio.run(main())
