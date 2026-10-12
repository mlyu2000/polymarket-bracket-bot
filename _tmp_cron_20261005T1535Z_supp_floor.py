"""Supplementary true-floor scan: best ask = min over ladder (CLOB asks are DESC-sorted).
Reports true near-misses (sum<=1.005) and the global floor across priced books."""
import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def run():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    detected = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
        opp = detector.detect(m, yb, nb)
        if opp:
            detected.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))

    rows.sort()
    out = {
        'priced_books': len(rows),
        'detector_hits': detected,
        'true_near_misses_le_1005': [r for r in rows if r[0] <= 1.005],
        'floor_top10': rows[:10],
    }
    print(json.dumps(out, indent=1, default=str))

asyncio.run(run())
