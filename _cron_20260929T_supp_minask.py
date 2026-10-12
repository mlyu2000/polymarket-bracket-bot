import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    sums = []
    true_brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            true_brackets.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            sums.append((ya+na, m.question[:50], ya, na, m.liquidity))
    sums.sort()
    print(f"detector.detect() brackets: {len(true_brackets)}")
    for o in true_brackets:
        print(f"  [{o.total_cost:.4f}] edge={o.net_edge:.4f} yes@{o.yes_price:.3f} no@{o.no_price:.3f} shares={o.max_shares} | {o.market.question[:60] if hasattr(o,'market') else ''}")
    print(f"Top 10 lowest min-ask sums (of {len(sums)} priced markets):")
    for total, q, ya, na, liq in sums[:10]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"Markets with min-ask sum <= 1.005: {sum(1 for s in sums if s[0] <= 1.005)}")

asyncio.run(supp())
