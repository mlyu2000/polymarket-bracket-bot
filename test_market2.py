import httpx
url = "https://gamma-api.polymarket.com/markets?limit=1&offset=1&active=true&closed=false&order=volume&ascending=false"
resp = httpx.get(url, timeout=10)
m = resp.json()[0]
print(m['question'])
print(m['outcomes'])
print(m['outcomePrices'])
print(m['clobTokenIds'])
