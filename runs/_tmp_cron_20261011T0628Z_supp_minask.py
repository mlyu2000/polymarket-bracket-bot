import asyncio, json, logging, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from polymarket_api import PolymarketAPI
logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows, priced = [], []
    for m, (yb, nb) in zip(markets, books):
        ya = yb.asks if yb else None
        na = nb.asks if nb else None
        if ya and na:
            yp = min(float(a['price']) for a in ya)
            np_ = min(float(a['price']) for a in na)
            s = yp + np_
            priced.append(s)
            rows.append({'q': m.question, 'yes_ask': yp, 'no_ask': np_, 'sum': round(s, 6), 'liq': m.liquidity})
    priced.sort()
    band = [r for r in rows if r['sum'] <= 1.005]
    band.sort(key=lambda r: r['sum'])
    out = {
        'markets': len(markets), 'priced': len(rows),
        'yes_only': sum(1 for _, (y, n) in zip(markets, books) if (y and y.asks) and not (n and n.asks)),
        'both_empty': sum(1 for _, (y, n) in zip(markets, books) if not (y and y.asks) and not (n and n.asks)),
        'floor': round(priced[0], 6) if priced else None,
        'median': round(priced[len(priced)//2], 4) if priced else None,
        'band_le_1005_n': len(band),
        'actionable_lt_098': sum(1 for s in priced if s < 0.98),
        'best_edge': round(1.0 - priced[0], 4) if priced else None,
        'band_top5': band[:5],
    }
    print(json.dumps(out, indent=2))
    with open(f'runs/_tmp_cron_{__import__("os").environ["TS"]}_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)

asyncio.run(main())
