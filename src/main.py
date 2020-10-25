import datetime
import logging

from pandas import DataFrame

from src.constants import Twitter
from src.services.stock import stock_service
from src.services.twitter import tweeter_service


def calculate(x: int, y: int, z: int, df: DataFrame):
    if x < y:
        raise ValueError("x는 y보다 항상 커야 합니다.")

    reset_df = df.reset_index()
    tweeted_datetime_index_list = reset_df[reset_df['tweeted'] == True].index

    for idx in tweeted_datetime_index_list:
        filtered_df = reset_df.iloc[idx: idx+x]
        for ticker in TICKERS:
            frac: DataFrame = getattr(filtered_df, ticker)
            inc_cnt = frac['increased'].sum()
            is_long = inc_cnt >= y
            frac.at[idx +x, 'transaction'] = True







def get_dataframe(screen_name):
    df = stock_service.download_stock_dataframe(['SQQQ', 'TQQQ'])
    df = stock_service.preprocess_dataframe(df)

    if screen_name == Twitter.ScreenName.TRUMP:
        tweet_list = tweeter_service.get_trump_tweet_objects()
    else:
        tweet_list = tweeter_service.get_biden_tweet_objects()

    tweeter_service.validate_period(tweet_list)
    result_df = stock_service.mark_tweeted(tweet_list, df)
    return result_df

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    logging.basicConfig(filename=f"calculation_log-{now}.log", level=logging.DEBUG)

    trump_df = get_dataframe(Twitter.ScreenName.TRUMP)
    biden_df = get_dataframe(Twitter.ScreenName.BIDEN)

