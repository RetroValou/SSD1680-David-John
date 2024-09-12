"""
© Anastase Valentin, 2024. All rights reserved.

This code is protected by copyright law. Unauthorized copying, distribution, or modification
of this code, in part or in whole, is strictly prohibited without prior written consent
from the copyright owner.
"""

""" Show my Itch.io page for see my other games ! https://retrovalou.itch.io """



from gc import mem_alloc, mem_free, collect
#print(f"Before Export Memory: {mem_alloc()} of {mem_free()} bytes used.")

import machine
from time import sleep
from game_basic_fct import button_right, button_left, button_action, button_start, button_up, button_down, randrange, update_input, maj_buffer, buzzer
from Avignon_game_class import battement, projectile_mark, init_projectile, projectile, speed_fall, grid_multi, init_visual_projectile, hidden_projectile_hidden, can_create_projectile
from math import sin
from ssd1680_RV import display
from json import load
from utime import ticks_ms

def monotonic():
    return ticks_ms() / 1000


# ////////////////////////////////////////////////////////
# //// Parameter ////

piezo_frequency = {"low": 240, "little_high": 400, "high": 480}

time_frame = 1/60
player_loc = {"x": 3, "y": 5}

wait_reactivate = 60
wait_restart = 60+30+60
speed_blink = 6

Player_pos_end = {"x": 28-2, "y": 34}
Player_pos_x = {"x_base" : 26-2, "x_up" : -2-6, "x_down" : 72}
pond_pos =  {"x_decal": 80-2, "y_decal" : 42}
canon_pos =  {"x": 12-2, "y" : -28}

score_pos = [94, 2]

last_time_input_init = 20

# size image
image_size = { "height" : 60, "width" :60 }

# Projectile generation
Projectile_gen_limit = {"min": 40, "max": 250}
Pond_change_limit = {"min": 40, "max": 200}
Pond_down_limit = {"min": 5, "max": 1}

Projectile_gen_increase = 1/40
Projectile_gen_random_power = 15
Projectile_gen_random_harmony = 1.4

Pond_change_increase = 1/50
Pond_change_random_power = 15
Pond_change_random_harmony = 1.4

Pond_down_increase = 1/50
Pond_down_random_power = 0.4
Pond_down_random_harmony = 1.4

index_pond = 2

nb_screen_move = 0

# Score to add
score_end = 5
score_end_bonus_speed = 2
score_end_bonus_is_use_jump = 2
speed_bonus_speed = 80
scores_add_life = [200, 500, 1000, 2000, 4000]

# ////////////////////////////////////////////////////////
# //// Function ////
# ////////////////////////////////////////////////////////

def blink_function(time_to_wait_reactivate):
    global last_speed_end
    
    last_wait_reactivate = time_to_wait_reactivate
    last_blink = 0
    while(last_wait_reactivate >= 0):
        last_wait_reactivate -= 1
        last_speed_end += 1
        frame_past()
        

def collider_with_projectile(i):
    global wait_reactivate
    global activ_mode
    global list_projectile
    global life
    global player_x
    global player_y
    global player_loc
    global max_up
    global display
        
    last_blink = 0
    activ_mode = False
    list_projectile[i].destroy(display, player_loc)
    list_projectile.pop(i)
    life -= 1
        
    if(life > 0):
        buzzer(piezo_frequency["low"], [6 for i in range(2)])
        display.update_img_screen(life_sprite[0], life_position(3-life-1), erase = False)
        blink_function(wait_reactivate)
        player_x = int(player_loc["x"]/2)
        player_y = player_loc["y"]-1
        max_up = player_y
        last_time_input = last_time_input_init


def fall_on_pond(player_y_add = 0):
    global wait_reactivate
    global activ_mode
    global life
    global player_x
    global player_y
    global player_loc
    global max_up
    global display
    global player_x_old
    global player_y_old
    
    last_blink = 0
    activ_mode = False
    life -= 1
    
    player_x = 2
    player_y += player_y_add
    
    if(life > 0):
        buzzer(piezo_frequency["low"], [6 for i in range(2)])
    display.delete_and_update_img_screen(player_sprite[player_x_old + player_y_old*player_loc["x"]],
                                                         [pos_x_player(player_x_old)+player_config_opti[player_x_old + player_y_old*player_loc["x"]][0],
                                                          player_y_old*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x_old + player_y_old*player_loc["x"]][1]],
                                                     player_sprite[player_x + player_y*player_loc["x"]],
                                                         [pos_x_player(player_x)+player_config_opti[player_x + player_y*player_loc["x"]][0],
                                                          player_y*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][1]] , already_lut = True)
    player_x_old = player_x
    player_y_old = player_y

    if(life > 0):
        display.update_img_screen(life_sprite[0], life_position(3-life-1), erase = False)
        blink_function(wait_reactivate)
        player_x = int(player_loc["x"]/2)
        player_y = player_loc["y"]-1
        max_up = player_y
        last_time_input = last_time_input_init



