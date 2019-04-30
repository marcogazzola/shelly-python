import json
from .const import (
    WORKING_MODE_ROLLER, ISON_ON, ISON_OFF,
    UNDEFINED_VALUE, COAP_CONFIG)
from .helpers import (Call_shelly_api, Rssi_to_percentage)
from .device import (ShellyUnknown, ShellyRelay, ShellyRoller, ShellyPowerMeter)
import logging

_LOGGER = logging.getLogger(__name__)


class BaseShellyAttribute(object):
    """Represents Sehlly base class"""
    json_obj = {}

    def __init__(self, json_def=None):
        """Initialize Wifi_sta class"""
        if json_def is None:
            self.json_obj = {}
        else:
            self.json_obj = json.loads(json_def)
        self.__dict__ = self.json_obj

    def as_dict(self):
        return self.__dict__


class SystemAttribute(BaseShellyAttribute):
    """Represents System attributes"""

    def __init__(self, json_def=None):
        super(SystemAttribute, self).__init__(json_def)

        self.mac = None \
            if 'mac' not in self.json_obj else self.json_obj['mac']
        self.ram_total = None \
            if 'ram_total' not in self.json_obj else self.json_obj['ram_total']
        self.ram_free = None \
            if 'ram_free' not in self.json_obj else self.json_obj['ram_free']
        self.fs_size = None \
            if 'fs_size' not in self.json_obj else self.json_obj['fs_size']
        self.fs_free = None \
            if 'fs_free' not in self.json_obj else self.json_obj['fs_free']
        self.uptime = None \
            if 'uptime' not in self.json_obj else self.json_obj['uptime']
        self.has_update = False \
            if 'has_update' not in self.json_obj else self.json_obj['has_update']


class RollerAttribute(BaseShellyAttribute):
    """Represents roller shutter base class"""

    def __init__(self, json_def=None):
        super(RollerAttribute, self).__init__(json_def)
        if (self.json_obj is not None and
                'positioning' in self.json_obj and
                self.json_obj['positioning'] and
                'current_pos' in self.json_obj):
            self.status = self.json_obj['current_pos']
        else:
            self.status = (
                self.json_obj['state']
                if 'current_pos' in self.json_obj else UNDEFINED_VALUE
                )


class RelayAttribute(BaseShellyAttribute):
    """Represents relay base class"""

    def __init__(self, json_def=None):
        super(RelayAttribute, self).__init__(json_def)

        self.status = (
            ISON_OFF if 'ison' not in self.json_obj
            else ISON_ON if self.json_obj['ison'] else ISON_OFF
            )


class Wifi_staAttribute(BaseShellyAttribute):
    """Represents Wifi_sta attributes"""

    def __init__(self, json_def=None):
        super(Wifi_staAttribute, self).__init__(json_def)

        self.connected = False if 'connected' not in self.json_obj else self.json_obj['connected']
        self.ssid = None if 'ssid' not in self.json_obj else self.json_obj['ssid']
        self.ip = None if 'ip' not in self.json_obj else self.json_obj['ip']
        self.rssi = None if 'rssi' not in self.json_obj else self.json_obj['rssi']
        self.quality = Rssi_to_percentage(self.rssi)


class CloudAttribute(BaseShellyAttribute):
    """Represents Cloud attributes"""

    def __init__(self, json_def=None):
        super(CloudAttribute, self).__init__(json_def)

        self.connected = False if 'connected' not in self.json_obj else self.json_obj['connected']
        self.enabled = False if 'connected' not in self.json_obj else self.json_obj['connected']


class MqttAttribute(BaseShellyAttribute):
    """Represents Mqtt attributes"""

    def __init__(self, json_def=None):
        super(MqttAttribute, self).__init__(json_def)

        self.connected = False if 'connected' not in self.json_obj else self.json_obj['connected']


class FirmwareAttribute(BaseShellyAttribute):
    """Represents Firmware attributes"""

    def __init__(self, json_def=None):
        super(FirmwareAttribute, self).__init__(json_def)

        self.has_update = False \
            if 'has_update' not in self.json_obj \
            else self.json_obj['has_update']
        self.new_version = None \
            if 'new_version' not in self.json_obj \
            else self.json_obj['new_version']
        self.old_version = None \
            if 'old_version' not in self.json_obj \
            else self.json_obj['old_version']
        self.status = None \
            if 'status' not in self.json_obj \
            else self.json_obj['status']


