import json


def get_secret(key):
    try:
        secret_file = "../secrets.json"
        with open(secret_file) as f:
            secrets = json.loads(f.read())
        return secrets[key]
    except KeyError:
        raise ValueError(f"***REMOVED***key***REMOVED***가 없습니다.")
    except Exception:
        return None


class Twitter:
    API_TOKEN = get_secret("TOKEN")
    TIMELINE_API_URL = f"https://api.twitter.com/1.1/statuses/user_timeline.json"
    TRUMP = "realdonaldtrump"
    BIDEN = "JoeBiden"
