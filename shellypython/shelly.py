from datetime import datetime, timedelta
import threading
import socket
import struct
import json
from .const import (VERSION, COAP_IP, COAP_PORT)
from .helpers import (
    Call_shelly_api, toString, get_device_id
    )
import logging
from .shelly_object import (Shelly_block)

_LOGGER = logging.getLogger(__name__)


class Shelly():
    """Represents a Shelly device base class"""
    def __init__(self, username=None, password=None):

        _LOGGER.info("Start shellypython %s", VERSION)

        self.stopped = threading.Event()
        self.coloT_blocks = {}
        self.devices = []
        self.coloT_blocks_added = []
        self.coloT_blocks_updated = []
        self.added_devices = []
        self.removed_devices = []
        self.master_username = username
        self.master_password = password
        self._udp_thread = None
        self._socket = None
        self.igmp_fix_enabled = False
        self.start_socket()

    def init_socket(self):
        udp_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM,
            socket.IPPROTO_UDP)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 10)
        udp_socket.bind(('', COAP_PORT))
        mreq = struct.pack(
            "=4sl", socket.inet_aton(COAP_IP),
            socket.INADDR_ANY)
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        udp_socket.settimeout(10)
        self._socket = udp_socket

    def start_socket(self):
        self.init_socket()
        self._udp_thread = threading.Thread(target=self._udp_reader)
        self._udp_thread.daemon = True
        self._udp_thread.start()

    def stop_socket(self):
        self.stopped.set()
        if self._udp_thread is not None:
            self._udp_thread.join()
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self._socket.close()

    def version(self):
        return VERSION

    def COAP_discover(self):
        msg = bytes(b'\x50\x01\x00\x0A\xb3cit\x01d\xFF')
        self._socket.sendto(msg, (COAP_IP, COAP_PORT))

    def update_status_information(self):
        """Update status information for all devices"""
        for device in self.devices:
            device.update_status_information()

    def add_device(self, device, code):
        _LOGGER.debug('Add device')
        self.devices.append(device)
        print(device.__dict__)
        for callback in self.added_devices:
            callback(device, code)

    def remove_device(self, dev, code):
        _LOGGER.debug('Remove device')
        self.devices.remove(dev)
        for callback in self.removed_devices:
            callback(dev, code)

    def _udp_reader(self):

        next_igmp_fix = datetime.now() + timedelta(minutes=1)

        while not self.stopped.isSet():
            try:

                if self.igmp_fix_enabled and datetime.now() > next_igmp_fix:
                    _LOGGER.debug("IGMP fix")
                    next_igmp_fix = datetime.now() + timedelta(minutes=1)
                    mreq = struct.pack("=4sl", socket.inet_aton(COAP_IP),
                                       socket.INADDR_ANY)
                    print(socket.INADDR_ANY)
                    print(mreq)
                    try:
                        self._socket.setsockopt(socket.IPPROTO_IP,
                                                socket.IP_DROP_MEMBERSHIP,
                                                mreq)
                    except Exception as e:
                        _LOGGER.debug("Can't drop membership, " + str(e))
                    try:
                        self._socket.setsockopt(socket.IPPROTO_IP,
                                                socket.IP_ADD_MEMBERSHIP, mreq)
                    except Exception as e:
                        _LOGGER.debug("Can't add membership, " + str(e))

                _LOGGER.debug("Wait for UDP message")

                try:
                    dataTmp, addr = self._socket.recvfrom(500)
                except socket.timeout:
                    continue

                _LOGGER.debug("Got UDP message")

                data = bytearray(dataTmp)
                _LOGGER.debug(" Data: %s", data)

                byte = data[0]
                # ver = byte >> 6
                # typex = (byte >> 4) & 0x3
                # tokenlen = byte & 0xF

                code = data[1]
                # msgid = 256 * data[2] + data[3]

                pos = 4

                _LOGGER.debug(' Code: %s', code)

                if code == 30 or code == 69:

                    byte = data[pos]
                    totDelta = 0

                    device_type = ''
                    id = ''

                    while byte != 0xFF:
                        delta = byte >> 4
                        length = byte & 0x0F

                        if delta == 13:
                            pos = pos + 1
                            delta = data[pos] + 13
                        elif delta == 14:
                            pos = pos + 2
                            delta = data[pos - 1] * 256 + data[pos] + 269

                        totDelta = totDelta + delta

                        if length == 13:
                            pos = pos + 1
                            length = data[pos] + 13
                        elif length == 14:
                            pos = pos + 2
                            length = data[pos - 1] * 256 + data[pos] + 269

                        value = data[pos + 1:pos + length]
                        pos = pos + length + 1

                        if totDelta == 3332:
                            device_type, id, _ = toString(value).split('#', 2)

                        byte = data[pos]

                    payload = toString(data[pos + 1:])
                    _LOGGER.debug(' Type %s, Id %s, Payload *%s*', device_type,
                                  id, payload.replace(' ', ''))

                    if id not in self.coloT_blocks:
                        self.coloT_blocks[id] = Shelly_block(
                            id, device_type, self,
                            addr[0], code, useCoAP=True)
                        for callback in self.coloT_blocks_added:
                            callback(self.coloT_blocks[id])
                    if code == 30:
                        payload_json = {d[1]: d[2] for d in json.loads(payload)['G']}
                        self.coloT_blocks[id].useCoAP = True
                        self.coloT_blocks[id].update(payload_json, addr[0])
                        for callback in self.coloT_blocks_updated:
                            callback(self.coloT_blocks[id])

            except Exception as e:
                _LOGGER.exception("Error receiving UDP: %s", e)

    def manual_add_device(self, ip_address, username=None, password=None):
        _LOGGER.debug("start add manually: %s" % ip_address)
        if (username and password):
            pass
        elif (self.master_username and self.master_password):
            username = self.master_username
            password = self.master_password
        settings = Call_shelly_api(
                ip_address, '/settings',
                username, password)
        if settings is not None:
            device_id = get_device_id(settings.get("device").get("hostname")) if (
                settings.get("device").get("hostname")) else ip_address
            if device_id not in self.coloT_blocks:
                self.coloT_blocks[device_id] = Shelly_block(
                    device_id, None, self, ip_address, 0, username, password, settings,
                    useCoAP=False
                    )
                for callback in self.coloT_blocks_added:
                    callback(self.coloT_blocks[device_id])
            elif username and password:
                self.coloT_blocks[device_id].username = username
                self.coloT_blocks[device_id].password = password
                for callback in self.coloT_blocks_updated:
                    callback(self.coloT_blocks[device_id])
        _LOGGER.debug("end manually add: %s" % ip_address)
