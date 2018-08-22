try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
from rgbmatrix import Adafruit_RGBmatrix
import time
LED_MATRIX_ROWS = 16
LED_MATRIX_COLS = 32
