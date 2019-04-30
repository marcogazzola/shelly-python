import json
import http.client as httplib
import base64
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


def Call_shelly_api(baseurl, url, username=None, password=None):
    print("call_shelly_api")
    try:
        conn = httplib.HTTPConnection(baseurl)
        headers = {}
        if username and password:
            login = '%s:%s' % (username, password)
            auth = str(
                base64.b64encode(login.encode()), 'cp1252')
            headers["Authorization"] = "Basic %s" % auth
        conn.request("GET", url, None, headers)
        resp = conn.getresponse()
        if resp and resp.status == 401:
            raise ShellyAccessForbitten("Access denied")
        elif resp and resp.status != 200:
            raise ShellyUnreachableException("Invalid status code %s" % resp.status)
        body = resp.read()
        conn.close()
        json_response = json.loads(body)
        return json_response
    except httplib.HTTPException:
        raise ShellyNetworkException(
            message="Shelly not responding at address %s%s" % (baseurl, url))


def Rssi_to_percentage(rssi=0):
    """Conversion from RSSI to Percent"""
    return min(max(2 * (0 if rssi is None else rssi + 100), 0), 100)


def toString(x):
    return str(x, 'cp1252')


def get_device_id(name):
    return name[name.find("-")+1:]
