import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)} markets")
    count=0
    brackets=0
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets+=1
            print(f"BRACKET: {opp.total_cost:.4f} edge={opp.net_edge:.4f} {m.question[:60]}")
        else:
            yes_asks = yes_book.asks
            no_asks = no_book.asks
            if yes_asks and no_asks:
                yes_min = min(float(a['price']) for a in yes_asks)
                no_min = min(float(a['price']) for a in no_asks)
                total = yes_min + no_min
                if total < 1.005:
                    print(f"NEAR: {total:.4f} {m.question[:60]} yes_min={yes_min} no_min={no_min}")
                    count+=1
    print("brackets", brackets, "near", count)

asyncio.run(test())
