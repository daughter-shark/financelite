# financelite
financelite is a lightweight stock information tool that takes every complicated features out.  
It only focuses on providing simple and intuitive, yet informative stock information.  

Currently, financelite is in a rapidly-evolving state. While I'll try to stay within the boundaries,
please understand your implementation may have to change in the future upgrades.

# Installation
`pip install financelite`

# Example Usage

```python
from financelite import News, Stock
from financelite.exceptions import NoNewsFoundException, DataRequestException

news = News()
try:
    news.get_news(ticker="gme", count=5)
except NoNewsFoundException:
    # handle exception
    pass
# returns 5 GME-related news

stock = Stock(ticker="gme")
try:
    stock.get_live()
    # returns GME's live price and currency
    
    stock.get_data(interval="1d", range="5d")
    # returns statistics for 5 days, with 1 day interval
except DataRequestException:
    # handle exception
    pass
```

# Special Thanks
* [yahoo! finance](https://finance.yahoo.com/) for providing awesome websites and APIs.
* [Andrew Treadway](https://github.com/atreadw1492) for providing an open source package for processing finance data.