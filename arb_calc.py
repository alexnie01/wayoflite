import numpy as np
import pandas as pd

store = pd.HDFStore("config.h5")
exchanges = ['GDAX', 'Binance', 'Poloniex', 'CoinExchange', 'BitGrail']
field_list = ['withdraw_fees', 'market_fees', 'US_based']
fields = {}
coins = ['BTC', 'LTC', 'ETH']

def write_fields(fields = fields, store=store):
    for field in fields:
        store[field] = fields[field]

first = input("First time? [Y/n]: ")
if first == "Y":
    fields['withdraw_fees'] = pd.DataFrame(
                    {'GDAX': {'BTC': 0,
                              'LTC': 0,
                              'ETH': 0},
                     'Binance': {'BTC': .001,
                                 'LTC': .01,
                                 'ETH': .01},
                     'CoinExchange': {'BTC': .001,
                                  'LTC': .01,
                                  'ETH': .01},
                     'Poloniex': {'BTC': .0001,
                                      'LTC': .01,
                                      'ETH': .01},
                     'BitGrail': {'BTC': .0012,
                                  'LTC': .01,
                                  'ETH': .01}})
    fields['market_fees'] = pd.DataFrame({'GDAX': {'maker': 0, 'taker': .003},
                               'Binance': {'maker': .0005, 'taker': .0005},
                               'Poloniex': {'maker': .0015, 'taker': .0025},
                               'CoinExchange': {'maker': .002, 'taker': .002},
                               'BitGrail': {'maker': .002, 'taker': .002}})
    fields['US_based'] = pd.Series({'GDAX': True, 
                          'Binance': False, 
                          'CoinExchange': False, 
                          'Poloniex': True,
                          'BitGrail': False})
    write_fields(fields, store)
else:
    for field in field_list:
        fields[field] = store[field]
    
temp = """ To be updated later
update = input("Market fee updates? [Y/n]: ")

while update == 'Y':
    mkt = input("Which market?\n{}".format(exchanges))
    while mkt not in exchanges:
        mkt = input("Exchange not found. Try again\n{}".format(exchanges))
    field = input("Which field?\n{}".format(field_list))
    while field not in field_list:
        field = input("Field not found. Try again\n{}".format(field_list))
    to_mod = store[field]
    if field == "withdraw_fees":
        coin = input("Which coin?\n{}".format(coins))
        while coin not in coins:
            coin = input("Coin not found. Try again\n{}".format(coins))
        to_mod[mkt].loc[coin]
        val = input("{} for {} in {} has value {}. New value: ".format(coin, mkt, field, to_mod[mkt].loc[coin]))
        try:
            to_mod[mkt].loc[coin] = float(val)
        except:
            print("Failed to write to file. Exiting")
    elif field == "market_fees":
        side = input("Which side?\n{}".format(['maker', 'taker']))
        while side not in ['maker', 'taker']:
            side = input("Invalid input. Try again.")
        val = input("{} for {} in {} has value {}. New value: ".format(side, mkt, field, to_mod[mkt].loc[side]))
        to_mod[mkt].loc[side] = float(val)
    elif field == "US_based":
        val = input("{} current US-based is set to {}. New value: ".format(mkt, to_mod.loc[mkt]))
        to_mod.loc[mkt] = bool(val)
    update = input("Any other updates? [Y/n]: ")
"""

# slippage: amount price of LTC might slip while transferring to GDAX
def simple_arb(slippage = .00005):
    """simple LTC/BTC between CoinExchange and GDAX/Binance. Assumes LTC is cheaper on CoinExchange"""
    print("Assuming slippage of {}".format(slippage))
    running = True
    exchs = ['GDAX', 'Binance']
    ratios = {}
    btc = {}
    while running:
        amt = float(input("input amount of BTC: "))
        coinex_r = float(input("input CoinExchange LTC/BTC ratio: "))
        # compute amount of LTC we send out
        ltc_coinex = (amt/coinex_r*(1.-store['market_fees']['CoinExchange']['maker']) - store['withdraw_fees']['CoinExchange']['LTC'])
        right_exch = None
        right_exch_amt = amt
        # figure out how much btc we would get after sending back to CoinExchange for each exchange
        for exch in exchs:
            ratios[exch] = float(input("input {} LTC/BTC ratio: ".format(exch))) - slippage
            btc[exch] = (ltc_coinex*ratios[exch]*(1.-store['market_fees'][exch]['taker'])-
                         store['withdraw_fees'][exch]['BTC'])
            # Find max return exchange. Want at least 1% returns or else too risky
            if btc[exch] > 1.01*amt and btc[exch] > right_exch_amt: 
                right_exch = exch
                right_exch_amt = btc[exch]
        if right_exch:
            print("Start: {0:.5f} BTC".format(amt))
            print("Buy {} LTC on CoinExchange at {}".format(ltc_coinex, coinex_r))
            print("Transfer to {} and sell at {} for {} BTC".format(right_exch, ratios[right_exch], right_exch_amt))
            print("Returns: {0:.2f}%".format(100*(right_exch_amt-amt)/amt))
        else:
            print("No arbitrage found with greater than 1% returns.")
        quit = input("quit? [Y/n]")
        if quit == "Y":
            running = False

if __name__ == "__main__":
    simple_arb()
    store.close()
