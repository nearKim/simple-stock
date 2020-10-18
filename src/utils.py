from datetime import datetime, timedelta


def convert_utc_to_usa_dt(dt_str: str) -> datetime:
    """ UTC string을 datetime unaware한 미국시간 객체로 변환한다 """
    utc_dt = datetime.strptime(dt_str, "%a %b %d %H:%M:%S +0000 %Y")
    return utc_dt - timedelta(hours=4)
