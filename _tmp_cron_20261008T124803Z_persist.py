import asyncio, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    priced = 0
    brackets = 0
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets += 1
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = round(yp + np_, 6)
            priced += 1
            rows.append({'sum': tot, 'q': m.question[:60], 'yes': yp, 'no': np_, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    band = [r for r in rows if r['sum'] <= 1.005]
    out = {
        'run': '20261008T124803Z',
        'ts': '2026-10-08T~12:48Z scan (verbatim + minask supp)',
        'markets': len(markets),
        'priced': priced,
        'floor': rows[0]['sum'] if rows else None,
        'brackets_minask': sum(1 for r in rows if r['sum'] < 1.0),
        'detector_opps': brackets,
        'band': len(band),
        'top8': rows[:8],
    }
    with open('runs/scan_latest.json', 'w') as f:
        json.dump(out, f, indent=1)
    with open('runs/scan_history.jsonl', 'a') as f:
        f.write(json.dumps(out) + '\n')
    print(json.dumps(out, indent=1))

asyncio.run(main())
