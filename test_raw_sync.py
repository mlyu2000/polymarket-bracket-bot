import httpx

url = "https://gamma-api.polymarket.com/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
resp = httpx.get(url, timeout=10)
data = resp.json()
m = data[0]
print('question', m.get('question'))
print('outcomes', m.get('outcomes'))
print('outcomePrices', m.get('outcomePrices'))
print('clobTokenIds', m.get('clobTokenIds'))
print('conditionId', m.get('conditionId'))
