# Supplementary: near-misses using BEST asks (min over asks), since /book
# asks are DESC-sorted and asks[0] is the worst price (~0.999).
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    near = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            if total <= 1.005:
                near.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near.sort()
    brackets.sort()
    print(f"Markets with both books priced: {priced}")
    print(f"Detector brackets: {len(brackets)}")
    for s, e, q in brackets:
        print(f"  BRACKET {s:.4f} edge={e:.4f} | {q}")
    print(f"Best-ask near-misses (<=1.005): {len(near)}")
    for total, q, yp, np, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    if near:
        print(f"Floor (lowest best-ask sum): {near[0][0]:.4f}")

asyncio.run(scan())
