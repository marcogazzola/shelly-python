VERSION = '0.2.0'

DEVICE_READY = "Online"
DEVICE_NOT_READY = "Offline"
REQUEST_TIMEOUT = 5
SHELLY_MODEL = {
    'SHSW-1': 'Shelly 1',
    'SHSW-21': 'Shelly 2',
    'SHSW-22': 'Shelly HD Pro',
    'SHSW-25': 'Shelly 2.5',
    'SHSW-44': 'Shelly 4 Pro',
    'SHPLG-1': 'Shelly Plug',
    'SHPLG2-1': 'Shelly Plug',
    'SHRGBWW-01': 'Shelly RGBWW',
    'SHBLB-1': 'Shelly Bulb',
    'SHHT-1': 'Shelly H&T',
    'SHRGBW2': 'Shelly RGBW2',
    'SHEM-1': 'Shelly EM',
    'SHCL-255': 'Shelly Bulb',
    'SH2LED-1': 'Shelly 2LED',
    'SHSK-1': 'Shelly Socket',
}
WORKING_MODE_RELAY = 'relay'
WORKING_MODE_ROLLER = 'roller'
SHELLY_WORKING_MODE = {WORKING_MODE_RELAY: 'Relay', WORKING_MODE_ROLLER: 'Roller shutter'}
ISON_ON = 'ON'
ISON_OFF = 'OFF'
UNDEFINED_VALUE = 'Undefined'

COAP_IP = "224.0.1.187"
COAP_PORT = 5683
COAP_CONFIG = {
    'SHSW-25': {
        'relay': {
            'relay': {
                0: '112',
                1: '122'
            },
            'power': {
                0: '111',
                1: '121'
            }
        },
        'roller': {
            'open': '112',
            'close': '122',
            'position': '113',
            'power': {
                0: '111',
                1: '121'
            }
        }
    },
    'SHSW-21': {
       'relay': {
            'relay': {
                0: '112',
                1: '122'
            },
            'power': {
                0: '111'
            }
        },
        'roller': {
            'open': '112',
            'close': '122',
            'position': '113',
            'power': {
                0: '111'
            }
        }
    },
    'SHSW-1': {
        'relay': {
            0: '112'
        }
    }
}
