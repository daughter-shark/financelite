# financelite
financelite is a lightweight stock information tool that takes every complicated features out.  
It only focuses on providing simple and intuitive, yet informative stock information.  

Currently, financelite is in a rapidly-evolving state. While I'll try to stay within the boundaries,
please understand your implementation may have to change in the future upgrades.

# Installation
`pip install financelite`

# Example Usage
### News
```python
from financelite import News
from financelite.exceptions import NoNewsFoundException

news = News()
try:
    news.get_news(ticker="gme", count=5)
    # returns 5 GME-related news
except NoNewsFoundException:
    # raised if there aren't any news associated with the ticker.
    pass
```
### Stock
```python
from financelite import Stock
from financelite.exceptions import DataRequestException

stock = Stock(ticker="gme")

try:
    stock.get_chart(interval="1d", range="5d")
    # returns statistics for 5 days, with 1 day interval

    stock.get_live()
    # returns GME's live price and currency
    
    stock.get_hist(data_range="1wk")
    # returns 1 week worth of closed price data
except DataRequestException:
    # raised if ticker, interval, or range values are wrong
    pass
except ValueError:
    # raised if get_hist's days is <= 1 or not int
    pass
```
### Group
```python
from financelite import Group, Stock
from financelite.exceptions import TickerNotInGroupException, DataRequestException, \
    ItemNotValidException

# You can add tickers to the group like this
group = Group()
group.add_ticker("gme")  # it takes in str value, then creates a Stock object with the ticker.
group.add_ticker("bb")
group.add_ticker("amc")

# or you can initialize the group with Stock objects
bb = Stock(ticker="bb")
gme = Stock(ticker="gme")
group = Group([bb, gme])

group.list_tickers()
# returns list of tickers represented as strings

try: 
    group.remove_ticker("ac.to")
except TickerNotInGroupException:
    # raised if ticker does not exist within the group
    pass

try:
    group.get_quotes(cherrypicks=["symbol", "shortName", "regularMarketPrice"])
    # returns a dictionary with only those keys
    
    group.get_quotes(cherrypicks=["symbol", "shortName", "regularMarketPrice"], exclude=True)
    # returns a dictionary with keys except these keys

except DataRequestException:
    # raised if the data request was not successful. Usually means invalid ticker.
    pass
except ItemNotValidException:
    # raised if any item in the cherrypicks list is invalidd
    pass
```


# Special Thanks
* [yahoo! finance](https://finance.yahoo.com/) for providing awesome websites and APIs.
* [Andrew Treadway](https://github.com/atreadw1492) for providing an open source package for processing finance data.