from datetime import datetime
import logging
from .helpers import Call_shelly_api
from .const import SHELLY_MODEL

_LOGGER = logging.getLogger(__name__)


class ShellyDevice(object):
    """Base shelly device class"""
    def __init__(self, coloT_block):
        self.ip_address = None
        self.last_updated = datetime.now()
        self.coloT_block = coloT_block
        self.device_id = coloT_block.device_id
        self.shelly_type = coloT_block.shelly_type
        self.ip_address = coloT_block.ip_address
        self.device_updated = []
        self._unavailableAfterSec = 20
        self.state_values = None
        self.info_values = None
        self.state = None
        self.mqtt_enabled = False

    def type_name(self):
        try:
            name = SHELLY_MODEL[self.shelly_type]
            print("name -- {}".format(name))
        except Exception:
            print("device type_name exception!")
            name = self.shelly_type
        return name

    def _sendCommand(self, url):
        self.coloT_block._http_get(url)

    def available(self):
        if self.last_updated is None:
            return False
        diff = datetime.now() - self.last_updated
        return diff.total_seconds() < self._unavailableAfterSec

    def _update(self, new_state=None, new_state_values=None, new_values=None,
                info_values=None):
        _LOGGER.debug(
            "Update state:%s stateValue:%s values:%s", new_state,
            new_state_values, new_values
            )
        self.last_updated = datetime.now()
        need_update = False
        if new_state is not None:
            if self.state != new_state:
                self.state = new_state
                need_update = True
        if new_state_values is not None:
            if self.state_values != new_state_values:
                self.state_values = new_state_values
                need_update = True
        if new_values is not None:
            self.sensor_values = new_values
            need_update = True
        if info_values is not None:
            self.info_values = info_values
            need_update = True
        if need_update:
            self._device_updated()

    def update_status_information(self, info_values):
        """Update the status information"""
        self._update(info_values=info_values)
        mqtt = info_values.get('mqtt')
        if mqtt is not None:
            self.mqtt_enabled = mqtt.connected
        else:
            self.mqtt_enabled = False

    def _device_updated(self):
        for callback in self.device_updated:
            callback()

    def _remove_my_self(self):
        self.coloT_block._remove_device(self)


class ShellyUnknown(ShellyDevice):
    def __init__(self, coloT_block):
        super(ShellyUnknown, self).__init__(coloT_block)
        self.device_type = "UNKNOWN"

    def update(self, data):
        pass


class ShellyRelay(ShellyDevice):
    def __init__(self, coloT_block, channel, position, power=None):
        super(ShellyRelay, self).__init__(coloT_block)
        self.device_id = coloT_block.device_id
        if channel > 0:
            self.device_id += '-' + str(channel)
            self._channel = channel - 1
        else:
            self._channel = 0
        self._pos = position
        self._power = power
        self.state = None
        self.device_type = "RELAY"

    def update(self, data):
        new_state = data['G'][self._pos][2] == 1
        new_values = None
        if self._power is not None:
            watt = data['G'][self._power][2]
            new_values = {'watt': watt}
        self._update(new_state, None, new_values)

    def turn_on(self):
        self._sendCommand("/relay/" + str(self._channel) + "?turn=on")

    def turn_off(self):
        self._sendCommand("/relay/" + str(self._channel) + "?turn=off")


class ShellyRoller(ShellyDevice):
    def __init__(self, coloT_block):
        super(ShellyRoller, self).__init__(coloT_block)
        self.device_id = coloT_block.device_id
        self.device_type = "ROLLER"
        self.state = None
        self.position = None
        self.support_position = False
        self.motion_state = None
        self.last_direction = None
        self.update_settings()

    def update(self, data):
        watt = data['G'][2][2]
        state = self.position != 0
        self.update_settings()
        self._update(state, None, {'watt': watt})

    def update_settings(self):
        settings = Call_shelly_api(
                self.coloT_block.ip_address, '/roller/0',
                self.coloT_block.username, self.coloT_block.password)
        self.support_position = settings.get("positioning", False)
        self.motion_state = settings.get("state", False)
        self.last_direction = settings.get("last_direction")
        self.position = settings.get('current_pos', 0)

    def up(self):
        self._sendCommand("/roller/0?go=" + ("open"))

    def down(self):
        self._sendCommand("/roller/0?go=" + ("close"))

    def stop(self):
        self._sendCommand("/roller/0?go=stop")

    def set_position(self, pos):
        self._sendCommand("/roller/0?go=to_pos&roller_pos=" + str(pos))


class ShellyPowerMeter(ShellyDevice):
    def __init__(self, coloT_block, channel, pos):
        super(ShellyPowerMeter, self).__init__(coloT_block)
        self.device_id = coloT_block.device_id
        if channel > 0:
            self.device_id += "-" + str(channel)
            self._channel = channel - 1
        else:
            self._channel = 0
        self._pos = pos
        self.sensor_values = {}
        self.device_type = "POWERMETER"

    def update(self, data):
        watt = data['G'][self._pos][2]
        self._update(None, None, {'watt': watt})
