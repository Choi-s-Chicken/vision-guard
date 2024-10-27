import datetime

log_time_format = "%Z %x %X"
log_format = "%(asctime)s %(levelname)8s %(message)s"
default_timef = "%Y%m%d%H%M%S"

def get_now_ftime(time_format: str | None = default_timef) -> str:
    time = datetime.datetime.now()
    f_time = time.strftime(time_format)
    return f_time

def get_now_iso_time() -> str:
    time = datetime.datetime.now()
    return time.isoformat()

def parse_time(ftime_str: str, time_format: str | None = default_timef) -> datetime.datetime:
    time = datetime.datetime.strptime(ftime_str, time_format)
    return time