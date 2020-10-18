from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tweet:
    _id: int
    text: str
    user: dict
    retweeted_status: dict
    quoted_status: dict
    created_at: datetime

    @property
    def is_retweet(self):
        return bool(self.retweeted_status)

    @property
    def is_quote(self):
        return bool(self.quoted_status)