def add_score(add, only_write = False, ram_red_after_upd = False,  write_white_on_ram_before = False):
    global Score
    global display
    global score_pos
    Score += add
    Score_text = str(Score)
    for i in range(len(Score_text), 4):
        Score_text = "0" + Score_text
    display.write_number(Score_text, score_pos, inverse = True, erase_before = True, already_lut = True, only_write = only_write, write_white_on_ram_before = write_white_on_ram_before, ram_red_after_upd = ram_red_after_upd)
    return



def highscore_update(only_write = False):
    global high_score
    global display
    global score_pos
    Score_text = str(high_score)
    for i in range(len(Score_text), 4):
        Score_text = "0" + Score_text
    display.write_number(Score_text, score_pos, inverse = True, erase_before = True, already_lut = True, only_write = only_write)
    return
    
    
def Projectile_creation_speed(x):
    global Projectile_gen_limit
    global Projectile_gen_increase
    global Projectile_gen_random_power
    global Projectile_gen_random_harmony
    return Projectile_gen_limit["min"] + (Projectile_gen_limit["max"]- Projectile_gen_limit["min"])/(1+x*Projectile_gen_increase) + Projectile_gen_random_power * sin(x * Projectile_gen_random_harmony)


def Pond_changement_speed(x):
    global Pond_change_limit
    global Pond_change_increase
    global Pond_change_random_power
    global Pond_change_random_harmony
    return Pond_change_limit["min"] + (Pond_change_limit["max"]- Pond_change_limit["min"])/(1+x*Pond_change_increase) + Pond_change_random_power * sin(x * Pond_change_random_harmony)

def Pond_nb_down(x):
    global Pond_change_limit
    global Pond_change_increase
    global Pond_change_random_power
    global Pond_change_random_harmony
    return Pond_down_limit["min"] + (Pond_down_limit["max"]- Pond_down_limit["min"])/(1+x*Pond_down_increase) + Pond_down_random_power * sin(x * Pond_down_random_harmony)


last_time = monotonic()
def frame_past():
    global time_frame
    global curr_time
    global last_time
    global display
    
    display.try_execute_PILE_ram_now()
    display.try_execute_PILE_ram_before()
    updt_result = bat_system.update()

    diff_time = time_frame - (monotonic() - last_time)
    if(diff_time > 0 and diff_time <= time_frame):
        sleep(diff_time)
    last_time = monotonic()
    curr_time += 1
    maj_buffer(1)


def nb_score_sup(v_Score):
    i = 0
    while(i < len(scores_add_life)):
        if(v_Score < scores_add_life[i]):
            return i
        i+= 1
    return i

def life_position(i):
    return [106, (i)*18]

first_start = True

def pos_x_player(x):
    if(x == 1):
        return Player_pos_x["x_base"]
    if(x == 0):
        return Player_pos_x["x_up"]
    return Player_pos_x["x_down"]


img_mark_hex = 0

