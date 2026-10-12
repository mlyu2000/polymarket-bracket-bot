import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    totals=[]
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb: continue
        if not yb.asks or not nb.asks: continue
        y_first = float(yb.asks[0]['price'])
        n_first = float(nb.asks[0]['price'])
        total = y_first + n_first
        totals.append((total, m.question[:50], y_first, n_first, m.liquidity))
    totals.sort(key=lambda x: x[0])
    print(f"Checked {len(totals)} markets")
    for t in totals[:20]:
        print(f"{t[0]:.4f} | Yes@{t[2]:.3f} No@{t[3]:.3f} | liq={t[4]:.0f} | {t[1]}")

asyncio.run(test())
