# Supplementary: correct near-miss accounting using min(asks) (asks are DESC-sorted,
# so asks[0] in the verbatim script is the WORST ask -> near-miss count always 0).
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    brackets = []
    near = []
    priced = 0
    floor = 10.0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append((opp.total_cost, m.question[:60], opp.net_edge, opp.max_shares, m.liquidity))
            continue
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            t = ya + na
            floor = min(floor, t)
            if t <= 1.005:
                near.append((t, m.question[:50], ya, na, m.liquidity))
    near.sort()
    brackets.sort()
    print(f"priced_markets={priced} brackets={len(brackets)} near_min_ask={len(near)} floor={floor:.4f}")
    for b in brackets[:10]:
        print(f"BRACKET sum={b[0]:.4f} edge={b[2]:.4f} shares={b[3]} liq={b[4]} | {b[1]}")
    for t, q, ya, na, liq in near[:10]:
        print(f"NEAR {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
