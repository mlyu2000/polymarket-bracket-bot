import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    for m in markets:
        if 'highest temperature in atlanta' in m.question.lower() or 'atlanta' in m.question.lower():
            print(f"ACTIVE MKT: {m.question[:90]}")
            print(f"  active={m.active} closed={m.closed} liq={m.liquidity:,.0f} end={m.end_date}")
    # check book for the 80-81 Oct 14 market
    for m in markets:
        if '80-81' in m.question and 'atlanta' in m.question.lower():
            print(f"FOUND: {m.question}")
            yb, nb = await asyncio.gather(
                api.fetch_order_book(m.clob_token_ids[0]),
                api.fetch_order_book(m.clob_token_ids[1]))
            for name, b in [('YES', yb), ('NO', nb)]:
                if b and b.asks:
                    prices = sorted(float(a['price']) for a in b.asks)
                    print(f"  {name} asks n={len(b.asks)} min={prices[0]:.3f} max={prices[-1]:.3f}")
                else:
                    print(f"  {name}: NO ASKS (book={b})")

asyncio.run(main())
