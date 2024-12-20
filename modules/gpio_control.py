import RPi.GPIO as GPIO
import config

HIGH = GPIO.HIGH
LOW = GPIO.LOW

# GPIO init
def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PIN_BUZZ, GPIO.OUT)
    GPIO.setup(config.PIN_BUZZ_DISABLE_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(config.PIN_R_LED, GPIO.OUT)
    GPIO.setup(config.PIN_Y_LED, GPIO.OUT)
    GPIO.setup(config.PIN_G_LED, GPIO.OUT)

def control_led(green: bool = None, yellow: bool = None, red: bool = None):
    if green  != None: GPIO.output(config.PIN_G_LED, green)
    if yellow != None: GPIO.output(config.PIN_Y_LED, yellow)
    if red    != None: GPIO.output(config.PIN_R_LED, red)
    pass

def control_alarm(control: bool):
    if control == True:
        GPIO.output(config.PIN_BUZZ, HIGH)
    else:
        GPIO.output(config.PIN_BUZZ, LOW)

def alarm_btn_status(pin: int = config.PIN_BUZZ_DISABLE_BTN) -> bool:
    return GPIO.input(pin)