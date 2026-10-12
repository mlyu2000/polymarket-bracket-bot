import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)} markets")
    best = 1.5
    best_q = ""
    count_le_1 = 0
    count_le_1_005 = 0
    near = []
    for m in markets:
        # Skip liquidity filter to see all
        yes_id = m.clob_token_ids[0]
        no_id = m.clob_token_ids[1]
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_price = min(float(a['price']) for a in yes_book.asks)
        no_price = min(float(a['price']) for a in no_book.asks)
        total = yes_price + no_price
        if total < best:
            best = total
            best_q = m.question[:80]
        if total < 1.0:
            count_le_1 += 1
            print(f"BRACKET {total:.4f} | Yes {yes_price:.3f} No {no_price:.3f} | liq {m.liquidity} | {m.question[:80]}")
        if total <= 1.005:
            count_le_1_005 += 1
            near.append((total, m.question[:80], m.liquidity))
    print(f"Best total: {best:.4f} | {best_q}")
    print(f"Brackets <1.0: {count_le_1}")
    print(f"Near <=1.005: {count_le_1_005}")
    near_sorted = sorted(near)
    for t, q, liq in near_sorted[:10]:
        print(f"  {t:.4f} | liq {liq} | {q}")

asyncio.run(test())
