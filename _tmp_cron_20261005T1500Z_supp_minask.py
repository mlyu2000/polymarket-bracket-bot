import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    sums = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append({'sum': opp.total_cost, 'edge': opp.net_edge, 'q': m.question[:60]})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yep = min(float(a['price']) for a in yes_book.asks)
            nop = min(float(a['price']) for a in no_book.asks)
            sums.append((yep + nop, m.question[:50], yep, nop, m.liquidity))

    sums.sort()
    out = {
        'priced_markets': len(sums),
        'bracket_count': len(brackets),
        'brackets': brackets,
        'floor_top10': sums[:10],
        'near_miss_le_1005': [s for s in sums if s[0] <= 1.005],
    }
    print(json.dumps(out))

asyncio.run(supp())
