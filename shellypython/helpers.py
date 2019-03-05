import requests
from .const import REQUEST_TIMEOUT
from .exception import (
    ShellyNetworkException, ShellyUnreachableException
)


def Get_item_safe(lst, idx, default):
    try:
        if isinstance(lst, dict):
            return lst[idx]
        if isinstance(lst, list):
            return idx if idx in lst else default
        else:
            return default
    except KeyError:
        return default


def Call_shelly_api(url, username=None, password=None):
    """Call shelly Api and get RAW result"""
    from requests.exceptions import RequestException
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        if (r.status_code != 200):
            raise ShellyUnreachableException("Invalid status code %s" % r.status_code)
        return r.text
    except RequestException:
        raise ShellyNetworkException(
            message="Shelly not responding at address %s" % url)
