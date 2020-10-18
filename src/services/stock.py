import typing

import yfinance as yf
from pandas import DataFrame
from src.constants import Stock


class StockService:
    def download_stock_dataframe(
        self,
        tickers: typing.List[Stock.Ticker],
        interval="1m",
        period="1mo",
        *,
        get_raw=False
    ) -> DataFrame:
        df = yf.download(tickers, interval=interval, period=period)
        if get_raw:
            return df

        return df.drop(["Open", "Low", "High", "Adj Close"], axis=1, level=1)

    # TODO
    # n_df = df.drop(['Open', 'Low', 'High', 'Adj Close'], axis=1, level=1)
    # n_df.columns.get_level_values(1)
    # n_df.iloc[:, n_df.columns.get_level_values(1)=='Close'].diff()
