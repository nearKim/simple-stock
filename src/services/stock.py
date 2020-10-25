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
        get_raw=False,
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
            multilevel_df[column, "transaction"] = None
        multilevel_df["tweeted"] = False
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

    def mark_first_transaction(
        self,
        multilevel_df: DataFrame,
        tweet_idx: int,
        ticker: str,
        x: int,
        *,
        is_increasing: bool,
    ) -> typing.NoReturn:
        """
        트윗 후 첫번째 거래: 상승중이면 매수하고, 하락중이면 매도한다.
        """
        multilevel_df.at[
            tweet_idx + x, IndexSlice[ticker, "transaction"]
        ] = is_increasing

    def mark_second_transaction(
        self,
        multilevel_df: DataFrame,
        tweet_idx: int,
        ticker: str,
        x: int,
        z: int,
        *,
        is_increasing: bool,
        timeout: int = 60,
    ) -> typing.NoReturn:
        """
        트윗 후 두번째 거래: 상승하여 첫번째 거래에서 매수했으면 매도하고, 하락하여 매도했으면 매수한다.
        z번 연속으로 하락 또는 상승이 있는 경우에만 거래한다. 그 외 Hold한다.
        """
        check_start_idx, i = tweet_idx + x, 0
        flags = [False] * z

        # 첫번째 거래에서 하락하여 매수했으면 두번째 거래는 상승을 탐지하여 매수해야 한다.
        should_long = check_increasing = not is_increasing

        # timeout(분) 동안만 탐지한다.
        while check_start_idx < timeout:
            check_start_idx += 1
            is_increased = multilevel_df.at[
                check_start_idx, IndexSlice[ticker, "increased"]
            ]

            if is_increased == check_increasing:
                flags[i] = True
                i += 1
            else:
                flags = [False] * z

            if all(flags):
                multilevel_df.at[
                    check_start_idx + 1, IndexSlice[ticker, "transaction"]
                ] = should_long
                break

    def process_dataframe(
        self, multilevel_df: DataFrame, ticker, *, x, y, z
    ) -> DataFrame:
        reset_multilevel_df = multilevel_df.reset_index()
        tweeted_datetime_index_list: typing.List[int] = reset_multilevel_df[
            reset_multilevel_df["tweeted"]
        ].index

        for tweet_idx, next_idx in zip(
            tweeted_datetime_index_list, tweeted_datetime_index_list[1:]
        ):
            filtered_df = reset_multilevel_df.iloc[tweet_idx : tweet_idx + x]

            frac: DataFrame = filtered_df[ticker]
            inc_cnt = frac["increased"].sum()
            is_increasing: bool = inc_cnt >= y

            self.mark_first_transaction(
                reset_multilevel_df, tweet_idx, ticker, x, is_increasing=is_increasing
            )
            self.mark_second_transaction(
                reset_multilevel_df,
                tweet_idx,
                ticker,
                x,
                z,
                is_increasing=is_increasing,
                timeout=next_idx,
            )
        return reset_multilevel_df

    def cleanup(self, df: DataFrame, quantity) -> float:
        price = df.tail(1).reset_index().at[0, "Close"]
        return price * quantity


stock_service = StockService()
