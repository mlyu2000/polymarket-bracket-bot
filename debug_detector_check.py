import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=100)
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        if not books:
            continue
        yes_book, no_book = books[0]
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print('OPPORTUNITY', m.question[:60], opp.total_cost, opp.net_edge)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_min = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
                no_min = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
                total = yes_min + no_min
                if total <= 1.005:
                    print('NEAR', total, m.question[:60], 'liq', m.liquidity)

asyncio.run(main())
