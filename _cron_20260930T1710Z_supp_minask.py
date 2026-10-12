import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from models import OrderBook

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    hits = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            hits.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            if total < 1.00:
                hits.append((total, 1.0 - total, None, '[min-ask] ' + m.question[:60]))
            elif total <= 1.005:
                near.append((total, m.question[:50], ya, na))
    near.sort()
    return hits, near, len(markets)

hits, near, n = asyncio.run(scan())
print(f"Markets scanned: {n}")
print(f"DET + MIN-ASK BRACKETS (best-ask sum < 1.00): {len(hits)}")
for s, e, sh, q in sorted(hits):
    print(f"  sum={s:.4f} edge={e:.4f} shares={sh} | {q}")
print(f"MIN-ASK near-misses (<=1.005): {len(near)}")
for total, q, ya, na in near[:10]:
    print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | {q}")
