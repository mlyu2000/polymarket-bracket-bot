import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    el = time.time() - t0

    rows = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            if total <= 1.005:
                rows.append((total, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"supp scan: {len(markets)} markets in {el:.1f}s | detector brackets: {len(brackets)}")
    for b in brackets:
        print(f"  BRACKET {b.total_cost:.4f} edge={b.net_edge:.4f} Yes@{b.yes_price} No@{b.no_price} shares={b.max_shares}")
    print(f"true best-ask near-misses (<=1.005): {len(rows)}")
    for total, q, ya, na, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(supp())
