import requests
from datetime import datetime
import time
import json


def get_market_price(timespan, start):
    _url = 'https://api.blockchain.info/charts/market-price'
    params = {
        'timespan': timespan,
        'start': start
    }
    response = requests.get(url=_url, params=params)
    return response.json()

def get_hashrate(timespan, start):
    _url = 'https://api.blockchain.info/charts/hash-rate'
    params = {
        'timespan': timespan,
        'start': start
    }
    response = requests.get(url=_url, params=params)
    return response.json()

start_date = datetime.strptime('2019-01-01', '%Y-%m-%d')
dates_timespan = [str(start_date.date())]

for i in range(1, 7):
    date = start_date
    date = date.replace(year=date.year+i, day=date.day+i)
    dates_timespan.append(str(date.date()))

hashrate_json = []
market_price_json = []

for date in dates_timespan:
    hashrate_data = get_hashrate(timespan='1year', start=date)
    hashrate_json += hashrate_data['values']
    time.sleep(1)

    market_price_data = get_market_price(timespan='1year', start=date)
    market_price_json += market_price_data['values']
    time.sleep(1)

with open('hashrate.json', 'w') as f:
    json.dump(hashrate_json, f, indent=4)
with open('market_price.json', 'w') as f:
    json.dump(market_price_json, f, indent=4)