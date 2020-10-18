import json


def get_secret(key):
    try:
        secret_file = "../secrets.json"
        with open(secret_file) as f:
            secrets = json.loads(f.read())
        return secrets[key]
    except KeyError:
        raise ValueError(f"{key}가 없습니다.")
    except Exception:
        return None


class Twitter:
    class ScreenName:
        TRUMP = "realdonaldtrump"
        BIDEN = "JoeBiden"

    class Token:
        API_BEARER_TOKEN = get_secret("BEARER_TOKEN")
        API_ACCESS_TOKEN = get_secret("ACCESS_TOKEN")
        API_ACCESS_TOKEN_SECRET = get_secret("ACCESS_TOKEN_SECRET")

    class API:
        TIMELINE_API_URL = f"https://api.twitter.com/1.1/statuses/user_timeline.json"
