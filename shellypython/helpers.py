import requests
from .const import REQUEST_TIMEOUT
from .exception import (
    ShellyNetworkException, ShellyUnreachableException,
    ShellyAccessForbitten
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

        session = requests.Session()
        if username and password:
            session.auth = (username, password)
        r = session.get(url, timeout=REQUEST_TIMEOUT)

        if r.status_code == 401:
            raise ShellyAccessForbitten("Access denied")
        elif (r.status_code != 200):
            raise ShellyUnreachableException("Invalid status code %s" % r.status_code)
        return r.text
    except RequestException:
        raise ShellyNetworkException(
            message="Shelly not responding at address %s" % url)


def Rssi_to_percentage(rssi=0):
    """Conversion from RSSI to Percent"""
    return min(max(2 * (0 if rssi is None else rssi + 100), 0), 100)
