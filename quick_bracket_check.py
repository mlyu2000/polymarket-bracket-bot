import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

# Override for faster scan
Config.SCAN_SORT_BY = 'liquidity'
Config.MAX_MARKETS_PER_SCAN = 50
Config.MIN_LIQUIDITY_USDC = 0

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    print(f"Fetched {len(markets)} markets")
    opps = []
    for m in markets:
        if m.liquidity < 100:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yb, nb = books[0]
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append(opp)
            print(f"BRACKET {m.question[:60]} sum {opp.total_cost:.4f} edge {opp.net_edge:.4f}")
    print(f"Total brackets: {len(opps)}")

asyncio.run(scan())
