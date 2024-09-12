"""
© Anastase Valentin, 2024. All rights reserved.

This code is protected by copyright law. Unauthorized copying, distribution, or modification
of this code, in part or in whole, is strictly prohibited without prior written consent
from the copyright owner.
"""

""" Show my Itch.io page for see my other games ! https://retrovalou.itch.io """


from math import sin
from machine import PWM, Pin

### Parameter ###
input_wait_before_enter = 4
force_bip_no_action = 600*15
wait_during_bip_no_action = 60

# Buzzer
piezo = PWM(Pin(9))
piezo_On = 16*100

### variables ###
list_buzzer = []
curr_time = 0
last_time_input = 0


### Buttons ###
class Button_:
    value = 0
    curr_upd_screen = False
    old_curr_upd_screen = False

    def __init__(self, GPX):
        self.curr_button = Pin(GPX, Pin.IN, Pin.PULL_DOWN)
        self.last_tap = 0
        
    def check_button_now(self):
        return(self.curr_button.value() == 1)

    def update(self, is_upd_screen = False):
        global curr_time
        global last_time_input
        # Change to not update screen to Update Screen
        if(is_upd_screen and not(self.curr_upd_screen) and self.value == 2):
            self.value = 1
        
        if(self.curr_button.value() == 1):
            if(self.value == 0 and self.last_tap == 0):
                self.value = 2
                self.last_tap = input_wait_before_enter
                last_time_input = curr_time
            elif((self.value == 2 and not(self.curr_upd_screen)) or self.value == 1):
                self.value = 1
            else:
                self.value = 0
                
        else:
            if(self.value == -2 or self.value == 0):
                self.value = 0
            elif(self.value != 2 or not(is_upd_screen)):
                self.value = -2
        
        if(self.last_tap != 0):
            self.last_tap -= 1
            last_time_input = curr_time

        self.old_curr_upd_screen = self.curr_upd_screen
        self.curr_upd_screen =  is_upd_screen

# Config of button
button_right = Button_(17)
button_left = Button_(16)
button_action = Button_(18)
button_start = Button_(0)
button_up = Button_(6)
button_down = Button_(7)

def update_input(is_upd_screen = False):
    button_right.update(is_upd_screen = is_upd_screen)
    button_left.update(is_upd_screen = is_upd_screen)
    button_action.update(is_upd_screen = is_upd_screen)
    button_up.update(is_upd_screen = is_upd_screen)
    button_down.update(is_upd_screen = is_upd_screen)


### SP execute when wait screen ###
def start_exc_wit_busy():
    global curr_time

def exc_wit_busy():
    update_input(is_upd_screen = True)
    maj_buffer(0.5) # wait on busy * wait for 1 frame classic


### """Random""" function ### # It's a personal choose ! 
def randrange(t, a, b):
    if(a>b):
        tmp = b
        b = a
        a = tmp
    return max(min(int(random(t)*(b-a+1)+a), b), a)
    
def random(t):
    return (sin(t) % 1 + 1) % 1


### Buzzer ###
buzzer_activ = True   
with open('data/parameter/sound.txt', 'r') as f:
    if(int(f.read()) == 0):
        buzzer_activ = False

def update_buzzer_file(buzz_update):
    global buzzer_activ
    buzzer_activ = buzz_update
    with open('data/parameter/sound.txt', 'r') as f:
        if(buzzer_activ):
            f.write(str(1))
        else:
            f.write(str(0))

def state_buzzer():
    return buzzer_activ


class buzzer:
    
    def __init__(self, frequency, list_wait_time, force_bip = False):
        global piezo
        global piezo_On
        global list_buzzer
        global buzzer_activ
        
        if(not(buzzer_activ) and not(force_bip)):
            return

        self.time = curr_time
        self.frequency = frequency
        self.list_wait_time = list_wait_time
        self.curr_wait = 0
        self.On = True

        piezo.freq(self.frequency)
        piezo.duty_u16(piezo_On)
        list_buzzer.append(self)
    
    def update(self, time_curr):
        global piezo
        global piezo_On
        global list_buzzer

        if(self.On and self.list_wait_time[self.curr_wait]+self.time < time_curr):
            self.On = False
            piezo.duty_u16(0)
            self.time = time_curr
        elif(not(self).On and self.list_wait_time[self.curr_wait]+self.time < time_curr):
            self.curr_wait += 1
            self.On = True
            self.time = time_curr
            if(self.curr_wait >= len(self.list_wait_time)):
                piezo.duty_u16(0)
                return False
            piezo.freq(self.frequency)
            piezo.duty_u16(piezo_On)
        return True   


def maj_buffer(time_to_add):
    global curr_time
    global last_time_input
    global force_bip_no_action
    global wait_during_bip_no_action
    i = 0
    curr_time += time_to_add
    while i < len(list_buzzer):
        result = list_buzzer[i].update(curr_time)
        if(result):
            i += 1
        else:
            list_buzzer.pop(i)

    if(curr_time > last_time_input + force_bip_no_action):
            buzzer(480, [5, 3, 2], force_bip = True)
            last_time_input += wait_during_bip_no_action
