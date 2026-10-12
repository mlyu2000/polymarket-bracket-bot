import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    detector = BracketDetector()
    for m in markets:
        if 'LeBron James' in m.question:
            yes_book = await api.fetch_order_book(m.clob_token_ids[0])
            no_book = await api.fetch_order_book(m.clob_token_ids[1])
            # simulate detector steps
            print('market active', m.active, m.closed)
            print('liquidity', m.liquidity, 'min', Config.MIN_LIQUIDITY_USDC)
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            yes_price = float(yes_ask['price'])
            no_price = float(no_ask['price'])
            yes_vol = int(float(yes_ask['size']))
            no_vol = int(float(no_ask['size']))
            max_shares = min(yes_vol, no_vol)
            total_cost = yes_price + no_price
            gross_edge = 1.0 - total_cost
            net_edge = gross_edge - Config.FEE_BUFFER - Config.SLIPPAGE_BUFFER
            print('max_shares', max_shares)
            print('total_cost', total_cost)
            print('gross_edge', gross_edge)
            print('net_edge', net_edge)
            print('min profit', Config.MIN_PROFIT_MARGIN)
            print('max usdc', max_shares * total_cost, 'limit', Config.MAX_CAPITAL_PER_TRADE)
            break

asyncio.run(f())
