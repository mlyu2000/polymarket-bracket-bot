import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

Config.SCAN_SORT_BY='volume'
Config.MAX_MARKETS_PER_SCAN=500
Config.MIN_LIQUIDITY_USDC=100

async def scan():
    api=PolymarketAPI()
    detector=BracketDetector()
    markets=await api.fetch_active_markets()
    print(f"Fetched {len(markets)}")
    # Use detector logic but print details
    for m in markets[:50]:
        if m.liquidity<100: continue
        books=await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yb,nb=books[0]
        if not yb or not nb: continue
        if not yb.asks or not nb.asks: continue
        # Detector uses min price
        yes_ask = min(yb.asks, key=lambda a: float(a['price']))
        no_ask = min(nb.asks, key=lambda a: float(a['price']))
        yes_price = float(yes_ask['price'])
        no_price = float(no_ask['price'])
        total = yes_price + no_price
        if total <= 1.005:
            print(f"{total:.3f} yes {yes_price:.3f} no {no_price:.3f} liq {m.liquidity:.0f} | {m.question[:60]}")

asyncio.run(scan())
