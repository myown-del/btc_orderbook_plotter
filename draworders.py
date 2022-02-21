#Made by tg: @billyel
import urllib.request
import json
import datetime
import time
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import socket

# US proxy
proxy = "login:password@ip:port"
socket.setdefaulttimeout(10)


class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"
    # TODO: check proxy func
    proxies = {'https': f"https://{proxy}"}


def min_max_OrderBookPrice(all_limits):
    return min([price[0] for price in all_limits]), max([price[0] for price in all_limits])


def getBitfinexOrders():
    response = linkopener.open(bitfinex_api)
    json_data = json.loads(response.read())
    json_data = json_data['bids'][:200:-1] + json_data['asks'][200:]
    limit_orders = []
    for x in json_data:
        limit_orders.append([int(x["price"]), float(x["amount"])])
    linkopener.close()
    return limit_orders


def getBitstampOrders(MaxPriceEdge):
    response = linkopener.open(bitstamp_api)
    json_data = json.loads(response.read())
    json_data = json_data['bids'][:200:-1] + json_data['asks'][200:]
    limit_orders = []
    for price in enumerate(json_data):
        if float(price[1][0]) > MaxPriceEdge:
            edge = price[0]
            break
    json_data = json_data[:edge]
    for x in json_data:
        all_limits.append([int(float(x[0])), float(x[1])])
    linkopener.close()
    return limit_orders


def getBtcPrice():
    response = linkopener.open(bitfinex_btc)
    json_data = json.loads(response.read())
    btc_price = int(float(json_data['mid']))
    linkopener.close()
    return btc_price


def cutLowVolume(matrix):
    max_volume = -1
    for x in matrix:
        for y in x:
            max_volume = max(max_volume, y)
    for x in enumerate(matrix):
        for volume in enumerate(x[1]):
            if volume[1] < max_volume*VOLUME_BARRIER:
                matrix[x[0]][volume[0]] = 0
    return matrix


def drawPlot(df):
    plt.clf()
    sns.heatmap(df, annot=False)
    ax = plt.gca()
    ax.set_xlim(0, df.shape[1])
    ax.set_ylim(0, df.shape[0])
    plt.plot(range(df.shape[1]), btc_priceline, linewidth=2,  color='#00FF00')
    plt.pause(TIMESTEP)

print("Made by tg: @billyel")
    
TIMESTEP = 5  # in seconds
DURATION = 60*60*12  # in seconds
VOLUME_BARRIER = 0

linkopener = AppURLopener()
bitfinex_api = "https://api.bitfinex.com/v1/book/BTCUSD?limit_bids=5000&limit_asks=5000&group=1"
bitfinex_btc = "https://api.bitfinex.com/v1/pubticker/BTCUSD"
bitstamp_api = "https://www.bitstamp.net/api/v2/order_book/btcusd"

matrix = []
timestamp_start = 0
btc_priceline = []
columns = []
rows = [price for price in range(0, 60000, 500)]

for i in range(int(DURATION/TIMESTEP)):
    temp_row = [0 for x in range(int(60000/500))]
    all_limits = []
    all_limits += getBitfinexOrders()
    all_limits += getBitstampOrders(59000)
    for x in all_limits:
        temp_price = x[0] - (x[0] % 500)
        temp_row[int(temp_price/500)] += x[1]*temp_price  # volume in usdt
    btc_price = getBtcPrice()
    btc_priceline.append(btc_price/500)
    if timestamp_start == 0:
        timestamp_start = int(time.time())
        matrix = temp_row
    else:
        matrix = np.column_stack((matrix, temp_row))
        matrix = cutLowVolume(matrix)
    print(datetime.datetime.utcfromtimestamp(timestamp_start+i))
    columns.append(datetime.datetime.utcfromtimestamp(timestamp_start+i).strftime('%Y-%m-%d %H:%M:%S'))
    df = pd.DataFrame(matrix, columns=columns, index=rows)
    drawPlot(df)

plt.show()
