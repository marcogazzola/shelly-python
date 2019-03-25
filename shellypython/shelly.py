import asyncio
import json
from .const import (
    DEVICE_READY, DEVICE_NOT_READY, SHELLY_MODEL, SHELLY_WORKING_MODE,
    WORKING_MODE_RELAY, WORKING_MODE_ROLLER, ISON_ON, ISON_OFF,
    UNDEFINED_VALUE
    )
from .exception import (ShellyException)
from .helpers import (Get_item_safe, Call_shelly_api, Rssi_to_percentage)
import logging

_LOGGER = logging.getLogger(__name__)


class Shelly():
    """Represents a Shelly device base class"""

    def __init__(self, address, username=None, password=None):
        """Initialize Shelly base class"""
        self.loop = asyncio.new_event_loop()
        self.device_address = address
        self.username = username
        self.password = password

        self.__api_address = "http://" + address if not address.startswith('http://') else address
        _LOGGER.debug("Api address: %s", self.__api_address)
        self.model_raw = None
        self.model = None
        self.working_mode_raw = None
        self.working_mode = None
        self.host_name = None
        self.main_status = None

        self.wifi_sta = None
        self.system = None
        self.cloud = None
        self.mqtt = None
        self.firmware = None
        self.relays = None
        self.rollers = None

    def update_data(self):
        """Update all shelly informations"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.__update_data())
        return self

    @asyncio.coroutine
    def __update_data(self):
        """Update all shelly informations"""
        # loop = asyncio.get_event_loop()
        api_base_info_req = self.loop.run_in_executor(None, self.__get_base_info_api)
        api_status_req = self.loop.run_in_executor(None, self.__get_status_api)
        api_status_res = yield from api_status_req
        api_base_info_res = yield from api_base_info_req

        self.__set_base_info_api(api_base_info_res)
        self.__set_status_api(api_status_res)

    def __get_status_api(self):
        """Get RAW shelly status"""
        try:
            return Call_shelly_api(
                url=self.__api_address + "/status",
                username=self.username,
                password=self.password)
        except ShellyException as err:
            _LOGGER.warning(err)

    def __set_status_api(self, json_response):
        """Get Shelly status thought api"""
        try:
            try:
                json_obj = None
                if json_response is None:
                    self.main_status = DEVICE_NOT_READY
                    json_response = "{}"
                else:
                    self.main_status = DEVICE_READY

                json_obj = json.loads(json_response)

                self.system = System(json_response)
                self.firmware = (
                    Firmware() if 'update' not in json_obj
                    else Firmware(json.dumps(json_obj['update']))
                    )
                self.mqtt = (
                    Mqtt() if 'mqtt' not in json_obj else Mqtt(json.dumps(json_obj['mqtt'])))
                self.cloud = (
                    Cloud() if 'cloud' not in json_obj else Cloud(json.dumps(json_obj['cloud'])))
                self.wifi_sta = (
                    Wifi_sta() if 'wifi_sta' not in json_obj
                    else Wifi_sta(json.dumps(json_obj['wifi_sta']))
                    )
                if self.working_mode_raw is None or self.working_mode_raw == WORKING_MODE_ROLLER:
                    rollers_dict = (
                        None if 'rollers' not in json_obj else json_obj['rollers'])
                    self.rollers = (
                        None if rollers_dict is None
                        else list(map(lambda x: Roller(json.dumps(x)), rollers_dict))
                        )
                if self.working_mode_raw is None or self.working_mode_raw == WORKING_MODE_RELAY:
                    relays_dict = (
                        None if 'relays' not in json_obj else json_obj['relays'])
                    self.relays = (
                        None if relays_dict is None
                        else list(map(lambda x: Relay(json.dumps(x)), relays_dict))
                        )

            except json.JSONDecodeError as err:
                raise ShellyException(err)
        except ShellyException as err:
            _LOGGER.warning(err)
            self.main_status = DEVICE_NOT_READY

        _LOGGER.debug("main_status: %s", self.main_status)

        return self

    def __get_base_info_api(self):
        """Get RAW shelly base info"""
        try:
            return Call_shelly_api(
                url=self.__api_address + "/settings",
                username=self.username,
                password=self.password)
        except ShellyException as err:
            _LOGGER.warning(err)

    def __set_base_info_api(self, json_response):
        """Get Shelly status thought api"""
        try:
            try:
                json_obj = None
                if json_response is None:
                    json_response = "{}"
                json_obj = json.loads(json_response)

                self.host_name = (
                    None
                    if 'device' not in json_obj or 'hostname' not in json_obj['device']
                    else json_obj['device']['hostname'])
                self.model_raw = (
                    None
                    if 'device' not in json_obj or 'type' not in json_obj['device']
                    else json_obj['device']['type']
                    )
                self.model = Get_item_safe(SHELLY_MODEL, self.model_raw, 'undefined')
                self.working_mode_raw = (
                    None
                    if 'mode' not in json_obj
                    else json_obj['mode']
                    )
                self.working_mode = (
                    Get_item_safe(SHELLY_WORKING_MODE, self.working_mode_raw, 'undefined'))

            except json.JSONDecodeError as err:
                _LOGGER.error("Error during parse json result.")
                raise ShellyException(err)
        except ShellyException as err:
            _LOGGER.warning(err)
            self.main_status = DEVICE_NOT_READY

        _LOGGER.debug("main_status: %s", self.main_status)


class BaseShellyAttribute():
    """Represents Sehlly base class"""

    def __init__(self, json_def=None):
        """Initialize Wifi_sta class"""
        if json_def is None:
            json_obj = {}
        else:
            json_obj = json.loads(json_def)
        self.__dict__ = json_obj

    def as_dict(self):
        return self.__dict__


class System(BaseShellyAttribute):
    """Represents System attributes"""

    def __init__(self, json_def=None):
        """Initialize System class"""
        if json_def is None:
            json_obj = {}
        else:
            json_obj = json.loads(json_def)

        self.mac = None if 'mac' not in json_obj else json_obj['mac']
        self.ram_total = None if 'ram_total' not in json_obj else json_obj['ram_total']
        self.ram_free = None if 'ram_free' not in json_obj else json_obj['ram_free']
        self.fs_size = None if 'fs_size' not in json_obj else json_obj['fs_size']
        self.fs_free = None if 'fs_free' not in json_obj else json_obj['fs_free']
        self.uptime = None if 'uptime' not in json_obj else json_obj['uptime']
        self.has_update = False if 'has_update' not in json_obj else json_obj['has_update']


class Roller(BaseShellyAttribute):
    """Represents roller shutter base class"""

    def __init__(self, json_def=None):
        """Initialize System class"""
        if json_def is None:
            json_obj = {}
        else:
            json_obj = json.loads(json_def)
        self.__dict__ = json_obj

        if (json_obj is not None and
                'positioning' in json_obj and
                json_obj['positioning'] and
                'current_pos' in json_obj):
            self.status = json_obj['current_pos']
        else:
            self.status = (
                json_obj['state']
                if 'current_pos' in json_obj else UNDEFINED_VALUE
                )


class Relay(BaseShellyAttribute):
    """Represents relay base class"""

    def __init__(self, json_def=None):
        """Initialize System class"""
        if json_def is None:
            json_obj = {}
        else:
            json_obj = json.loads(json_def)
        self.__dict__ = json_obj

        self.status = (
            ISON_OFF if 'ison' not in json_obj
            else ISON_ON if json_obj['ison'] else ISON_OFF
            )


class Wifi_sta(BaseShellyAttribute):
    """Represents Wifi_sta attributes"""

    def __init__(self, json_def=None):
        """Initialize Wifi_sta class"""
        if json_def is None:
            json_obj = {}
        else:
            json_obj = json.loads(json_def)
        self.__dict__ = json_obj

        self.connected = False if 'connected' not in json_obj else json_obj['connected']
        self.ssid = None if 'ssid' not in json_obj else json_obj['ssid']
        self.ip = None if 'ip' not in json_obj else json_obj['ip']
        self.rssi = None if 'rssi' not in json_obj else json_obj['rssi']
        self.quality = Rssi_to_percentage(self.rssi)


class Cloud(BaseShellyAttribute):
    """Represents Cloud attributes"""

    def __init__(self, json_def=None):
        """Initialize Cloud class"""
        if json_def is None:
            json_obj = {}
        else:
            json_obj = json.loads(json_def)
        self.__dict__ = json_obj

        self.connected = False if 'connected' not in json_obj else json_obj['connected']
        self.enabled = False if 'connected' not in json_obj else json_obj['connected']


class Mqtt(BaseShellyAttribute):
    """Represents Mqtt attributes"""

    def __init__(self, json_def=None):
        """Initialize Mqtt class"""
        if json_def is None:
            json_obj = {}
        else:
            json_obj = json.loads(json_def)
        self.__dict__ = json_obj

        self.connected = False if 'connected' not in json_obj else json_obj['connected']


class Firmware(BaseShellyAttribute):
    """Represents Firmware attributes"""

    def __init__(self, json_def=None):
        """Initialize Firmware class"""
        if json_def is None:
            json_obj = {}
        else:
            json_obj = json.loads(json_def)
        self.__dict__ = json_obj

        self.has_update = False if 'has_update' not in json_obj else json_obj['has_update']
        self.new_version = None if 'new_version' not in json_obj else json_obj['new_version']
        self.old_version = None if 'old_version' not in json_obj else json_obj['old_version']
        self.status = None if 'status' not in json_obj else json_obj['status']
