import datetime
import logging

from pandas import DataFrame
from src.constants import INITIAL_MONEY, TRANSACTION_BATCH, Stock, Twitter
from src.services.stock import stock_service
from src.services.twitter import tweeter_service


def calculate(x: int, y: int, z: int, multilevel_df: DataFrame, ticker: str):
    logging.info(f"Start `calculate`...\nx: {x}, y: {y}, z: {z}, ticker: {ticker}\n")

    if x < y:
        raise ValueError("x는 y보다 항상 커야 합니다.")
    if not ticker:
        raise ValueError("ticker를 입력하세요.")

    money = INITIAL_MONEY
    batch = TRANSACTION_BATCH
    stocks = 0

    processed_multilevel_df = stock_service.process_dataframe(
        multilevel_df, ticker, x=x, y=y, z=z
    )
    processed_df = processed_multilevel_df[ticker]
    calc_df = processed_df[~processed_df["transaction"].isnull()]
    transactions_count: int = calc_df.shape[0]

    for _, row in calc_df.iterrows():
        price, is_long = row["Close"], row["transaction"]

        if is_long:
            transaction_amount = money if money < batch else batch
            long_count, remainder = divmod(transaction_amount, price)
            stocks += long_count
            money = money - transaction_amount + remainder
        else:
            money += price * stocks
            stocks = 0

    leftover: float = stock_service.cleanup(processed_df, stocks)

    logging.info(
        f"Result:\n"
        f"x:{x}, y:{y}, z:{z}, ticker:{ticker} -> "
        f"거래횟수:{transactions_count}, "
        f"보유량:{stocks}, "
        f"처리 전 금액: {money}, "
        f"잔금: {leftover}, \n"
        f"처리 후 금액: {money + leftover}\n"
        f"End `calculate`...\n"
    )
    return money + leftover


def get_dataframe(screen_name, tickers: list):
    df = stock_service.download_stock_dataframe(tickers)
    df = stock_service.preprocess_dataframe(df)

    if screen_name == Twitter.ScreenName.TRUMP:
        tweet_list = tweeter_service.get_trump_tweet_objects()
    else:
        tweet_list = tweeter_service.get_biden_tweet_objects()
    try:
        tweeter_service.validate_period(tweet_list)
    except ValueError:
        # TODO
        pass
    result_df = stock_service.mark_tweeted(tweet_list, df)
    return result_df


if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    logging.basicConfig(filename=f"calculation_log-{now}.log", level=logging.DEBUG)
    tickers = [Stock.Ticker.UDOW, Stock.Ticker.UPRO, Stock.Ticker.TQQQ]

    trump_df = get_dataframe(Twitter.ScreenName.TRUMP, tickers)
    biden_df = get_dataframe(Twitter.ScreenName.BIDEN, tickers)

    calculate(5, 3, 1, trump_df, "TQQQ")
