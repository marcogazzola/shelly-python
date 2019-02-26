import requests
from .const import (DEVICE_READY, DEVICE_NOT_READY)
from .exception import (ShellyException, ShellyNetworkException, ShellyUnreachableException)
from .pyjson import PyJSON
from .AbstractBase import AbstractBase
import logging

_LOGGER = logging.getLogger(__name__)


class Shelly(AbstractBase):
    """Represents a Shelly device base class"""

    def __init__(self, address):
        """Initialize Shelly base class"""

        self.device_address = address

        self.__api_address = "http://" + address if not address.startswith('http://') else address
        _LOGGER.debug("Api address: %s", self.__api_address)
        self.shelly_status = None
        self.shelly_attributes = None

    def shelly_status_api(self):
        """Get RAW shelly status"""
        from requests.exceptions import RequestException
        _LOGGER.debug("shelly_status_api")
        try:
            _LOGGER.warning(self.__api_address + "/status")
            r = requests.get(self.__api_address + "/status")
            if (r.status_code != 200):
                _LOGGER.error(r.status_code)
                raise ShellyUnreachableException("Invalid status code %s" % r.status_code)
            return r.json()
        except RequestException as err:
            _LOGGER.error(err)
            _LOGGER.error("Shelly not responding at address %s" % self.device_address)
            raise ShellyNetworkException(
                message="Shelly not responding at address %s" % self.device_address)

    def get_shelly_status(self, api_status=None):
        """Get Shelly status thought api"""
        try:
            json_response = api_status if api_status is None else self.shelly_status_api()
            try:
                json_obj = PyJSON(json_response)
                attributes = Attributes(
                    json_obj.mac, json_obj.ram_total, json_obj.ram_free,
                    json_obj.fs_size, json_obj.fs_free, json_obj.uptime)
                attributes.wifi_sta = Wifi_sta(
                    json_obj.wifi_sta.connected, json_obj.wifi_sta.ssid,
                    json_obj.wifi_sta.ip, json_obj.wifi_sta.rssi)
                attributes.mqtt = Mqtt(json_obj.mqtt.connected)
                attributes.cloud = Cloud(json_obj.cloud.connected, json_obj.cloud.enabled)
                attributes.update = Update(
                    json_obj.update.new_version, json_obj.update.old_version,
                    json_obj.update.status, json_obj.update.has_update)

                self.shelly_attributes = attributes
                self.shelly_status = DEVICE_READY
            except Exception:
                _LOGGER.error("Error during parse json result.")
                raise ShellyException
        except ShellyException as err:
            self.shelly_status = DEVICE_NOT_READY
            self.shelly_attributes = None
            _LOGGER.error(err)

        _LOGGER.debug("shelly_status: %s", self.shelly_status)

        return self


class Attributes(AbstractBase):
    """Represents Shelly attributes"""

    def __init__(
            self, mac=None, ram_total=None,
            ram_free=None, fs_size=None, fs_free=None,
            uptime=None
            ):
        """Initialize attribute class"""
        self.mac = mac
        self.ram_total = ram_total
        self.ram_free = ram_free
        self.fs_size = fs_size
        self.fs_free = fs_free
        self.uptime = uptime
        self.wifi_sta = Wifi_sta()
        self.cloud = Cloud()
        self.mqtt = Mqtt()
        self.update = Update()


class Wifi_sta(AbstractBase):
    """Represents Wifi_sta attributes"""

    def __init__(
            self, connected=False, ssid=None,
            ip=None, rssi=None
            ):
        """Initialize Wifi_sta class"""
        self.connected = connected
        self.ssid = ssid
        self.ip = ip
        self.rssi = rssi


class Cloud(AbstractBase):
    """Represents Cloud attributes"""

    def __init__(self, connected=False, enabled=False):
        """Initialize Cloud class"""
        self.connected = connected
        self.enabled = enabled


class Mqtt(AbstractBase):
    """Represents Mqtt attributes"""

    def __init__(self, connected=False):
        """Initialize Mqtt class"""
        self.connected = connected


class Update(AbstractBase):
    """Represents Update attributes"""

    def __init__(
            self, new_version=None, old_version=None,
            status=None, has_update=False
            ):
        """Initialize Update class"""
        self.new_version = new_version
        self.old_version = old_version
        self.status = status
        self.has_update = has_update
