import alpaca_trade_api.rest
from alpaca_trade_api import REST
import random

api = REST(base_url="https://paper-api.alpaca.markets")


def buy_stock(stock_to_buy):
    try:
        print("Attempting to buy stock...")
        api.submit_order(stock_to_buy, qty=1)
        print(f'{stock_to_buy} successfully bought')
    except alpaca_trade_api.rest.APIError as e:
        if e.status_code == 403:
            print("Not enough money, selling oldest stock...")
            # Sell oldest
            positions = api.list_positions()
            if len(positions) == 0:
                print("Game over")
                exit()
            position_to_sell = positions[-1]
            print(f'Selling {position_to_sell.symbol}, to buy {stock_to_buy}')
            api.submit_order(position_to_sell.symbol, side="sell", qty=1)
            buy_stock(stock_to_buy)
        pass


def lambda_handler(event, context):
    max_stock_price = 100
    min_stock_price = 20

    # Pick the stock to buy
    print("Downloading all assets...")
    assets = api.list_assets(status="active")
    print("Filtering by only tradeable assets...")
    tradeable_assets = [asset for asset in assets if asset.tradable]
    symbols = [s.symbol for s in tradeable_assets]
    print("Getting market price for all assets...")
    snapshot = api.get_snapshots(symbols)
    print("Filtering by price range...")
    filtered_symbols = list(filter(lambda x: max_stock_price >= snapshot[x].latest_trade.p >= min_stock_price \
        if snapshot[x] and snapshot[x].latest_trade else False, snapshot))
    print("Picking random stock...")
    stock_to_buy = random.choice(filtered_symbols)
    # Try to buy, if not enough funds then sell the oldest stock in portfolio and try again.
    # If the entire portfolio is sold and still can't buy, game over.
    buy_stock(stock_to_buy)
    return 'Wasted money'
