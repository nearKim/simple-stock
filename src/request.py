from functools import partial

import requests
from src.constants import Twitter

__all__ = ["api_requests"]


class APIRequests:
    def __init__(self, token: str):
        self.token = token

    def build_header(self):
        header = {}
        if self.token:
            header["Authorization"] = f"Bearer {self.token}"
        return header

    def get(self, *args, **kwargs):
        header = self.build_header()

        if "header" in kwargs:
            header.update(kwargs.get("header"))

        get = partial(requests.get, headers=header)
        return get(*args, **kwargs)


api_requests = APIRequests(Twitter.Token.API_BEARER_TOKEN)
