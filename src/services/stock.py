import typing

import pandas as pd
import yfinance as yf
from pandas import DataFrame, IndexSlice
from pandas._libs.tslibs.timestamps import Timestamp

from src.constants import Stock
from src.dto import Tweet
from src.utils import make_tz_unaware_df

__all__ = ["stock_service"]


class StockService:
    def download_stock_dataframe(
        self,
        tickers: typing.List[Stock.Ticker],
        interval="1m",
        period="1wk",
        *,
        get_raw=False
    ) -> DataFrame:
        df = yf.download(tickers, interval=interval, period=period, group_by="ticker")
        if get_raw:
            return df

        return df.drop(["Open", "Low", "High", "Adj Close"], axis=1, level=1)

    def __add_increased_column(self, multilevel_df: DataFrame) -> DataFrame:

        diff_df = (
            multilevel_df.loc[:, IndexSlice[:, "Close"]]
            .rename(columns={"Close": "increased"})
            .diff()
            > 0
        )
        result_df = pd.concat([multilevel_df, diff_df], axis=1).sort_index(axis=1)
        return result_df

    def __add_initial_columns(self, multilevel_df: DataFrame) -> DataFrame:
        first_columns = multilevel_df.columns.get_level_values(0).unique()
        for column in first_columns:
            multilevel_df[column, "tweeted"] = False
            multilevel_df[column, "transaction"] = None
        result_df = multilevel_df.sort_index(axis=1)
        return result_df

    def preprocess_dataframe(self, multilevel_df: DataFrame) -> DataFrame:
        result_df = make_tz_unaware_df(multilevel_df)
        result_df = self.__add_increased_column(result_df)
        result_df = self.__add_initial_columns(result_df)
        return result_df

    def mark_tweeted(
        self, tweet_list: typing.List[Tweet], target_df: DataFrame
    ) -> DataFrame:
        for tweet in tweet_list:
            tweet_time = tweet.created_at.replace(second=0)
            filtered_df = target_df[target_df.index >= tweet_time]

            if filtered_df.empty:
                continue
            idx: Timestamp = filtered_df.iloc[0].name
            target_df.at[idx, IndexSlice["tweeted", :]] = True

        return target_df

    def process_dataframe(self, df: DataFrame, tickers: list, *, x, y, z) -> DataFrame:
        if not tickers:
            tickers = ["SQQQ", "TQQQ"]

        reset_df = df.reset_index()
        tweeted_datetime_index_list = reset_df[reset_df["tweeted"] is True].index

        for i, idx in enumerate(tweeted_datetime_index_list):
            filtered_df = reset_df.iloc[idx : idx + x]
            # TODO: 여기부터
            next_idx = tweeted_datetime_index_list[i+1]

            for ticker in tickers:
                frac: DataFrame = getattr(filtered_df, ticker)
                inc_cnt = frac["increased"].sum()
                is_long = inc_cnt >= y
                frac.at[idx + x, "transaction"] = True


stock_service = StockService()