def init_mark_on_screen():
    global display
    global player_loc
    global grid_multi
    global player_sprite
    global Player_pos_end
    global life_sprite
    global life_position

    collect()
    # Write
    display.write_img_ram(canon_sprite[0],
                              [canon_pos["x"] + canon_config_opti[0][0],
                               canon_pos["y"] + canon_config_opti[0][1]],
                                  ram_now = False, ram_before = False)

    for x in range(player_loc["x"]):
        for y in range(player_loc["y"]):
            display.write_img_ram(player_sprite[x + y*player_loc["x"]],
                                  [pos_x_player(x) + player_config_opti[x + y*player_loc["x"]][0],
                                   (y*grid_multi["y"]+ grid_multi["y_decal"]) + player_config_opti[x + y*player_loc["x"]][1]],
                                  ram_now = False, ram_before = False)
        collect()
    display.write_img_ram(player_sprite[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1],
                          [Player_pos_end["x"] + player_config_opti[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1][0],
                           Player_pos_end["y"]+ player_config_opti[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1][1]],
                            ram_now = False, ram_before = False)
    
    for y in range(player_loc["y"]+1):
       for i in range(3):
            display.write_img_ram(sprite_pond[i+y*player_loc["x"]],
                                  [pond_pos["x_decal"] + pond_config_opti[i+y*player_loc["x"]][0],
                                   grid_multi["y"] * y+ pond_pos["y_decal"] + pond_config_opti[i+y*player_loc["x"]][1]],
                                   ram_now = False, ram_before = False)

    projectile_mark(player_loc, display)
    for i in range(3):
        display.write_img_ram(life_sprite[0], life_position(i), ram_now = False, ram_before = False)
    
    # Problem memory
    collect()
    print(f"Memory: {mem_alloc()} of {mem_free()} bytes used.")
    display.convert_hex_all_buffer_img()
    collect()
    
    display.buffer_all_white()



def mark_on_screen(keep_mark = False):
    global display
    global first_start
    collect()
    # Clean screen
    display.PILE_RAM_BEFORE = []
    display.PILE_RAM_NOW = []
    display.PILE_wait_updt_RAM_BEFORE = []
        
    if(not(first_start)): # already clean on first start of screen
        display.display_clean()
    else:
        first_start = False
    collect()
    
    display.write_img_ram_hex_img(display.buffer_img_stock_hex, ram_before = False)
    collect()
        
    if(not(keep_mark)):
    # Activate Screen
        display.display_grey()
        display.go_in_lut_diff()
        collect()
        display.buffer_all_white()
        collect()
        display.write_all_screen(hex_value = [0xFF])
        collect()
    else:
        display.display_black()
        collect()

    
    
# ////////////////////////////////////////////////////////
# /// Init global elem ///
# ////////////////////////////////////////////////////////

# BUTTON UP FOR DEBLOCK WRITE MODE -> FOR SAVE DATA ON RASBERRY PI PICO
if(button_action.check_button_now() == False):
    started_game = True
else:
    started_game = False
    
     
# BUTTON LEFT AND RIGHT FOR INIT HIGH SCORE
if(button_left.check_button_now() and button_right.check_button_now() ):
    try:
        with open('data/Avignon.txt', 'w') as f:
            f.write(str(0))
            f.close()
    except:
        print("Impossible to write in file")


# /// Player just load sprite ///
with open("/img/Avignon/guy_multi.json", 'r') as f:
    player_sprite, player_config_opti = display.pre_optimise_img(load(f)[:-2])        

# /// Life ///
with open("/img/Avignon/life.json", 'r') as f:
    life_sprite = load(f)       

# /// pond ///
with open("/img/Avignon/pond_multi.json", 'r') as f:
    sprite_pond, pond_config_opti = display.pre_optimise_img(load(f))        

with open("/img/Avignon/canon.json", 'r') as f:
    canon_sprite, canon_config_opti = display.pre_optimise_img(load(f))        
collect()



# /// Init Score Text ///
# HighScore
high_score = 0
with open('data/Avignon.txt', 'r') as f:
    high_score = int(f.read())
    f.close()


init_visual_projectile(display)
collect()
curr_time = 0
init_mark_on_screen()
collect()


