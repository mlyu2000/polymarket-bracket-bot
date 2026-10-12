import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=50)
    print(f"fetched {len(markets)}")
    for m in markets[:5]:
        print(m.question[:60], m.liquidity, m.clob_token_ids)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    cnt=0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            cnt+=1
            print("OPP", m.question[:60], opp.yes_price, opp.no_price, opp.total_cost, opp.net_edge)
    print("total opps", cnt)

asyncio.run(test())
