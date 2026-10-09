import asyncio, logging, json, time
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

    priced = 0
    all_rows = []
    best = None  # (sum, question, yes_min, no_min, liq)
    near = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ym = min(float(a['price']) for a in yes_book.asks)
        nm = min(float(a['price']) for a in no_book.asks)
        total = ym + nm
        priced += 1
        all_rows.append((round(total, 4), m.question[:50], ym, nm, m.liquidity))
        if best is None or total < best[0]:
            best = (total, m.question[:60], ym, nm, m.liquidity)
        if total <= 1.005:
            near.append((round(total, 4), m.question[:50], ym, nm, m.liquidity))
    near.sort()
    with open('_tmp_cron_20261009T0941Z_supp_data.json', 'w') as f:
        json.dump({
            'markets': len(markets),
            'priced': priced,
            'rows': [{'sum': round(t, 4), 'q': q, 'yes': y, 'no': n, 'liq': l} for t, q, y, n, l in near],
            'all_rows': all_rows,
            'brackets': [{'sum': t, 'edge': e, 'shares': s, 'q': q} for t, e, s, q in brackets],
        }, f)
    print(f"priced_markets={priced}")
    if best:
        print(f"FLOOR sum={best[0]:.4f} Yes@{best[2]:.3f} No@{best[3]:.3f} liq={best[4]} | {best[1]}")
    print(f"near(mind-asks,<=1.005)={len(near)}")
    for t, q, y, n, l in near[:10]:
        print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | {q}")
    print(f"detector_brackets={len(brackets)}")
    for t, e, s, q in brackets:
        print(f"  {t:.3f} edge={e:.4f} shares={s} | {q}")

asyncio.run(supp())
