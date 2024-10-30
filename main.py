import os
import time
import threading
import config
import src.utils as utils
from modules.logging import logger
import modules.gpio_control as gpio_ctrl
from webservice.main import VGApp
import modules.targets as targets

SERVICE_KEY = os.getenv("SERVICE_KEY")
PROCESS_URL = os.getenv("PROCESS_URL")
WEB_HOST = os.getenv("WEB_HOST")
WEB_PORT = os.getenv("WEB_PORT")

# GPIO Setup
## GPIO Init
gpio_ctrl.gpio_init()
gpio_ctrl.control_led(green=False, yellow=False, red=False)
config.set_config('status', config.STATUS_NORMAL)

# boot animation
for i in range(0, 3):
    gpio_ctrl.control_led(green=True, yellow=True, red=True)
    time.sleep(0.3)
    gpio_ctrl.control_led(green=False, yellow=False, red=False)
    time.sleep(0.3)
gpio_ctrl.control_led(green=True, yellow=True, red=True)
time.sleep(3)
gpio_ctrl.control_led(green=False, yellow=False, red=False)

# thread start
threading.Thread(target=targets._capture_target, args=(0.1,), daemon=True).start()
threading.Thread(target=targets._led_control_target, daemon=True).start()

# WebService Start
vg_web_app = VGApp()
vg_web_app.run(WEB_HOST, WEB_PORT, _debug=True)
