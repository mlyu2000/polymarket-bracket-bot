import asyncio, json, logging, statistics, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity,
            })

    # True best-ask (min) analysis. CLOB /book asks are DESC-sorted;
    # asks[0] is the WORST ask, detector.py uses min().
    best_all = []
    two_sided = yes_only = empty = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            empty += 1
            continue
        ya, na = bool(yes_book.asks), bool(no_book.asks)
        if not ya and not na:
            empty += 1
            continue
        if ya and na:
            two_sided += 1
        else:
            yes_only += 1
        if not ya or not na:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1.0 or np_ >= 1.0:
            continue
        yes_sz = max((float(a['size']) for a in yes_book.asks if float(a['price']) == yp), default=0)
        no_sz = max((float(a['size']) for a in no_book.asks if float(a['price']) == np_), default=0)
        best_all.append((yp + np_, m.question[:60], yp, np_, m.liquidity, min(yes_sz, no_sz)))
    best_all.sort()

    bands = {}
    for hi in (1.000, 1.005, 1.010, 1.015, 1.020):
        bands[hi] = len([b for b in best_all if b[0] < hi])
    median = round(statistics.median([b[0] for b in best_all]), 4) if best_all else None
    under1 = [b for b in best_all if b[0] < 1.0]
    near = [b for b in best_all if 1.0 <= b[0] <= 1.005]
    le1010 = [b for b in best_all if b[0] <= 1.010]

    print(f"Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"BRACKETS (detector): {len(opps)}")
    for o in opps:
        print(f"  RED {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={int(o['liq'])} | {o['q']}")
    print(f"true min-ask floor: {best_all[0][0]:.4f} ({best_all[0][1]})")
    print(f"bands <1.000: {bands[1.000]} | <1.005: {bands[1.005]} | <=1.010: {bands[1.010]} | <1.015: {bands[1.015]} | <1.020: {bands[1.020]}")
    print(f"median 2-sided min-ask sum: {median} | {two_sided} two-sided / {yes_only} yes-only / {empty} empty")
    print(f"true brackets (sum<1.00): {len(under1)} | near [1.00,1.005]: {len(near)}")
    for total, q, yp, np_, liq, sz in best_all[:5]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={int(liq)} sz={int(sz)} | {q}")
    print("--- <=1.010 list ---")
    for total, q, yp, np_, liq, sz in le1010:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={int(liq)} sz={int(sz)} | {q}")

    data = {
        'ts': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()),
        'markets': len(markets),
        'scan_time_s': round(scan_time, 1),
        'brackets_detector': len(opps),
        'bracket_opps': opps,
        'brackets_true_minask': len(under1),
        'near_misses_true_minask': len(near),
        'best_ask_floor': round(best_all[0][0], 4),
        'bands': {str(k): v for k, v in bands.items()},
        'median_two_sided_sum': median,
        'two_sided': two_sided,
        'yes_only': yes_only,
        'empty': empty,
        'priced_markets': len(best_all),
        'top_true_sums': [{'sum': round(t, 4), 'yes': yp, 'no': np_, 'liq': int(liq), 'sz': int(sz), 'q': q}
                          for t, q, yp, np_, liq, sz in best_all[:10]],
        'le1010': [{'sum': round(t, 4), 'yes': yp, 'no': np_, 'liq': int(liq), 'sz': int(sz), 'q': q}
                   for t, q, yp, np_, liq, sz in le1010],
    }
    with open('runs/_tmp_cron_20261014T030809Z_supp_data.json', 'w') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print("data persisted -> runs/_tmp_cron_20261014T030809Z_supp_data.json")

result = asyncio.run(scan())
