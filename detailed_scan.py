import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def detailed_scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=200)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    results = []
    for m, (y,n) in zip(markets, books):
        if not y or not n:
            continue
        # Use detector logic
        if not y.asks or not n.asks:
            continue
        yes_ask = min(y.asks, key=lambda a: float(a["price"]))
        no_ask = min(n.asks, key=lambda a: float(a["price"]))
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        total = yes_price + no_price
        if total <= 1.005:
            opp = detector.detect(m, y, n)
            results.append({
                'q': m.question[:80],
                'total': total,
                'yes_price': yes_price,
                'no_price': no_price,
                'liq': m.liquidity,
                'opp_found': opp is not None,
                'yes_vol': float(yes_ask['size']),
                'no_vol': float(no_ask['size'])
            })
    results.sort(key=lambda x: x['total'])
    for r in results[:30]:
        print(f"{r['total']:.4f} opp={r['opp_found']} vol {r['yes_vol']:.1f}/{r['no_vol']:.1f} liq {r['liq']:.0f} {r['q']}")

asyncio.run(detailed_scan())
