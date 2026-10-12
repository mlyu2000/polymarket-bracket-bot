import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    opps = []
    for m, (yes, no) in zip(markets, all_books):
        opp = detector.detect(m, yes, no)
        if opp:
            opps.append(opp)
    print('detected', len(opps))
    for o in opps[:10]:
        print(o.market.question[:60], o.yes_price, o.no_price, o.total_cost, o.net_edge, o.max_shares)

asyncio.run(scan())
