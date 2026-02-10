from datetime import datetime, timedelta, timezone

def get_ecuador_time() -> datetime:
    """Retorna la fecha y hora actual en zona horaria de Ecuador (UTC-5)"""
    ecuador_tz = timezone(timedelta(hours=-5))
    return datetime.now(ecuador_tz)
