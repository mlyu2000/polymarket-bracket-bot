import asyncio, json, logging, time
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

    brackets = []
    near_misses = []  # total <= 1.005, using TRUE best ask (min) per side
    priced = 0
    one_sided = {'yes_only': 0, 'no_only': 0, 'empty': 0, 'both': 0}

    for m, (yb, nb) in zip(markets, all_books):
        has_y = bool(yb and yb.asks)
        has_n = bool(nb and nb.asks)
        if has_y and has_n:
            one_sided['both'] += 1
        elif has_y:
            one_sided['yes_only'] += 1
        elif has_n:
            one_sided['no_only'] += 1
        else:
            one_sided['empty'] += 1
        if not (has_y and has_n):
            continue
        priced += 1

        # TRUE best ask per side (asks are DESC-sorted; asks[0] is WORST)
        yes_ask = min(yb.asks, key=lambda a: float(a['price']))
        no_ask = min(nb.asks, key=lambda a: float(a['price']))
        yes_p = float(yes_ask['price'])
        no_p = float(no_ask['price'])
        total = yes_p + no_p

        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append({
                'q': m.question, 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity,
            })
        elif total <= 1.005:
            near_misses.append((round(total, 4), m.question, round(yes_p, 4), round(no_p, 4), m.liquidity))

    near_misses.sort()
    return {
        'ts': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()),
        'markets': len(markets), 'priced': priced, 'scan_time': round(scan_time, 1),
        'one_sided': one_sided,
        'floor': near_misses[0][0] if near_misses else None,
        'floor_q': near_misses[0][1] if near_misses else None,
        'floor_yes': near_misses[0][2] if near_misses else None,
        'floor_no': near_misses[0][3] if near_misses else None,
        'floor_liq': near_misses[0][4] if near_misses else None,
        'band': [list(x) for x in near_misses[:5]],
        'brackets': brackets, 'detector_opps': len(brackets),
    }


result = asyncio.run(scan())
ts = result['ts']
with open(f'runs/_tmp_cron_{ts}_supp_data.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"SCAN {ts}: {result['markets']} markets / {result['priced']} priced / {result['scan_time']}s")
print(f"one-sided: {result['one_sided']}")
print(f"BRACKETS (detector, sum<1.00): {result['detector_opps']}")
for b in result['brackets']:
    print(f"  RED {b['sum']:.3f} edge={b['edge']:.4f} | Y@{b['yes']:.3f} N@{b['no']:.3f} | {b['shares']} sh | {b['q'][:60]}")
print(f"TRUE FLOOR (min-ask, <=1.005): {result['floor']} | {result['floor_q']}")
if result['band']:
    print(f"  floor detail: Y@{result['floor_yes']} N@{result['floor_no']} liq={result['floor_liq']}")
    for t, q, yp, np_, liq in result['band'][1:]:
        print(f"  {t:.4f} | Y@{yp:.4f} N@{np_:.4f} liq={liq} | {q[:50]}")
