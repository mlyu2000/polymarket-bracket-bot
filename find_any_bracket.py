import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    found = []
    for m in markets:
        if len(m.clob_token_ids) != 2:
            continue
        if m.liquidity < 100:
            continue
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_best = min(yes_book.asks, key=lambda a: float(a['price']))
        no_best = min(no_book.asks, key=lambda a: float(a['price']))
        total = float(yes_best['price']) + float(no_best['price'])
        if total < 1.0:
            found.append((total, m.question[:60], m.liquidity, float(yes_best['price']), float(no_best['price'])))
    found.sort()
    print('found', len(found))
    for t, q, liq, yp, np in found[:20]:
        print(f"{t:.4f} Yes@{yp:.3f} No@{np:.3f} liq={liq} {q}")

asyncio.run(f())
