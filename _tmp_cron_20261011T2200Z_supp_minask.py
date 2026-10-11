import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        y_asks = [float(a['price']) for a in (yb.asks if yb and yb.asks else [])]
        n_asks = [float(a['price']) for a in (nb.asks if nb and nb.asks else [])]
        if y_asks and n_asks:
            two_sided += 1
        elif y_asks:
            yes_only += 1
        elif n_asks:
            no_only += 1
        else:
            empty += 1
        if y_asks and n_asks:
            total = min(y_asks) + min(n_asks)
            rows.append((total, m.question[:60], min(y_asks), min(n_asks), m.liquidity))

    rows.sort()
    import json
    with open('/home/ml/projects/polymarket-bracket-bot/_tmp_cron_20261011T2200Z_supp_data.json', 'w') as f:
        json.dump({
            'ts': '20261011T2200Z',
            'priced': len(rows),
            'two_sided': two_sided,
            'yes_only': yes_only,
            'no_only': no_only,
            'empty': empty,
            'true_floor': rows[0][0] if rows else None,
            'floor_market': rows[0][1] if rows else None,
            'band_le_1005': [(t, q, y, n, liq) for t, q, y, n, liq in rows if t <= 1.005],
            'band_le_1020': [(t, q, y, n, liq) for t, q, y, n, liq in rows if t <= 1.020],
        }, f, indent=2)

    print(f"TRUE FLOOR (min-ask): {rows[0][0]:.4f} | {rows[0][1]} | Y@{rows[0][2]:.3f} N@{rows[0][3]:.3f} liq={rows[0][4]}")
    print(f"books: two_sided={two_sided} yes_only={yes_only} no_only={no_only} empty={empty}")
    print("BAND <=1.005:")
    for t, q, y, n, liq in rows:
        if t <= 1.005:
            print(f"  {t:.4f} | Y@{y:.3f} N@{n:.3f} | liq={liq} | {q}")
    print("TIER <=1.020:")
    for t, q, y, n, liq in rows:
        if t <= 1.020:
            print(f"  {t:.4f} | Y@{y:.3f} N@{n:.3f} | {q}")

asyncio.run(supp())
