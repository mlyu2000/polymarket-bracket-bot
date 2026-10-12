import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def check():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=100)
    print(f"Fetched {len(markets)} markets")
    count = 0
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print(f"FOUND: {m.question[:60]} sum={opp.total_cost} edge={opp.net_edge}")
            count +=1
        else:
            # debug
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yp = float(yes_book.asks[0]['price'])
                np_ = float(no_book.asks[0]['price'])
                total = yp+np_
                if total <= 1.005:
                    print(f"Near: {m.question[:60]} total={total} yp={yp} np={np_} liq={m.liquidity}")
    print(f"Total opps {count}")

asyncio.run(check())
