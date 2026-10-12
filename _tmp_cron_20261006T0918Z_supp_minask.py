import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

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

    priced = 0
    top = []
    brackets = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = round(yp + np_, 6)
            priced += 1
            if total < 1.00:
                brackets += 1
            top.append({'sum': total, 'q': m.question[:60], 'yes': yp, 'no': np_, 'liq': m.liquidity})
    top.sort(key=lambda d: d['sum'])
    return {'markets': len(markets), 'priced': priced, 'brackets': brackets,
            'floor': top[0]['sum'] if top else None, 'top': top[:6], 'scan_time': scan_time}

r = asyncio.run(scan())
print(f"[minask] markets={r['markets']} priced={r['priced']} brackets(min-ask sum<1.00)={r['brackets']} floor={r['floor']} ({r['scan_time']:.1f}s)")
for t in r['top']:
    print(f"  {t['sum']:.4f} | Yes@{t['yes']:.3f} No@{t['no']:.3f} | liq={t['liq']} | {t['q']}")
