import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=1000)
    # Find Timothee
    m = None
    for mk in markets:
        if 'Timothée Chalamet' in mk.question:
            m = mk
            break
    print('Market found', bool(m))
    if not m:
        return
    print(m.question)
    print('liquidity', m.liquidity)
    print('clob', m.clob_token_ids)
    yes_id, no_id = m.clob_token_ids
    yb = await api.fetch_order_book(yes_id)
    nb = await api.fetch_order_book(no_id)
    print('yes asks', len(yb.asks) if yb else 0)
    print('no asks', len(nb.asks) if nb else 0)
    if yb and nb:
        yes_min = min(float(a['price']) for a in yb.asks)
        no_min = min(float(a['price']) for a in nb.asks)
        print('yes_min', yes_min, 'no_min', no_min, 'sum', yes_min+no_min)
    opp = detector.detect(m, yb, nb)
    print('detector result', opp)
    if opp:
        print('opp yes', opp.yes_price, 'no', opp.no_price, 'sum', opp.total_cost, 'net', opp.net_edge)

asyncio.run(test())
