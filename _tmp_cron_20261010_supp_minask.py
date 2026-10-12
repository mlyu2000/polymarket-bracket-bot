import asyncio, logging, time, json
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

    rows = []
    opps = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:80],
                'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity
            })
            continue
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            rows.append((total, m.question[:60], yp, np_, m.liquidity, len(yes_book.asks), len(no_book.asks)))
    rows.sort()
    return {'markets': len(markets), 'priced': priced, 'opps': opps, 'rows': rows, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"markets={result['markets']} priced={result['priced']} scan={result['scan_time']:.1f}s")
print(f"detector brackets: {len(result['opps'])}")
for o in result['opps']:
    print(f"  BRACKET sum={o['sum']:.3f} edge={o['edge']:.4f} yes={o['yes']:.3f} no={o['no']:.3f} shares={o['shares']} liq={o['liq']} | {o['q']}")
le15 = [r for r in result['rows'] if r[0] <= 1.015]
le1005 = [r for r in result['rows'] if r[0] <= 1.005]
lt100 = [r for r in result['rows'] if r[0] < 1.0]
print(f"true floor (min-ask): {result['rows'][0][0]:.4f}" if result['rows'] else "no priced rows")
print(f"sum<1.00: {len(lt100)} | sum<=1.005: {len(le1005)} | sum<=1.015: {len(le15)}")
print("closest 8 by true sum (min-ask):")
for total, q, yp, np_, liq, ny, nn in result['rows'][:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | asksY={ny} asksN={nn} | {q}")
with open('_tmp_cron_20261010_minask.json', 'w') as f:
    json.dump({'floor': result['rows'][0][0] if result['rows'] else None,
               'le1005': len(le1005), 'le1015': len(le15),
               'closest': [{'sum': r[0], 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]} for r in result['rows'][:15]]}, f, indent=1)
