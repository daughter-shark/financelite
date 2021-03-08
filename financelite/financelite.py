"""
Please refer to the documentation provided in the README.md,
which can be found at financelite's PyPI URL: https://pypi.org/project/financelite/
"""
from typing import List
from requests import get
import feedparser
from financelite.exceptions import NoNewsFoundException, ItemNotValidException, \
    TickerNotInGroupException, DataRequestException


NEWS_BASE_URL = "https://feeds.finance.yahoo.com/rss/2.0/headline"
CHART_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
QUOTE_BASE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
VALID_TIME = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
ACCEPTABLE_ITEMS = [
    'language', 'region', 'quoteType', 'quoteSourceName', 'triggerable', 'currency', 'marketState',
    'tradeable', 'fiftyTwoWeekRange', 'fiftyTwoWeekHighChange', 'fiftyTwoWeekHighChangePercent',
    'fiftyTwoWeekLow', 'fiftyTwoWeekHigh', 'earningsTimestamp', 'earningsTimestampStart',
    'earningsTimestampEnd', 'trailingAnnualDividendRate', 'trailingAnnualDividendYield',
    'epsTrailingTwelveMonths', 'epsForward', 'epsCurrentYear', 'priceEpsCurrentYear',
    'sharesOutstanding', 'bookValue', 'fiftyDayAverage', 'fiftyDayAverageChange',
    'fiftyDayAverageChangePercent', 'twoHundredDayAverage', 'twoHundredDayAverageChange',
    'twoHundredDayAverageChangePercent', 'marketCap', 'forwardPE', 'priceToBook', 'sourceInterval',
    'exchangeDataDelayedBy', 'exchange', 'shortName', 'longName', 'messageBoardId',
    'exchangeTimezoneName', 'exchangeTimezoneShortName', 'gmtOffSetMilliseconds', 'market',
    'esgPopulated', 'priceHint', 'postMarketChangePercent', 'postMarketTime', 'postMarketPrice',
    'postMarketChange', 'regularMarketChange', 'regularMarketChangePercent', 'regularMarketTime',
    'regularMarketPrice', 'regularMarketDayHigh', 'regularMarketDayRange', 'regularMarketDayLow',
    'regularMarketVolume', 'regularMarketPreviousClose', 'bid', 'ask', 'bidSize', 'askSize',
    'fullExchangeName', 'financialCurrency', 'regularMarketOpen', 'averageDailyVolume3Month',
    'averageDailyVolume10Day', 'fiftyTwoWeekLowChange', 'fiftyTwoWeekLowChangePercent',
    'dividendDate', 'firstTradeDateMilliseconds', 'displayName', 'symbol'
]


def _fetch(url: str) -> dict:
    """
    :param url: url to request and fetch from
    :return: json dict of results
    """
    request = get(url)
    return request.json()


def _cherry_pick(json: dict, cherries: List[str], exclude: bool = False) -> dict:
    """
    :param json: json dict to process
    :param cherries: items to cherry-pick (or not to cherry-pick)
    :param exclude: if exclude == True, it excludes the items and get everything else
    :return:
    """
    picked = {}
    for c in cherries:
        if c not in ACCEPTABLE_ITEMS:
            raise ItemNotValidException

    if exclude:
        for key, value in json.items():
            if key not in cherries:
                picked[key] = value
    else:
        for key, value in json.items():
            if key in cherries:
                picked[key] = value
    return picked


class News:
    def __init__(self, region: str = "US", lang: str = "en-US"):
        self.region = region
        self.lang = lang

    def get_news(self, ticker: str, count: int = 10) -> List[dict]:
        """
        :param ticker: string value for ticker(symbol)
        :param count: count of returned news items
        :return: list of news items
        """
        url = NEWS_BASE_URL + f"?region={self.region}&lang={self.lang}&s={ticker}&count={count}"
        parsed = feedparser.parse(url)
        news = parsed.get("entries")
        if not news:
            raise NoNewsFoundException
        return news


class Stock:
    def __init__(self, ticker: str):
        self.ticker = ticker

    def __str__(self):
        return f"{self.ticker}"

    def get_chart(self, interval: str, range: str) -> dict:
        """
        valid for interval and range :
        ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"]
        :param interval: how granular the data is.
        :param range: how much data is pulled.
        :return: dictionary of the chart
        """
        url = CHART_BASE_URL + f"/{self.ticker}?interval={interval}&range={range}"
        content = _fetch(url)
        chart = content.get("chart")
        if chart.get("error"):
            raise DataRequestException(chart.get("error").get("description"))
        if range not in VALID_TIME:
            raise DataRequestException(f"Invalid range: {range}")
        return chart

    def get_live(self) -> tuple:
        """
        :return: tuple of live price in float, and currency as str
        """
        data = self.get_chart(interval="1d", range="1d")
        result = data.get("result").pop()
        meta = result.get("meta")
        live = meta.get("regularMarketPrice")
        currency = meta.get("currency")
        return live, currency


class Group:
    def __init__(self, tickers: List[str] = None):
        self.tickers = tickers if tickers else []

    def add_ticker(self, ticker: str):
        """
        :param ticker: string value of ticker symbol
        """
        self.tickers.append(ticker)

    def remove_ticker(self, ticker: str):
        """
        :param ticker: string value of ticker symbol
        """
        removed = False
        for t in self.tickers:
            if t == ticker:
                self.tickers.remove(t)
                removed = True
                break
        if not removed:
            raise TickerNotInGroupException

    def get_quotes(self, cherrypicks: List[str] = None, exclude: bool = False) -> List[dict]:
        """

        :param cherrypicks: data you want
        :param exclude: does the opposite. data you don't want
        :return: dictionary consists of only the wanted data
        """
        formatted = ""
        for t in self.tickers:
            formatted += t
            if t != self.tickers[-1]:
                formatted += ","
        url = QUOTE_BASE_URL + f"?symbols={formatted}"
        content = _fetch(url)
        quote_resp = content.get("quoteResponse")
        quotes = quote_resp.get("result")
        if len(quotes) != len(self.tickers):
            raise DataRequestException("Invalid tickers")
        if quote_resp.get("error"):
            raise DataRequestException(quotes.get("error").get("description"))
        if cherrypicks:
            for i, q in enumerate(quotes):
                quotes[i] = _cherry_pick(q, cherries=cherrypicks, exclude=exclude)
        return quotes
