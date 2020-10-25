import typing
from datetime import timedelta

from furl import furl
from src.constants import Twitter
from src.dto import Tweet
from src.request import api_requests
from src.utils import convert_utc_to_usa_dt

__all__ = ["tweeter_service"]


class TwitterService:
    def get_timeline_api_url(self, screen_name, since_id=None, count=200) -> str:
        f_url: furl = furl(Twitter.API.TIMELINE_API_URL)

        if not screen_name:
            raise ValueError("screen_name이 제공되지 않았습니다.")

        f_url.add({"screen_name": screen_name})
        f_url.add({"count": count})

        if since_id:
            f_url.add({"since_id": since_id})
        return f_url.url

    def get_timeline_api_result(
        self, screen_name, since_id=None, count=200
    ) -> typing.List[dict]:
        url = self.get_timeline_api_url(screen_name, since_id, count)
        response = api_requests.get(url)
        response_list = response.json()
        return response_list

    def get_timeline_tweet_objects(
        self, screen_name, since_id=None, count=200
    ) -> typing.List[Tweet]:
        response_list = self.get_timeline_api_result(screen_name, since_id, count)
        objects = []
        if not response_list:
            return objects

        for r in response_list:
            _id = r.get("id")
            text = r.get("text")
            user = r.get("user")
            retweeted_status = r.get("retweeted_status")
            quoted_status = r.get("quoted_status")
            created_at = convert_utc_to_usa_dt(r.get("created_at"))

            dto = Tweet(
                _id=_id,
                text=text,
                user=user,
                retweeted_status=retweeted_status,
                quoted_status=quoted_status,
                created_at=created_at,
            )
            objects.append(dto)
        return objects

    def exclude_rt_tweets(
        self, tweet_objects: typing.List[Tweet]
    ) -> typing.List[Tweet]:
        return [
            tweet for tweet in tweet_objects if not (tweet.is_retweet or tweet.is_quote)
        ]

    def validate_period(self, tweet_object_list: typing.List[Tweet]) -> typing.NoReturn:
        min_dt = max_dt = None
        for tweet in tweet_object_list:
            created_at = tweet.created_at

            if not min_dt or not max_dt:
                min_dt = max_dt = created_at
                continue
            if min_dt > created_at:
                min_dt = created_at
            if max_dt < created_at:
                max_dt = created_at
        delta = max_dt - min_dt

        if delta > timedelta(days=7):
            raise ValueError('1wk보다 큰 범위가 필요합니다.')

    def get_trump_tweet_objects(self, *, exclude_rt=True) -> typing.List[Tweet]:
        objects = self.get_timeline_tweet_objects(Twitter.ScreenName.TRUMP)
        if exclude_rt:
            objects = self.exclude_rt_tweets(objects)
        return objects

    def get_biden_tweet_objects(self, *, exclude_rt=True) -> typing.List[Tweet]:
        objects = self.get_timeline_tweet_objects(Twitter.ScreenName.BIDEN)
        if exclude_rt:
            objects = self.exclude_rt_tweets(objects)
        return objects


tweeter_service = TwitterService()
