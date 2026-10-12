import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    print(f"Fetched {len(markets)} markets")
    for m in markets[:5]:
        print(m.question[:60], m.liquidity, m.clob_token_ids)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets[:5]]
    books = await api.fetch_order_books_batch(token_pairs)
    for m, (yb, nb) in zip(markets[:5], books):
        if yb and nb and yb.asks and nb.asks:
            y_min = min(float(a['price']) for a in yb.asks)
            n_min = min(float(a['price']) for a in nb.asks)
            print(f"{m.question[:40]} yes_min={y_min:.3f} no_min={n_min:.3f} sum={y_min+n_min:.3f}")
            # also first ask
            y_first = float(yb.asks[0]['price'])
            n_first = float(nb.asks[0]['price'])
            print(f"  first asks: yes={y_first:.3f} no={n_first:.3f} sum={y_first+n_first:.3f}")

asyncio.run(test())
