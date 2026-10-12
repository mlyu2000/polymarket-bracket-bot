import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    # Change sort to liquidity ascending to find low liq markets
    from config import Config
    orig = Config.SCAN_SORT_BY
    # We'll fetch with liquidity sort manually
    import httpx
    # Actually just fetch a sample with different params
    # Simpler: just check markets with very low liquidity
    count = 0
    for m in markets:
        if m.liquidity < 1000:
            yb = await api.fetch_order_book(m.clob_token_ids[0])
            nb = await api.fetch_order_book(m.clob_token_ids[1])
            if not yb or not nb or not yb.asks or not nb.asks:
                continue
            y_price = min(float(a['price']) for a in yb.asks)
            n_price = min(float(a['price']) for a in nb.asks)
            total = y_price + n_price
            if total < 1.0:
                print(f"BRACKET {total:.4f} {m.question[:60]} y {y_price} n {n_price} liq {m.liquidity}")
                count += 1
    print("found", count)

asyncio.run(scan())
