"""
© Anastase Valentin, 2024. All rights reserved.

This code is protected by copyright law. Unauthorized copying, distribution, or modification
of this code, in part or in whole, is strictly prohibited without prior written consent
from the copyright owner.
"""

""" Show my Itch.io page for see my other games ! https://retrovalou.itch.io """

from gc import mem_alloc, mem_free, collect

from time import sleep
from game_basic_fct import button_right, button_left, button_action, button_up, button_down, update_input, buzzer, state_buzzer, update_buzzer_file, maj_buffer
from ssd1680_RV import display, temperature, Lut_choose, update_lut_by_temperature
from json import load
from utime import ticks_ms

def monotonic():
    return ticks_ms() / 1000
  
clean_screen = 40

pos_img = [9,20+30]

piezo_frequency = {"low": 240, "little_high": 400, "high": 480}

min_wait_after_start = 10


with open("/img/boot/Menu_img_multi.json", 'r') as f:
    img_menu = load(f)
with open("/img/boot/highscore.json", 'r') as f:
    img_highscore = load(f)
with open("/img/boot/creatorscore.json", 'r') as f:
    img_creatorscore = load(f)
with open("/img/boot/stars.json", 'r') as f:
    img_stars = load(f)
with open("/img/boot/temp_mode.json", 'r') as f:
    img_temp_mode = load(f)
with open("/img/boot/logo.json", 'r') as f:
    img_logo = load(f)


data_to_open = ["Climber", "Avignon", "rythme", "Fabric", "esquive"]

# HighScore
list_high_score = []
for data in data_to_open:
    try:
        with open('data/'+data+'.txt', 'r') as f:
            list_high_score.append(str(f.read()))
            f.close()
    except:
        with open('data/'+data+'.txt', 'w+') as f:
            f.write("0")
            list_high_score.append("0")
            f.close()
# add 0
for i in range(len(list_high_score)):
    Score_text = list_high_score[i]
    for j in range(len(Score_text), 4):
        Score_text = "0" + Score_text
    list_high_score[i] = Score_text


# Creator Score
nb_creator_score = 4
list_creator_score = [[] for i in range(nb_creator_score)]
for data in data_to_open:            
    with open('data/creator_score/'+data+'.txt', 'r') as f:
        creat_score_tmp = load(f)
        for i in range(nb_creator_score):
            list_creator_score[i].append(str(creat_score_tmp[i]))
        f.close()
# add 0
for k in range(nb_creator_score):
    for i in range(len(list_creator_score[k])):
        Score_text = list_creator_score[k][i]
        for j in range(len(Score_text), 4):
            Score_text = "0" + Score_text
        list_creator_score[k][i] = Score_text
# Check nb Stars
stop = False
nb_stars = 0
while not(stop) and nb_stars < nb_creator_score:
    for i in range(len(list_creator_score[nb_stars])):
        stop = stop | ( list_creator_score[nb_stars][i] > list_high_score[i])
    if(not(stop)):
        nb_stars += 1
del stop
        
pos_high_score = [50+20, 234-4+28]
pos_creator_score = [50+20, 235+16+28]

start_script = -1
index_img = 0
true_index_img = 0

clean_now = 0

display.display_grey()
collect()
display.buffer_all_white()
collect()
display.write_all_screen(hex_value = [0xFF])
collect()

display.write_img_ram(img_logo[0], [4+10, 20], ram_red_after_upd = False)

display.write_img_ram(img_menu[index_img], pos_img, ram_red_after_upd = False)
display.write_number(list_high_score[index_img], pos_high_score, only_write = True, ram_red_after_upd = False)
display.write_img_ram(img_highscore[0], [4+20, 230-4+28], ram_red_after_upd = False)

for i in range(min(nb_stars, 2)):
    display.write_img_ram(img_stars[0], [16 - i*12, 235+16+25], ram_red_after_upd = False)
for i in range(2, nb_stars):
    display.write_img_ram(img_stars[0], [16 + 64 + i*12, 235+16+25], ram_red_after_upd = False)
nb_stars = min(nb_stars, nb_creator_score-1)
display.write_number(list_creator_score[nb_stars][index_img], pos_creator_score, only_write = True, ram_red_after_upd = False, light_txt = True)
display.write_img_ram(img_creatorscore[0], [4+20-2+6, 230+16+3+28], ram_red_after_upd = False)

display.write_img_ram(img_temp_mode[0], [42, 10-6], ram_red_after_upd = False)

update_lut_by_temperature()
display.write_number(int(temperature), [42+2+8*3, 9-6], only_write = True, ram_red_after_upd = False)
display.write_number(int(Lut_choose), [42+2+8*9, 9-6], only_write = True, ram_red_after_upd = False)

