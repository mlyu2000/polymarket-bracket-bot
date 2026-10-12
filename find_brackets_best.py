import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    brackets = []
    for m in markets:
        if len(m.clob_token_ids) != 2:
            continue
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_best = min(yes_book.asks, key=lambda a: float(a['price']))
        no_best = min(no_book.asks, key=lambda a: float(a['price']))
        yes_price = float(yes_best['price'])
        no_price = float(no_best['price'])
        total = yes_price + no_price
        if total < 1.0:
            brackets.append((total, m.question[:60], m.liquidity, yes_price, no_price))
    brackets.sort()
    print(f"Found {len(brackets)} brackets with best asks")
    for total, q, liq, yp, np in brackets[:20]:
        print(f"{total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")

asyncio.run(f())
