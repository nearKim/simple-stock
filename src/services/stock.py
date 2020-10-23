import typing

import pandas as pd
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

    def preprocess_dataframe(self, multilevel_df: DataFrame) -> DataFrame:
        idx = pd.IndexSlice
        diff_df = (
            multilevel_df.loc[:, idx[:"Close"]]
            .rename(columns={"Close": "increased"})
            .diff()
            > 0
        )
        result_df = pd.concat([multilevel_df, diff_df], axis=1).sort_index(axis=1)

        return result_df