display.display_partial(only_black = True)
display.go_in_lut_diff()
display.disable_analog()


# Pop Up 1 Time -> delete
del img_logo
del img_highscore
del img_creatorscore
del img_temp_mode
del img_stars
del data_to_open

collect()

while(start_script == -1):
    
    update_input()
    
    
    if(button_left.value == 2):
        buzzer(piezo_frequency["little_high"], [1])
        display.write_img_ram(img_menu[true_index_img], pos_img, erase = True, ram_red_after_upd = True)
        index_img += 1
        index_img = (index_img)%(len(img_menu)-1)
        # SP case sound         
        if(index_img == len(img_menu)-2 and not(state_buzzer())): # img buzzer not actif
            true_index_img = index_img+1
        else: # Habitual img write
            true_index_img = index_img          
        display.write_img_ram(img_menu[true_index_img], pos_img, erase = False, ram_red_after_upd = True)
        # High Score            
        if(len(list_high_score) > index_img):
            display.write_number(list_high_score[index_img], pos_high_score, ram_red_after_upd = True, only_write = True)
            display.write_number(list_creator_score[nb_stars][index_img], pos_creator_score, ram_red_after_upd = True, only_write = True, light_txt = True)
        else:
            display.write_number("0000", pos_high_score, ram_red_after_upd = True, only_write = True)
            display.write_number("0000", pos_creator_score, ram_red_after_upd = True, only_write = True, light_txt = True)            
        display.display_diff()


    elif(button_right.value == 2):
        buzzer(piezo_frequency["little_high"], [1])
        display.write_img_ram(img_menu[true_index_img], pos_img, erase = True, ram_red_after_upd = True)
        index_img = (index_img - 1 + (len(img_menu)-1))%(len(img_menu)-1)
        # SP case sound         
        if(index_img == len(img_menu)-2 and not(state_buzzer())): # img buzzer not actif
            true_index_img = index_img+1
        else: # Habitual img write
            true_index_img = index_img          
        display.write_img_ram(img_menu[true_index_img], pos_img, erase = False, ram_red_after_upd = True)
        # High Score
        if(len(list_high_score) > index_img):
            display.write_number(list_high_score[index_img], pos_high_score, ram_red_after_upd = True, only_write = True)
            display.write_number(list_creator_score[nb_stars][index_img], pos_creator_score, ram_red_after_upd = True, only_write = True, light_txt = True)
        else:
            display.write_number("0000", pos_high_score, ram_red_after_upd = True, only_write = True)
            display.write_number("0000", pos_creator_score, ram_red_after_upd = True, only_write = True, light_txt = True)            
        display.display_diff()


    elif(button_action.value == 2):
        
        if(index_img >= len(img_menu)-2): #  update state of buzzer
            update_buzzer_file(not(state_buzzer()))
            display.write_img_ram(img_menu[true_index_img], pos_img, erase = True, ram_red_after_upd = True)
            if(state_buzzer()):
                true_index_img = index_img
            else:
                true_index_img = index_img+1
            display.write_img_ram(img_menu[true_index_img], pos_img, erase = False, ram_red_after_upd = True)
            display.display_diff()
            
        else: # normal case -> Start Script
            start_script = index_img
            
        buzzer(piezo_frequency["little_high"], [1])
        
        
    elif(button_down.check_button_now() and button_up.check_button_now()): # USB MODE
        start_script = -2
        
        
    clean_now += 1
    if(clean_now >= clean_screen):
        display.display_diff()
        clean_now = 0
        
    sleep(1/60)
    maj_buffer(1)


del img_menu
del piezo_frequency
del list_high_score
del list_creator_score
del pos_high_score
del pos_creator_score

display.clean_screen(long = True)


while(display.busy.value() == 1 or min_wait_after_start > 0):
    sleep(1/60)
    maj_buffer(1)
    min_wait_after_start -= 1

del min_wait_after_start

if(start_script == -2):
    display.write_number("0110011101101", [20, 100])

collect()
print(f"Before Export Memory: {mem_alloc()} of {mem_free()} bytes used.")
if(start_script == 0):
    exec(open("/Climber.py").read())
elif(start_script == 1):
    exec(open("/Avignon.py").read())
elif(start_script == 2):
    exec(open("/rythme.py").read())
elif(start_script == 3):
    exec(open("/Fabric.py").read())
elif(start_script == 4):
    exec(open("/esquive.py").read())
elif(start_script == 5):
    exec(open("/Long_clean_screen.py").read())
   