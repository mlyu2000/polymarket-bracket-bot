"""Supplement: near-miss scan using min(asks) — CLOB returns asks DESC-sorted,
so asks[0] in the verbatim cron script is the WORST ask. This recomputes with
the true best (lowest) ask on each side, matching detector.py logic."""
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
    near = []
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append(opp)
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            total = yp + np
            if total <= 1.005:
                near.append((total, m.question[:60], yp, np, m.liquidity))
    near.sort()
    return markets, opps, near

markets, opps, near = asyncio.run(scan())
print(f"Markets scanned: {len(markets)}")
print(f"BRACKETS via detector (net_edge>=min): {len(opps)}")
for o in opps:
    print(f"  🔴 sum={o.total_cost:.4f} edge={o.net_edge:.4f} Yes@{o.yes_price} No@{o.no_price} shares={o.max_shares} | {o.market.question[:60] if hasattr(o,'market') else ''}")
print(f"TRUE near-misses (min-ask sum <=1.005): {len(near)}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if near:
    floor = near[0][0]
    print(f"Observed floor this run: {floor:.4f}")
