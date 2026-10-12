import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def debug_detector():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=20)
    for m in markets:
        if m.liquidity < 100:
            continue
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if not yes_book or not no_book:
            continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print("DETECTED", m.question[:60], opp.total_cost, opp.yes_price, opp.no_price)
        else:
            if yes_book.asks and no_book.asks:
                yes_best = min(float(a['price']) for a in yes_book.asks)
                no_best = min(float(a['price']) for a in no_book.asks)
                total = yes_best + no_best
                if total < 1.01:
                    print("NEAR", m.question[:60], total, yes_best, no_best, "liq", m.liquidity)
                    # Check why detector rejected
                    print("  market.active", m.active, "closed", m.closed, "liq", m.liquidity)
                    # check asks order
                    print("  yes asks first 3", [float(a['price']) for a in yes_book.asks[:3]])
                    print("  no asks first 3", [float(a['price']) for a in no_book.asks[:3]])

asyncio.run(debug_detector())
