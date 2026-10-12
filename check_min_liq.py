import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging = __import__('logging')
logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    markets = await api.fetch_active_markets(limit=200)
    print(f"Fetched {len(markets)} markets")
    if markets:
        print("Min liquidity:", min(m.liquidity for m in markets))
        print("Max liquidity:", max(m.liquidity for m in markets))
        below = sum(1 for m in markets if m.liquidity < Config.MIN_LIQUIDITY_USDC)
        print(f"Below MIN_LIQUIDITY_USDC ({Config.MIN_LIQUIDITY_USDC}): {below}")

asyncio.run(scan())
