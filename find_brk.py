import asyncio
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from config import Config

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    # Use volume sort but check all
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)}")
    hits = []
    for m in markets:
        if m.liquidity < 100:
            continue
        yb = await api.fetch_order_book(m.clob_token_ids[0])
        nb = await api.fetch_order_book(m.clob_token_ids[1])
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        y_price = min(float(a['price']) for a in yb.asks)
        n_price = min(float(a['price']) for a in nb.asks)
        total = y_price + n_price
        if total < 1.0:
            hits.append((total, m.question[:60], y_price, n_price))
            print(f"{total:.4f} {m.question[:60]}")
    print("hits", len(hits))

asyncio.run(scan())
