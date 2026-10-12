# Supplementary run: near-misses computed with MIN ask (best ask) instead of asks[0].
# Polymarket /book returns asks DESC-sorted, so asks[0] is the WORST ask (~0.999).
import asyncio, logging
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

    opps = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.question[:60], m.liquidity))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return len(markets), opps, near_misses

n, opps, near = asyncio.run(scan())
print(f"[min-ask] markets={n} real_brackets={len(opps)} near_misses(<=1.005)={len(near)}")
for o in opps:
    print(f"  REAL BRACKET sum={o[0]:.3f} edge={o[1]:.4f} Yes@{o[2]:.3f} No@{o[3]:.3f} shares={o[4]} liq={o[6]} | {o[5]}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
