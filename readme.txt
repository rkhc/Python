#Introduction
This python script computes the mean-variance optimization for a given list of contracts from one week ago until the start of today.

Data is retrieved from https://open.huobigroup.com/

Trading symbol for BTC, ETH and LTC will be in USD to standardize their currency

Candle sampling is in one hour intervals using Singapore Time GMT+8

Run using Python 3.9

#Configurations
-input.txt has a list of contract trading symbols. Add a comma followed by the contract trading symbol in the file for it to be read properly

-output.txt is the output location for the mean-variance computation

-requirements.txt are the dependencies used for this script

#References
https://builtin.com/data-science/portfolio-optimization-python
https://pyportfolioopt.readthedocs.io/en/latest/UserGuide.html
