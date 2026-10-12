# Supplemental: true best-ask scan (asks in CLOB /book are DESC-sorted, so
# asks[0] is the WORST ask; detector.py internally uses min()). Recomputes
# near-misses using best ask = min(price for a in asks).
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

    rows = []
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], opp.yes_price, opp.no_price, m.liquidity))
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    priced = len(rows)
    print(f"markets={len(markets)} priced_books={priced}")
    print(f"detector_brackets={len(brackets)}")
    for b in brackets:
        print(f"  BRACKET sum={b[0]:.4f} edge={b[1]:.4f} shares={b[2]} yes@{b[4]:.3f} no@{b[5]:.3f} liq={b[6]} | {b[3]}")
    print("--- true best-ask totals: lowest 15 ---")
    for total, q, ya, na, liq in rows[:15]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near_misses(<=1.005)={len(nm)}")
    for total, q, ya, na, liq in nm[:10]:
        print(f"  NM {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
