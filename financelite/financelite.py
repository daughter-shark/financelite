import feedparser
from requests import get
from exceptions import *

NEWS_BASE_URL = "https://feeds.finance.yahoo.com/rss/2.0/headline"
CHART_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"


class News:
    def __init__(self, region: str = "US", lang: str = "en-US"):
        self.region = region
        self.lang = lang

    def get_news(self, ticker: str, count: int = 10) -> list:
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

    def get_data(self, interval: str, range: str) -> dict:
        """
        valid for interval and range : ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"]
        :param interval: how granular the data is.
        :param range: how much data is pulled.
        :return: dictionary of the chart
        """
        url = CHART_BASE_URL + f"/{self.ticker}?interval={interval}&range={range}"
        request = get(url)
        content = request.json()
        chart = content.get("chart")
        if chart.get("error"):
            raise DataRequestException(chart.get("error").get("description"))
        return chart

    def get_live(self) -> tuple:
        """
        :return: tuple of live price in float, and currency as str
        """
        data = self.get_data(interval="1d", range="1d")
        result = data.get("result").pop()
        meta = result.get("meta")
        live = meta.get("regularMarketPrice")
        currency = meta.get("currency")
        return live, currency

