import requests
import pandas as pd
import datetime
import json

from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier

def read_contracts():
    try:
        f = open("input.txt", "r")
        # extract contract values from key
        contracts = f.readline().split('=')[-1]

        # separate contracts
        return contracts.split(',')
    except:
        return None

def create_df_contract(contract):
    # extract 1 week of candle sample data from last week till the start of today
    ticks = 24 * 7 + 1
    hours_today = datetime.datetime.now().hour
    samples = ticks + hours_today

    # api call to get hourly samples
    url = "https://api.huobi.pro/market/history/kline"
    params = {'symbol': contract, 'period': '60min', 'size': samples}

    r = requests.get(url, params)
    result = r.json()

    # error checking
    status_code = result.get("status")
    if status_code != 'ok':
        print("Contract:" + contract + " Error code:" + result.get('err-code') + " Error message:" + result.get('err-msg'))
        return None

    # save results into a dataframe
    df_temp = pd.DataFrame(result['data'])

    # extract the UNIX timestamp along with the closing amount for the past week until the start of today
    df_temp = df_temp.loc[hours_today:samples, ['id', 'close']]

    # reorder by timestamp and rename columns
    df_temp = df_temp.iloc[::-1]
    df_temp = df_temp.rename(columns={'id': 'UNIX timestamp', 'close': contract})

    return df_temp

def calculate_mean_variance(portfolio):
    # mean variance calculation
    mu = mean_historical_return(portfolio)
    sigma = CovarianceShrinkage(portfolio).ledoit_wolf()

    ef = EfficientFrontier(mu, sigma)

    try:
        weights = ef.max_sharpe()
    except:
        # max_sharpe failed due to all assets being lower than the risk-free rate
        weights = ef.min_volatility()

    cleaned_weights = ef.clean_weights()

    # output calculations to console and text file
    dictionary = dict(cleaned_weights)
    print(dictionary)
    with open('output.txt', 'w') as file:
        file.write(json.dumps(dictionary))

# entry point to program
if __name__ == '__main__':
    contracts = ['btcusdt', 'ltcusdt', 'ethusdt']

    # read contracts from input file if provided
    file_contracts = read_contracts()
    if(file_contracts is not None):
        contracts = file_contracts

    combined_df = None

    #extract data for all contracts
    for contract in contracts:
        current_df = create_df_contract(contract)

        # merge contract dataframe
        if(current_df is not None):
            if combined_df is None:
                combined_df = current_df
            else:
                combined_df = pd.merge(combined_df, current_df)

    if combined_df is not None:
        # remove timestamp before mean variance calculation
        portfolio = combined_df.drop('UNIX timestamp', axis=1)

        calculate_mean_variance(portfolio)
    else:
        print("No contract data")
