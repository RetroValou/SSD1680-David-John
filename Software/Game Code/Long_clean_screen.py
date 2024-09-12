from gc import mem_alloc, mem_free, collect

from time import sleep
from game_basic_fct import button_right, button_left, button_action, update_input, buzzer, maj_buffer, de_init_button
from ssd1680_RV import display
from json import load
from utime import ticks_ms

def monotonic():
    return ticks_ms() / 1000

pos_img = [9,20]


piezo_frequency = {"low": 240, "little_high": 400, "high": 480}

display.display_long_clean()
sleep(4)
display.display_long_clean()
sleep(4)
display.display_long_clean()
sleep(4)