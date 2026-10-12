import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    print('markets count', len(markets))
    # Print first few
    for i,m in enumerate(markets[:5]):
        print(i, m.question[:60], m.liquidity, m.clob_token_ids)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    # Find any with asks
    count_valid = 0
    for m, (yes, no) in zip(markets, all_books):
        if yes and no and yes.asks and no.asks:
            count_valid +=1
            # compute best asks
            yes_ask = min(yes.asks, key=lambda a: float(a['price']))
            no_ask = min(no.asks, key=lambda a: float(a['price']))
            total = float(yes_ask['price'])+float(no_ask['price'])
            if total <= 1.005:
                print('near', total, m.question[:60])
    print('valid books', count_valid)

asyncio.run(scan())
