import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)} markets")
    count = 0
    found = []
    for m in markets:
        yes_id = m.clob_token_ids[0]
        no_id = m.clob_token_ids[1]
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a["price"]) for a in yes_book.asks)
            no_price = min(float(a["price"]) for a in no_book.asks)
            total = yes_price + no_price
            if total <= 1.005:
                found.append((total, m.question[:80], yes_price, no_price))
                count += 1
        await asyncio.sleep(0.02)
        if count >= 20:
            break
    print(f"Near misses (min ask sum <=1.005): {count}")
    for t,q,yp,np in found[:10]:
        print(f"{t:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

asyncio.run(test())