# /// Game routine ///
while(started_game):

    mark_on_screen()

    # /////////////////////////////////////////////////////
    # Initialisation of variable
    # /////////////////////////////////////////////////////
        
    # life
    life = 3
    nb_screen_move = 0
    index_pond = 2

    bat_system = battement(nb_screen_move)
   
    # Init Player
    player_x = int(player_loc["x"]/2)
    player_y = player_loc["y"]-1
    player_x_old = player_x
    player_y_old = player_y

    # Score
    Score = 0
    is_use_jump = False
    last_speed_end = 0
    highscore_update(only_write = True)
    
    # Projectile
    list_projectile = []
    index_gen_projectile = 1
    last_gen_projectile = Projectile_creation_speed(nb_screen_move)
    init_projectile(display)
    
    # Pond
    pond_state = [2 for i in range(player_loc["y"])]
    for i in range(len(pond_state)):
        display.write_img_ram(sprite_pond[pond_state[i]+i*player_loc["x"]],
                              [pond_pos["x_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][0],
                               grid_multi["y"] * i+ pond_pos["y_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][1]] )

    display.write_img_ram(sprite_pond[len(pond_state)*player_loc["x"]],
                              [pond_pos["x_decal"] + pond_config_opti[len(pond_state)*player_loc["x"]][0],
                               len(pond_state)*grid_multi["y"]+ pond_pos["y_decal"] + pond_config_opti[len(pond_state)*player_loc["x"]][1]] )

    display.write_img_ram(canon_sprite[0],
                              [canon_pos["x"] + canon_config_opti[0][0],
                               canon_pos["y"] + canon_config_opti[0][1]] )

    last_change_pond = 10 # first on manual for show of player pond fall
    nb_pond_down = 0

    # other
    activ_mode = True
    last_time_input = last_time_input_init

    display.display_partial(only_black = True)
    display.go_in_lut_diff()
    display.disable_analog()

    update_input()
    while(button_left.value != 2 and button_right.value != 2):
        frame_past()
        update_input()
        
    buzzer(piezo_frequency["high"], [1])
    display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"]],
                          [pos_x_player(player_x)+player_config_opti[player_x + player_y*player_loc["x"]][0],
                           (player_y*grid_multi["y"]+ grid_multi["y_decal"])+player_config_opti[player_x + player_y*player_loc["x"]][1]],
                          ram_red_after_upd = True)
    add_score(0, only_write = True, ram_red_after_upd = True)
    display.display_diff()
    

    
    # ////////////////////////////////////////////////////////////////////////////
    # /// Game execution
    # ////////////////////////////////////////////////////////////////////////////
    while(life > 0):
        
        # /////////////////////
        # /// Player action ///
        # /////////////////////
        if(True):
        #////Player move
            update_input()
            
  
            # Left and right
            if button_up.value == 2:
                if(pond_state[player_y] == 0 and player_x == 1):
                    fall_on_pond()
                else:
                    player_y -= 1
                    if(player_x == 0):
                        player_x = 1
                        for i in range(0, len(list_projectile)):
                            if(list_projectile[i].is_same_pos(0, player_y+1)): # OUTCH
                                player_y += 1
                                collider_with_projectile(i)
                                break

                    last_time_input = last_time_input_init
                    buzzer(piezo_frequency["little_high"], [1])
                
            if button_down.value == 2:
                if(player_y != player_loc["y"]-1 and player_x == 1):
                    if(pond_state[player_y+1] == 0):
                        fall_on_pond(1)
                    else:
                        player_y += 1
                if(player_x == 0):
                    player_x = 1
                    for i in range(0, len(list_projectile)):
                        if(list_projectile[i].is_same_pos(0, player_y+1)): # OUTCH
                            player_y += 1
                            collider_with_projectile(i)
                            break

                last_time_input = last_time_input_init
                buzzer(piezo_frequency["little_high"], [1])

            # Jump
            if button_right.value == 2 or button_left.value == 2:

                if(player_x != 0): #Jumping
                    player_x -= 1
                    buzzer(piezo_frequency["high"], [1])
                    is_use_jump = is_use_jump & (pond_state[player_y] == 0 )
                else: # Fall
                    player_x += 1
                    player_y -= 1
                    buzzer(piezo_frequency["low"], [1])
                    for i in range(0, len(list_projectile)):
                        if(list_projectile[i].is_same_pos(player_x-1, player_y+1)): # OUTCH
                            player_y += 1
                            collider_with_projectile(i)
                            break

                last_time_input = last_time_input_init
            
            
            #//// Fall       
            last_time_input -= 1
            if(last_time_input <= 0):
                last_time_input = last_time_input_init
                if(player_x == 0):
                    player_x += 1
                    player_y -= 1

            
            # At end of Pond
            if(player_y < 0):
                
                nb_score_init = nb_score_sup(Score)
                
                nb_blink = 1
                score_to_add = score_end
                if(is_use_jump):
                    score_to_add += score_end_bonus_is_use_jump
                    nb_blink += 1
                if(last_speed_end <= speed_bonus_speed):
                    score_to_add += score_end_bonus_speed
                    nb_blink += 1
                is_use_jump = True
                last_speed_end = 0

                add_score(score_to_add, only_write = True, ram_red_after_upd = True, write_white_on_ram_before = True)
                
                mode_projectile_start = False
                for j in range(len(list_projectile)):
                    list_projectile[j].hidden_now(display, player_loc, ram_red_after_upd = True)
                    mode_projectile_start = mode_projectile_start | list_projectile[j].start_mode()
                if(mode_projectile_start == False):
                    hidden_projectile_hidden(display, True)

                display.delete_and_update_img_screen(
                    player_sprite[player_x_old + player_y_old*player_loc["x"]],
                        [pos_x_player(player_x_old)+player_config_opti[player_x_old + player_y_old*player_loc["x"]][0],
                         player_y_old*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x_old + player_y_old*player_loc["x"]][1]],
                    player_sprite[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1],
                        [Player_pos_end["x"]+player_config_opti[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1][0],
                         Player_pos_end["y"]+player_config_opti[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1][1]]) # , already_lut = True
                
                # freeze and player blinking
                buzzer(piezo_frequency["high"], [4 for i in range(nb_blink)])
                
                # Loss life because score is up on specify value         
                if(life != 3 and nb_score_init != nb_score_sup(Score)):
                    buzzer(piezo_frequency["little_high"], [4 for i in range(3)])
                    last_blink = speed_blink
                    while(last_blink > 0):
                        last_blink -= 1
                        frame_past()
                    display.update_img_screen(life_sprite[0], life_position(3-life-1), erase = True)
                    life += 1
                    last_blink = speed_blink*4
                    while(last_blink > 0):
                        last_blink -= 1
                        frame_past()

                mark_on_screen()                
                bat_system.time_bat_conf(nb_screen_move)

                for i in range(len(pond_state)):
                    display.write_img_ram(sprite_pond[pond_state[i]+i*player_loc["x"]],
                              [pond_pos["x_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][0],
                               grid_multi["y"] * i+ pond_pos["y_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][1]] )
                display.write_img_ram(sprite_pond[len(pond_state)*player_loc["x"]],
                              [pond_pos["x_decal"] + pond_config_opti[len(pond_state)*player_loc["x"]][0],
                               len(pond_state)*grid_multi["y"]+ pond_pos["y_decal"] + pond_config_opti[len(pond_state)*player_loc["x"]][1]] )

                display.write_img_ram(canon_sprite[0],
                              [canon_pos["x"] + canon_config_opti[0][0],
                               canon_pos["y"] + canon_config_opti[0][1]] )
                
                player_y = player_loc["y"]-1
                player_x = 1
                player_x_old = player_x
                player_y_old = player_y
                
                display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"]],
                                      [pos_x_player(player_x)+player_config_opti[player_x + player_y*player_loc["x"]][0],
                                       (player_y*grid_multi["y"]+ grid_multi["y_decal"])+player_config_opti[player_x + player_y*player_loc["x"]][1]])
                add_score(0, only_write = True)

                if(mode_projectile_start == False):
                    hidden_projectile_hidden(display, erase = False, ram_red_after_upd = False)
                for j in range(len(list_projectile)):
                    list_projectile[j].hidden_now(display, player_loc, erase = False, ram_red_after_upd = False)
                for j in range(3-life):
                    display.write_img_ram(life_sprite[0], life_position(j))

                display.display_partial(only_black = True)
                display.go_in_lut_diff()

                nb_screen_move += 1
                

      #//// Move visual Sprite
            if(player_x != player_x_old or player_y != player_y_old):
                display.delete_and_update_img_screen(player_sprite[player_x_old + player_y_old*player_loc["x"]],
                                                         [pos_x_player(player_x_old)+player_config_opti[player_x_old + player_y_old*player_loc["x"]][0],
                                                          player_y_old*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x_old + player_y_old*player_loc["x"]][1]],
                                                     player_sprite[player_x + player_y*player_loc["x"]],
                                                         [pos_x_player(player_x)+player_config_opti[player_x + player_y*player_loc["x"]][0],
                                                          player_y*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][1]] , already_lut = True)
                player_x_old = player_x
                player_y_old = player_y
      
      #////Projectile
            # Generate Projectile
            v_is_moving = False
            # Projectile verification (Move + delete + collider player)
            i = 0
            while i < len(list_projectile):
                v_is_same_pos = list_projectile[i].is_same_pos(player_x, player_y)
                v_is_moving = v_is_moving | list_projectile[i].verify_move_down(display, player_loc, bat_system)
                if(v_is_same_pos and v_is_moving): # OUTCH
                    collider_with_projectile(i)
                elif(list_projectile[i].flag_destroy): # destroy
                    list_projectile[i].destroy(display, player_loc)
                    list_projectile.pop(i)
                else:
                    i += 1    
    
                    
            last_gen_projectile -= 1
            if(last_gen_projectile <= 0 and can_create_projectile() and bat_system.new_index and len(list_projectile) < 2 ):
                new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now)
                index_gen_projectile += 1
                last_gen_projectile = Projectile_creation_speed(nb_screen_move) #index_gen_projectile
                list_projectile.append(new_proj)
                v_is_moving = True
               
               
           #//// Pond
            last_change_pond -= 1
            if(bat_system.new_index and bat_system.index_now == 0):
                # Change State of Pond
                for i in range(len(pond_state)):
                    if(pond_state[i] == 1): # Indication
                        display.write_img_ram(sprite_pond[pond_state[i]+i*player_loc["x"]],
                              [pond_pos["x_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][0],
                               grid_multi["y"] * i+ pond_pos["y_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][1]],
                                          erase = True, ram_red_after_upd = True)
                        pond_state[i] = 0
                        display.write_img_ram(sprite_pond[pond_state[i]+i*player_loc["x"]],
                              [pond_pos["x_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][0],
                               grid_multi["y"] * i+ pond_pos["y_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][1]] ,
                                              ram_red_after_upd = True)
                        v_is_moving = True

                # New fall of Pond
                if(last_change_pond <= 0):
                    # Choose if need to destroy or recreate
                    if(nb_pond_down < Pond_nb_down(nb_screen_move)):
                        mode_destroy = True
                        i_tmp = randrange(index_pond, 0, 3-nb_pond_down)
                    else:
                        mode_destroy = False
                        i_tmp = randrange(index_pond, 0, nb_pond_down)
                    # find pond choose random with good config
                    i = 0
                    for j in range(len(pond_state)-1):
                        if( (pond_state[j] == 2 and mode_destroy) or (pond_state[j] == 0 and mode_destroy == False )):
                            i+=1
                            if(i == i_tmp):
                                break
                    i = j
                    # Change visual pond
                    index_pond += 1
                    last_change_pond = Pond_changement_speed(nb_screen_move)
                    display.write_img_ram(sprite_pond[pond_state[i]+i*player_loc["x"]],
                                  [pond_pos["x_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][0],
                                   grid_multi["y"] * i+ pond_pos["y_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][1]],
                                          erase = True, ram_red_after_upd = True)
                    if(pond_state[i] == 2): # down
                                pond_state[i] = 1
                                nb_pond_down += 1
                    else: # reconstruct
                                pond_state[i] = 2
                                nb_pond_down -= 1
                    display.write_img_ram(sprite_pond[pond_state[i]+i*player_loc["x"]],
                              [pond_pos["x_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][0],
                               grid_multi["y"] * i+ pond_pos["y_decal"] + pond_config_opti[pond_state[i]+i*player_loc["x"]][1]],
                                              ram_red_after_upd = True )
                    v_is_moving = True
                        
            if(v_is_moving):
                display.display_diff()
                
                
                
        # ////////////////////
        # /// Blink player ///
        # ////////////////////
        else :
            a = 0
            
        last_speed_end += 1
        frame_past()



    # /////////////////
    # /// Game Over ///
    # /////////////////

    # /// Blinking
    buzzer(piezo_frequency["low"], [6 for i in range(5)])
    display.update_img_screen(life_sprite[0], life_position(3-life-1))
    blink_function(wait_restart)  

    # /// HighScore Update and Save
    if(high_score < Score):
        high_score = Score
        highscore_update()
        try:
            with open('data/Avignon.txt', 'w') as f:
                f.write(str(high_score))
                f.close()
        except:
            print("Impossible to write in file")
    
    for j in range(0,len(list_projectile)):
        try:
            list_projectile[j].destroy(display, player_loc)
        except:
            print("etrange...")
            
    display.clean_screen(long = True)
    first_start = True


# ////////////////// DEBUG /////////////////////////////////////
mark_on_screen(True)
sleep(5)

# ////////////////// DEBUG /////////////////////////////////////                
