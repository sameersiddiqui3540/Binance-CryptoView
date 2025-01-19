from datetime import date
import datetime
import os
from flask import Flask , render_template, request, flash, redirect, jsonify
from binance.client import Client
from binance.enums import *
from mongo_db_connector import get_api_credentials

mongo_uri = "mongodb://localhost:27017"
db_name = "SECRETS"
collection_name = "BINANCE_SECRET"

credentials = get_api_credentials(mongo_uri, db_name, collection_name)

app = Flask(__name__)
app.secret_key = b'somelongrandomstring'

API_KEY = credentials[0]['API_KEY']
API_SECRET = credentials[0]['API_SECRET']

# print(f"From Mongo, API_KEY: {API_KEY}, API_SECRET: {API_SECRET}")

client = Client(API_KEY, API_SECRET)

try:
    account_info = client.get_account()
    # print(f"Account info: \n{account_info}")
    print("----------- Account info retrieved successfully ----------")
except Exception as e:
    print(f"Error: {e}")

@app.route("/")
def index():
    title = "CryptoView"
    try:
        account = client.get_account()
        balances = account['balances']
        # print(f"count := {len(balances)}")
        balances = [{'asset':balance['asset'][2:] if balance['asset'][:2] == "LD" else balance['asset'] , 'free': balance['free']} for balance in balances if float(balance['free']) != 0.0]
        # print(f"count := {len(balances)}")
        # print(f"account: {account},\n balances: {balances}")
    except Exception as e:
        flash(f"An error occurred: {e}")
        balances = {'BTC': 0, 'ETH': 0}
    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']

    return render_template('index.html', title=title, my_balances=balances, symbols=symbols)

@app.route('/buy', methods=['POST'])
def buy():
    print(request.form)
    try:
        order = client.create_order(symbol=request.form['symbol'], 
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=request.form['quantity'])
    except Exception as e:
        flash(e.message, "error")

    return redirect('/')

@app.route('/sell', methods=['POST'])
def sell():
    print(request.form)
    try:
        order = client.create_order(symbol=request.form['symbol'], 
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=request.form['quantity'])
    except Exception as e:
        flash(e.message, "error")

    return redirect('/')

@app.route('/settings')
def settings():
    return 'settings'

@app.route('/history')
def history():
    candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Jan, 2024", "1 Jan, 2025")

    processed_candlesticks = []

    for data in candlesticks:
        candlestick = { 
            "time": data[0] / 1000, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)

if __name__=="__main__":
    app.run(debug=True)