class Shelly_block():
    def __init__(
            self, device_id, shelly_type, parent, ip_address,
            code, username=None, password=None, api_settings=None,
            useCoAP=False):
        self.device_id = device_id
        self.shelly_type = shelly_type
        self.ip_address = ip_address
        self.devices = []
        self.code = code
        self.parent = parent
        self.username = username
        self.password = password
        self.updated = []
        self.api_settings = api_settings
        self.useCoAP = useCoAP
        self.blk = {}
        self.sensor = {}
        self._setup()

    def _block_updated(self):
        for callback in self.updated:
            callback()

    def update(self, data, new_ip_address):
        self.ip_address = new_ip_address
        for dev in self.devices:
            dev.ip_address = new_ip_address
            dev.update(data)

    def update_status_information(self):
        """Update the status information"""
        status = Call_shelly_api(
            self.ip_address, '/status',
            self.username, self.password)
        if status == {}:
            return

        info_values = {}

        wifi_sta = (
            Wifi_staAttribute() if 'wifi_sta' not in status
            else Wifi_staAttribute(json.dumps(status['wifi_sta']))
            )
        info_values['wifi_sta'] = wifi_sta

        update = (
            FirmwareAttribute() if 'update' not in status
            else FirmwareAttribute(json.dumps(status['update']))
            )
        info_values['update'] = update

        cloud = (
            CloudAttribute() if 'cloud' not in status
            else CloudAttribute(json.dumps(status['cloud']))
            )
        info_values['cloud'] = cloud

        mqtt = (
            MqttAttribute() if 'mqtt' not in status
            else MqttAttribute(json.dumps(status['mqtt']))
            )
        info_values['mqtt'] = mqtt

        self._block_updated()

        for dev in self.devices:
            dev.update_status_information(info_values)

    def _setup(self):
        _LOGGER.debug("start _setup")
        if self.shelly_type is None:
            self.api_settings = (
                self.api_settings if self.api_settings is not None else Call_shelly_api(
                        self.ip_address, '/settings',
                        self.username, self.password)
                )
            self.shelly_type = self.api_settings.get('device').get('type')
        if self.shelly_type == 'SHBLB-1' or self.shelly_type == 'SHCL-255':
            # self._add_device(pyShellyBulb(self))
            pass
        elif self.shelly_type == 'SHSW-21':
            self.api_settings = (
                self.api_settings if self.api_settings is not None else Call_shelly_api(
                    self.ip_address, '/settings',
                    self.username, self.password)
                )
            if self.api_settings.get('mode') == WORKING_MODE_ROLLER:
                self._add_device(ShellyRoller(self))
            else:
                self._add_device(ShellyRelay(
                    self, 1,
                    COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('relay').get(0),
                    COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('power').get(0)
                    ))
                self._add_device(ShellyRelay(
                    self, 2,
                    COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('relay').get(1),
                    COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('power').get(1)
                    ))
            self._add_device(ShellyPowerMeter(
                self, 0, COAP_CONFIG.get(
                    self.shelly_type, {}).get(
                        self.api_settings.get('mode'), {}).get('power').get(0)))
        elif self.shelly_type == 'SHSW-25':
            self.api_settings = (
                self.api_settings if self.api_settings is not None else Call_shelly_api(
                    self.ip_address, '/settings',
                    self.username, self.password)
                )
            if self.api_settings.get('mode') == WORKING_MODE_ROLLER:
                self._add_device(ShellyRoller(self))
            else:
                self._add_device(ShellyRelay(
                    self, 1,
                    COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('relay').get(0),
                    COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('power').get(0)
                    ))
                self._add_device(ShellyRelay(
                    self, 2,
                    COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('relay').get(1),
                    COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('power').get(1)
                    ))
                self._add_device(ShellyPowerMeter(
                    self, 1, COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('power').get(0)))
                self._add_device(ShellyPowerMeter(
                    self, 2, COAP_CONFIG.get(
                        self.shelly_type, {}).get(
                            self.api_settings.get('mode'), {}).get('power').get(1)))
        # elif self.shelly_type == 'SHSW-22':
        #     self._add_device(pyShellyRelay(self, 1, 0, 1))
        #     self._add_device(pyShellyRelay(self, 2, 2, 3))
        #     self._add_device(pyShellyPowerMeter(self, 1, 1))
        #     self._add_device(pyShellyPowerMeter(self, 2, 3))
        # elif self.shelly_type == 'SH2LED-1':
        #     self._add_device(pyShellyRGBW2W(self, 0))
        #     self._add_device(pyShellyRGBW2W(self, 1))
        # elif self.shelly_type == 'SHEM-1':
        #     self._add_device(pyShellyRelay(self, 1, 0, 1))
        elif self.shelly_type == 'SHSW-1' or self.shelly_type == 'SHSK-1':
            self._add_device(ShellyRelay(
                self, 0,
                COAP_CONFIG.get(self.shelly_type, {}).get('relay').get(0)
                ))
        elif self.shelly_type == 'SHSW-44':
            for channel in range(4):
                self._add_device(
                    ShellyRelay(
                        self, channel + 1,
                        COAP_CONFIG.get(self.shelly_type, {}).get('relay', {}).get(channel),
                        COAP_CONFIG.get(self.shelly_type, {}).get('power', {}).get(channel)
                        ))
        # elif self.shelly_type == 'SHRGBWW-01':
        #     self._add_device(pyShellyRGBWW(self))
        # elif self.shelly_type == 'SHPLG-1' or self.shelly_type == 'SHPLG2-1':
        #     self._add_device(pyShellyRelay(self, 0, 1, 0))
        #     self._add_device(pyShellyPowerMeter(self, 0, 0))
        # elif self.shelly_type == 'SHHT-1':
        #     self._add_device(pyShellySensor(self))
        # elif self.shelly_type == 'SHRGBW2':
        #     self.api_settings = self._http_get("/settings")
        #     if self.api_settings.get('mode', 'color') == 'color':
        #         self._add_device(pyShellyRGBW2C(self))
        #     else:
        #         for channel in range(4):
        #             self._add_device(pyShellyRGBW2W(self, channel + 1))
        else:
            self._add_device(ShellyUnknown(self))
        _LOGGER.debug("end _setup")

    def _add_device(self, device):

        self.devices.append(device)
        self.parent.add_device(device, self.code)
        return device

    def _remove_device(self, device):
        self.devices.remove(device)
        self.parent.remove_device(device.device_id, self.code)
        if not self.devices:
            self._setup()
