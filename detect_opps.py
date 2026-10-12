import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    opps = []
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
            print(f"OPPORTUNITY: {m.question[:60]} sum={opp.total_cost:.4f} edge={opp.net_edge:.4f}")
    print(f"Total opps: {len(opps)}")

asyncio.run(scan())
