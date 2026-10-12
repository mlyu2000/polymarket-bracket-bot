import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=200)
    print(f"Fetched {len(markets)} markets")
    found = 0
    for m in markets:
        yes_id = m.clob_token_ids[0]
        no_id = m.clob_token_ids[1]
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book:
            await asyncio.sleep(0.05)
            continue
        if not yes_book.asks or not no_book.asks:
            await asyncio.sleep(0.05)
            continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            found += 1
            print(f"OPP: {m.question[:80]} sum={opp.total_cost:.3f} edge={opp.net_edge:.4f}")
        await asyncio.sleep(0.05)
        if found >= 10:
            break
    print(f"Found {found} opps")

asyncio.run(test())
