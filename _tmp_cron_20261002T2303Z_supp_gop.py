import asyncio, logging
from polymarket_api import PolymarketAPI
logging.basicConfig(level=logging.ERROR)

async def check():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    for m in markets:
        if 'Republican Party candidate win the 2026' in m.question:
            yb, nb = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yb, nb = yb[0], nb[0]
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            print(f"{m.question[:70]} | Yes@{ya:.3f} No@{na:.3f} sum={ya+na:.4f} liq={m.liquidity:.0f}")
            return
    print("GOP 2026 market not found in active set")

asyncio.run(check())
