DEFAULT_FPS = 60
DEFAULT_LED_SEP_COUNT = [117, 106, 117, 126]
DEFAULT_LED_COUNT = sum(DEFAULT_LED_SEP_COUNT)
DEFAULT_OSC_IP = "0.0.0.0"
IN_PORT = 9090
MOBILE_APP_OSC_PORT = 5005
MOBILE_APP_OSC_IP = "127.0.0.1"
MAX_SEGMENTS = 30

LED_BINARY_OUT_IP_0 = "192.168.11.105"
LED_BINARY_OUT_IP_1 = "192.168.11.106"
LED_BINARY_OUT_IP_2 = "192.168.11.107"
LED_BINARY_OUT_IP_3 = "192.168.11.108"
LED_BINARY_OUT_PORT = 7000
LED_BINARY_OSC_ADDRESS = "/light/serial"

DEFAULT_COLOR_PALETTES = {
    "A": [
        [255, 0, 0],    # Red
        [0, 255, 0],    # Green
        [0, 0, 255],    # Blue
        [255, 255, 0],  # Yellow
        [0, 255, 255],  # Cyan
        [255, 0, 255]   # Magenta
    ],
    "B": [
        [255, 128, 0],  # Orange
        [128, 0, 255],  # Purple
        [0, 128, 255],  # Sky Blue
        [255, 0, 128],  # Pink
        [128, 255, 0],  # Lime
        [255, 255, 255] # White
    ],
    "C": [
        [128, 0, 0],    # Dark Red
        [0, 128, 0],    # Dark Green
        [0, 0, 128],    # Dark Blue
        [128, 128, 0],  # Olive
        [0, 128, 128],  # Teal
        [128, 0, 128]   # Purple
    ],
    "D": [
        [255, 200, 200],  # Light Pink
        [200, 255, 200],  # Light Green
        [200, 200, 255],  # Light Blue
        [255, 255, 200],  # Light Yellow
        [200, 255, 255],  # Light Cyan
        [255, 200, 255]   # Light Magenta
    ],
    "E": [
        [100, 100, 100],  # Dark Gray
        [150, 150, 150],  # Medium Gray
        [200, 200, 200],  # Light Gray
        [255, 100, 50],   # Coral
        [50, 100, 255],   # Royal Blue
        [150, 255, 150]   # Light Green
    ]
}


UI_WIDTH = 1400
UI_HEIGHT = 800
UI_BACKGROUND_COLOR = (30, 30, 30)
UI_TEXT_COLOR = (220, 220, 220)
UI_ACCENT_COLOR = (50, 120, 220)
UI_BUTTON_COLOR = (60, 60, 60)

DEFAULT_TRANSPARENCY = [1.0, 1.0, 1.0, 1.0]
DEFAULT_LENGTH = [1, 0, 0]
DEFAULT_MOVE_SPEED = 0.0
DEFAULT_MOVE_RANGE = [0, DEFAULT_LED_COUNT - 1]
DEFAULT_INITIAL_POSITION = 0
DEFAULT_IS_EDGE_REFLECT = True
DEFAULT_DIMMER_TIME = [0, 100, 200, 100, 0]
DEFAULT_DIMMER_TIME_RATIO = 1.0


import copy
import logging

logger = logging.getLogger("color_signal_system")

RUNTIME_PALETTE_CACHE = {}
RUNTIME_MOBILE_CONFIG = {
    "ip": MOBILE_APP_OSC_IP,
    "port": MOBILE_APP_OSC_PORT
}

def initialize_palette_cache():
    global RUNTIME_PALETTE_CACHE
    RUNTIME_PALETTE_CACHE = copy.deepcopy(DEFAULT_COLOR_PALETTES)

initialize_palette_cache()

def update_palette_cache(palette_id, colors):
    global RUNTIME_PALETTE_CACHE
    if palette_id in RUNTIME_PALETTE_CACHE:
        RUNTIME_PALETTE_CACHE[palette_id] = copy.deepcopy(colors)
    else:
        RUNTIME_PALETTE_CACHE[palette_id] = copy.deepcopy(colors)

def get_palette(palette_id):
    global RUNTIME_PALETTE_CACHE
    if palette_id in RUNTIME_PALETTE_CACHE:
        return copy.deepcopy(RUNTIME_PALETTE_CACHE[palette_id])
    elif palette_id in DEFAULT_COLOR_PALETTES:
        return copy.deepcopy(DEFAULT_COLOR_PALETTES[palette_id])
    else:
        return copy.deepcopy(DEFAULT_COLOR_PALETTES["A"])

def get_mobile_config():
    global RUNTIME_MOBILE_CONFIG
    return {
        "ip": RUNTIME_MOBILE_CONFIG["ip"],
        "port": RUNTIME_MOBILE_CONFIG["port"]
    }

def update_mobile_config(ip=None, port=None):
    global RUNTIME_MOBILE_CONFIG
    
    if ip is not None:
        RUNTIME_MOBILE_CONFIG["ip"] = ip
        logger.info(f"Updated mobile app IP to: {ip}")
    
    if port is not None:
        try:
            port_value = int(port)
            RUNTIME_MOBILE_CONFIG["port"] = port_value
            logger.info(f"Updated mobile app port to: {port_value}")
        except (ValueError, TypeError):
            logger.warning(f"Invalid port value: {port}. Using existing value: {RUNTIME_MOBILE_CONFIG['port']}")
