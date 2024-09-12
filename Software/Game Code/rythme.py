"""
© Anastase Valentin, 2024. All rights reserved.

This code is protected by copyright law. Unauthorized copying, distribution, or modification
of this code, in part or in whole, is strictly prohibited without prior written consent
from the copyright owner.
"""

""" Show my Itch.io page for see my other games ! https://retrovalou.itch.io """


from gc import mem_alloc, mem_free, collect

from time import sleep
from game_basic_fct import button_right, button_left, button_action, randrange, update_input, maj_buffer, buzzer
from rythme_game_class import battement, projectile_mark, init_projectile, projectile, speed_fall, grid_multi, init_visual_projectile
from math import sin
from ssd1680_RV import display, size_number
from json import load
from utime import ticks_ms

def monotonic():
    return ticks_ms() / 1000

# //// Parameter ////
piezo_frequency = {"low": 240, "more_little_high": 340, "little_high": 400, "high": 480}

time_frame = 1/60
player_loc = {"x": 3, "y": 3}

gen_projectile_speed = 150
wait_reactivate = 60
wait_restart = 60+30+60
speed_blink = 6
wait_on_top = 9

player_pos  = {"x": 44, "x_decal": 10, "y_decal" : 210}
protect_pos  = {"x": 44, "x_decal": 10, "y_decal" : 160, "y_up" : 40}
line_vertical_pos  = {"x": 44, "x_decal": 14+28, "y_decal" : 62}
line_horizontal_pos  = {"x": 44, "x_decal": 0, "y_decal" : 186}
david_dodo_pos  = {"x": 36, "y" : 273}
david_angry_pos  = {"x": 70 ,"y" : 260}

score_pos = [8, 4]

# Projectile generation
Projectile_gen_limit = {"min": -20, "max": 130}
Projectile_gen_increase = 1/50
Projectile_gen_random_power = 20
Projectile_gen_random_harmony = 1.4
index_gen_projectile = 0
nb_Projectile_gen_limit = {"min": 4, "max": -1}
nb_Projectile_gen_increase = 1/60
nb_Projectile_gen_random_power = 0.3
nb_max_total_projectile = 5 #6
nb_projectile_per_vague = 15

# Score to add
score_end = 2
score_end_multi_destroy = 3
score_end_vague = 5
scores_add_life = [200, 500, 1000, 2000, 4000]

# //// Function ////
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
    global index_gen_projectile
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



def add_score(add, only_write = False, ram_red_after_upd = False, only_need = False, write_white_on_ram_before = False):
    global Score
    global display
    global score_pos
    
    # text score before
    Score_text_b = str(Score)
    for i in range(len(Score_text_b), 4):
        Score_text_b = "0" + Score_text_b
    # text score now
    Score += add
    Score_text = str(Score)
    for i in range(len(Score_text), 4):
        Score_text = "0" + Score_text
       
    # Update all number
    if(not(only_need)):
        display.write_number(Score_text, score_pos,
                             erase_before = True, already_lut = True, only_write = only_write, ram_red_after_upd = ram_red_after_upd, write_white_on_ram_before = write_white_on_ram_before)
        return
    
    # Update only number need
    begin = 0
    while(begin < len(Score_text) and Score_text[begin] == Score_text_b[begin]):
        begin += 1
    end = len(Score_text)-1
    while(end >= begin and Score_text[end] == Score_text_b[end]):
        end -= 1
    display.write_number(Score_text[begin:end+1], [score_pos[0] + size_number*begin, score_pos[1]],
                             erase_before = True, already_lut = True, only_write = only_write, ram_red_after_upd = ram_red_after_upd, write_white_on_ram_before = write_white_on_ram_before)
    return



def highscore_update(only_write = False):
    global high_score
    global display
    global score_pos
    Score_text = str(high_score)
    for i in range(len(Score_text), 4):
        Score_text = "0" + Score_text
    display.write_number(Score_text, score_pos, erase_before = True, already_lut = True, only_write = only_write)
    return
    
    
def Projectile_creation_speed(x):
    global Projectile_gen_limit
    global Projectile_gen_increase
    global Projectile_gen_random_power
    global Projectile_gen_random_harmony
    return max(Projectile_gen_limit["min"] + (Projectile_gen_limit["max"]- Projectile_gen_limit["min"])/(1+x*Projectile_gen_increase) + Projectile_gen_random_power * sin(x * Projectile_gen_random_harmony), 0)


def Projectile_nb_create(x):
    return max(min(nb_Projectile_gen_limit["min"] + (nb_Projectile_gen_limit["max"]- nb_Projectile_gen_limit["min"])/(1+x*nb_Projectile_gen_increase) + nb_Projectile_gen_random_power * sin(x * Projectile_gen_random_harmony), 3), 1) 


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
    return [2 + (3-i-1)*18, 16]

first_start = True




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
    for x in range(player_loc["x"]):
        display.write_img_ram(player_sprite[x],
                                  [((x*player_pos["x"])-player_pos["x_decal"])+player_config_opti[x][0],
                                   (player_pos["y_decal"])+player_config_opti[x][1]],
                                  ram_now = False, ram_before = False)
        collect()
    projectile_mark(player_loc, display)
    for i in range(3):
        display.write_img_ram(life_sprite[0], life_position(i), ram_now = False, ram_before = False)
    collect()
    
    #Line for help visual
    for i in range(2):
        display.write_img_ram(line_sprite[0],
                              [line_vertical_pos["x"]*i + line_vertical_pos["x_decal"], line_vertical_pos["y_decal"]],
                              erase = False)
    collect()
    # line_horizontal 
    for i in range(3):
        display.write_img_ram(line_horizontal_sprite[0],
                              [((i*line_horizontal_pos["x"])-line_horizontal_pos["x_decal"]),
                               (line_horizontal_pos["y_decal"])],
                              erase = False)
    collect()                   
    # Button
    for x in range(player_loc["x"]):
        display.write_img_ram(button_sprite[x],
                                  [((x*player_pos["x"])-player_pos["x_decal"])+button_config_opti[x][0],
                                   (player_pos["y_decal"])+button_config_opti[x][1]],
                                  erase = False)
    collect()               
    # Tuyau up 
    for i in range(3):
        display.write_img_ram(tuyau_up_sprite[i],
                              [((i*protect_pos["x"])-protect_pos["x_decal"])+tuyau_up_config_opti[i][0],
                               (protect_pos["y_up"])+tuyau_up_config_opti[i][1]],
                              erase = False)
    collect()
    # David
    display.write_img_ram(david_dodo_sprite[2],
                          [david_dodo_pos["x"]+david_dodo_config_opti[2][0],
                           david_dodo_pos["y"]+david_dodo_config_opti[2][1]],
                              erase = False)
    
    display.write_img_ram(david_dodo_fix_sprite[0],
                          [david_dodo_pos["x"]+david_dodo_fix_config_opti[0][0],
                           david_dodo_pos["y"]+david_dodo_fix_config_opti[0][1]],
                              erase = False)
    
    display.write_img_ram(david_angry_sprite[0],
                          [david_angry_pos["x"]+david_angry_config_opti[0][0],
                           david_angry_pos["y"]+david_angry_config_opti[0][1]],
                              erase = False)
    collect()
    # Protect
    for a in range(2):
        for i in range(player_loc["x"]):
            ind = i + a*player_loc["x"]
            display.write_img_ram(
                protect_sprite[ind],
                [((i*protect_pos["x"])-protect_pos["x_decal"])+protect_config_opti[ind][0],
                   (protect_pos["y_decal"])+protect_config_opti[ind][1]]
                )
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

    
    
# /// Init global elem ///

# BUTTON UP FOR DEBLOCK WRITE MODE -> FOR SAVE DATA ON RASBERRY PI PICO
if(button_action.check_button_now() == False):
    started_game = True
else:
    started_game = False
    
     
# BUTTON LEFT AND RIGHT FOR INIT HIGH SCORE
if(button_left.check_button_now() and button_right.check_button_now() ):
    try:
        with open('data/rythme.txt', 'w') as f:
            f.write(str(0))
            f.close()
    except:
        print("Impossible to write in file")


# /// Player just load sprite ///
with open("/img/rythme/guy_multi.json", 'r') as f:
    player_sprite, player_config_opti = display.pre_optimise_img(load(f))        

with open("/img/rythme/protect_multi.json", 'r') as f:
   protect_sprite, protect_config_opti = display.pre_optimise_img(load(f))        

# /// Life ///
with open("/img/rythme/life.json", 'r') as f:
    life_sprite = load(f)       

# /// line ///
with open("/img/rythme/line.json", 'r') as f:
    line_sprite = load(f)
    
# /// line_horizontal ///
with open("/img/rythme/line_horizontal.json", 'r') as f:
    line_horizontal_sprite = load(f)       

# // Tuyau up
with open("/img/rythme/tuyau_up.json", 'r') as f:
   tuyau_up_sprite, tuyau_up_config_opti = display.pre_optimise_img(load(f))
   
# // button
with open("/img/rythme/button_multi.json", 'r') as f:
   button_sprite, button_config_opti = display.pre_optimise_img(load(f))
   
# // dodo_david
with open("/img/rythme/dodo_david.json", 'r') as f:
   david_dodo_sprite, david_dodo_config_opti = display.pre_optimise_img(load(f))
with open("/img/rythme/dodo_david_fix.json", 'r') as f:
   david_dodo_fix_sprite, david_dodo_fix_config_opti = display.pre_optimise_img(load(f))
   
# // dodo_david
with open("/img/rythme/david_angry.json", 'r') as f:
   david_angry_sprite, david_angry_config_opti = display.pre_optimise_img(load(f))        

collect()

# /// Init Score Text ///
high_score = 0
with open('data/rythme.txt', 'r') as f:
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
    collect()
    
    # Initialisation of variable
        
    # life
    life = 3
    
    # Line for help visual
    for i in range(2):
        display.write_img_ram(line_sprite[0],
                              [line_vertical_pos["x"]*i + line_vertical_pos["x_decal"], line_vertical_pos["y_decal"]],
                              erase = False)
        
    # line_horizontal 
    for i in range(3):
        display.write_img_ram(line_horizontal_sprite[0],
                              [((i*line_horizontal_pos["x"])-line_horizontal_pos["x_decal"]),
                               (line_horizontal_pos["y_decal"])],
                              erase = False)
     
    # Button
    for x in range(player_loc["x"]):
        display.write_img_ram(button_sprite[x],
                                  [((x*player_pos["x"])-player_pos["x_decal"])+button_config_opti[x][0],
                                   (player_pos["y_decal"])+button_config_opti[x][1]],
                                  erase = False)

    
    # Tuyau up 
    for i in range(3):
        display.write_img_ram(tuyau_up_sprite[i],
                              [((i*protect_pos["x"])-protect_pos["x_decal"])+tuyau_up_config_opti[i][0],
                               (protect_pos["y_up"])+tuyau_up_config_opti[i][1]],
                              erase = False)

    # Protect
    protect_state = [0 for i in range(player_loc["x"])]
    for i in range(len(protect_state)):
        ind = i + protect_state[i]*player_loc["x"]
        display.write_img_ram(
            protect_sprite[ind],
            [((i*protect_pos["x"])-protect_pos["x_decal"])+protect_config_opti[ind][0],
               (protect_pos["y_decal"])+protect_config_opti[ind][1]]
            )
    
    # David
    id_dodo = 0
    display.write_img_ram(david_dodo_sprite[id_dodo],
                          [david_dodo_pos["x"]+david_dodo_config_opti[id_dodo][0],
                           david_dodo_pos["y"]+david_dodo_config_opti[id_dodo][1]],
                              erase = False)
    
    display.write_img_ram(david_dodo_fix_sprite[0],
                          [david_dodo_pos["x"]+david_dodo_fix_config_opti[0][0],
                           david_dodo_pos["y"]+david_dodo_fix_config_opti[0][1]],
                              erase = False)
    
    bat_system = battement(int(index_gen_projectile/nb_projectile_per_vague))

    # Init Player
    player_x = int(player_loc["x"]/2)
    player_x_old = player_x

    # Score
    Score = 0
    is_falling = False
    last_speed_end = 0
    highscore_update(only_write = True)
    nb_score_init = nb_score_sup(Score)

    # Projectile
    list_projectile = []
    index_gen_projectile = 1
    last_gen_projectile = Projectile_creation_speed(index_gen_projectile)
    init_projectile(display)
    nb_projectile_current_vague = nb_projectile_per_vague

    # other
    activ_mode = True

    display.display_partial(only_black = True)
    display.go_in_lut_diff()
    display.disable_analog()

    #last_blink = 0
    button_action.update()
    while(button_action.value != 2):
        frame_past()
        button_action.update()
        
    buzzer(piezo_frequency["high"], [2])
    display.write_img_ram(player_sprite[player_x],
                          [((player_x*player_pos["x"])-player_pos["x_decal"])+player_config_opti[player_x][0],
                           (player_pos["y_decal"])+player_config_opti[player_x][1]], ram_red_after_upd = True)
    add_score(0, only_write = True, ram_red_after_upd = True)
    display.display_diff()
    
    # /// Game execution
    while(life > 0):
        
        # /// Player action ///
        if(True):
            update_input()
            
            if button_action.value == 2 :
                ind_before = player_x + protect_state[player_x]*player_loc["x"]
                protect_state[player_x] = (protect_state[player_x]+1)%2
                ind = player_x + protect_state[player_x]*player_loc["x"]
                display.delete_and_update_img_screen(
                    protect_sprite[ind_before],
                    [((player_x*protect_pos["x"])-protect_pos["x_decal"])+protect_config_opti[ind_before][0],
                    (protect_pos["y_decal"])+protect_config_opti[ind_before][1]],
                    protect_sprite[ind],
                    [((player_x*protect_pos["x"])-protect_pos["x_decal"])+protect_config_opti[ind][0],
                    (protect_pos["y_decal"])+protect_config_opti[ind][1]])
                if(protect_state[player_x] == 1):
                    buzzer(piezo_frequency["high"], [3])
                else :
                    buzzer(piezo_frequency["more_little_high"], [3])

            if button_right.value == 2:
                player_x = player_x - min(1, player_x)
                buzzer(piezo_frequency["little_high"], [1])

            if button_left.value == 2:
                player_x = player_x + min(1, player_loc["x"]-player_x-1)
                buzzer(piezo_frequency["little_high"], [1])

      #//// Move visual Sprite
            if(player_x != player_x_old):
                display.write_img_ram(david_dodo_sprite[id_dodo],
                          [david_dodo_pos["x"]+david_dodo_config_opti[id_dodo][0],
                           david_dodo_pos["y"]+david_dodo_config_opti[id_dodo][1]],
                              erase = True, ram_red_after_upd = True)
                id_dodo = (id_dodo+1)%len(david_dodo_sprite)
                display.write_img_ram(david_dodo_sprite[id_dodo],
                          [david_dodo_pos["x"]+david_dodo_config_opti[id_dodo][0],
                           david_dodo_pos["y"]+david_dodo_config_opti[id_dodo][1]],
                              erase = False, ram_red_after_upd = True)
                display.delete_and_update_img_screen(player_sprite[player_x_old],
                                                         [player_x_old*player_pos["x"]-player_pos["x_decal"]+player_config_opti[player_x_old][0],
                                                          player_pos["y_decal"]+player_config_opti[player_x_old][1]],
                                                     player_sprite[player_x],
                                                         [player_x*player_pos["x"]-player_pos["x_decal"]+player_config_opti[player_x][0],
                                                          player_pos["y_decal"]+player_config_opti[player_x ][1]] , already_lut = True)
                player_x_old = player_x
      
      #////Projectile
            v_is_moving = False
            # Projectile verification (Move + delete + collider player)
            nb_destroy_ok = 0
            i = 0
            while i < len(list_projectile):
                v_is_moving = v_is_moving | list_projectile[i].verify_move_down(display, player_loc, bat_system)
                if(list_projectile[i].flag_destroy): # destroy projectile -> at end
                    if(protect_state[list_projectile[i].pos_x] == list_projectile[i].color): # god color
                        list_projectile[i].destroy(display, player_loc)
                        list_projectile.pop(i)
                        nb_destroy_ok += 1
                    else: # not good color
                        # Destroy all projectile -> More easy to restart
                        for j in range(len(list_projectile)):
                            list_projectile[j].destroy(display, player_loc)
                            nb_projectile_current_vague += 1 # for not validate end of vague if destroy all by defeat
                        
                        list_projectile = []
                        nb_destroy_ok = 0
                        last_blink = 0
                        activ_mode = False
                        life -= 1
                        
                        # David
                        display.write_img_ram(david_dodo_fix_sprite[0],
                          [david_dodo_pos["x"]+david_dodo_fix_config_opti[0][0],
                           david_dodo_pos["y"]+david_dodo_fix_config_opti[0][1]],
                              erase = True, ram_red_after_upd = True)
                        display.write_img_ram(david_dodo_sprite[id_dodo],
                          [david_dodo_pos["x"]+david_dodo_config_opti[id_dodo][0],
                           david_dodo_pos["y"]+david_dodo_config_opti[id_dodo][1]],
                              erase = True, ram_red_after_upd = True)
                        display.write_img_ram(david_angry_sprite[0],
                          [david_angry_pos["x"]+david_angry_config_opti[0][0],
                           david_angry_pos["y"]+david_angry_config_opti[0][1]],
                              erase = False, ram_red_after_upd = True)

                        if(life > 0):
                            buzzer(piezo_frequency["low"], [6 for i in range(2)])
                            display.update_img_screen(life_sprite[0], life_position(3-life-1), erase = False)
                            blink_function(wait_reactivate)
                            v_is_moving = False
                            # David 
                            display.write_img_ram(david_dodo_sprite[id_dodo],
                                  [david_dodo_pos["x"]+david_dodo_config_opti[id_dodo][0],
                                   david_dodo_pos["y"]+david_dodo_config_opti[id_dodo][1]],
                                  erase = False, ram_red_after_upd = True)
                            display.write_img_ram(david_dodo_fix_sprite[0],
                                  [david_dodo_pos["x"]+david_dodo_fix_config_opti[0][0],
                                   david_dodo_pos["y"]+david_dodo_fix_config_opti[0][1]],
                                      erase = False, ram_red_after_upd = True)
                            display.write_img_ram(david_angry_sprite[0],
                                  [david_angry_pos["x"]+david_angry_config_opti[0][0],
                                   david_angry_pos["y"]+david_angry_config_opti[0][1]],
                                      erase = True, ram_red_after_upd = True)
                            display.display_diff()

                else:
                    i+=1
                    
            if(nb_destroy_ok != 0 and (nb_projectile_current_vague > 0 or len(list_projectile) > 0)):  # Projectile are destroy correctly
                buzzer(piezo_frequency["high"], [2 for i in range(nb_destroy_ok)])
                score_to_add = score_end
                for i in range(1, nb_destroy_ok):
                    score_to_add += score_end_multi_destroy
                add_score(score_to_add, only_write = True, ram_red_after_upd = True, only_need = True)


            # Generate Projectile
            last_gen_projectile -= 1
            if(life > 0 and last_gen_projectile <= 0
                       and bat_system.new_index and len(list_projectile) < nb_max_total_projectile
                       and nb_projectile_current_vague > 0):
                nb_generate = min(min(Projectile_nb_create(index_gen_projectile),
                                      nb_max_total_projectile - len(list_projectile)),
                                      nb_projectile_current_vague)
                if(nb_generate == 1): # 1 projectile to generate -> Random Pos
                    new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now)
                    index_gen_projectile += 1
                    last_gen_projectile = Projectile_creation_speed(index_gen_projectile)
                    list_projectile.append(new_proj)
                    nb_projectile_current_vague -= 1
                elif(nb_generate == player_loc["x"]): # normaly 3
                    for i in range(player_loc["x"]):
                        new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now, force_x = i)
                        index_gen_projectile += 1
                        last_gen_projectile = Projectile_creation_speed(index_gen_projectile)
                        list_projectile.append(new_proj)
                        nb_projectile_current_vague -= 1
                else: # nb_generate == 2
                    # first -> Random pos
                    new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now)
                    index_gen_projectile += 1
                    last_gen_projectile = Projectile_creation_speed(index_gen_projectile)
                    list_projectile.append(new_proj)
                    # Second -> right pos to first
                    x_p = (new_proj.pos_x+1)%player_loc["x"]
                    new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now, force_x = x_p)
                    index_gen_projectile += 1
                    last_gen_projectile = Projectile_creation_speed(index_gen_projectile)
                    list_projectile.append(new_proj)
                    nb_projectile_current_vague -= 2

                v_is_moving = True
            # Need to update screen
            if(v_is_moving and life > 0):
                display.display_diff()
               
               
            # END OF VAGUE
            if(nb_projectile_current_vague <= 0 and len(list_projectile) <= 0 and life > 0):
                
                add_score(score_end_vague,
                          only_write = True,
                          ram_red_after_upd = True, write_white_on_ram_before = True)
                display.write_img_ram(david_dodo_fix_sprite[0],
                          [david_dodo_pos["x"]+david_dodo_fix_config_opti[0][0],
                           david_dodo_pos["y"]+david_dodo_fix_config_opti[0][1]],
                           erase = True, ram_now = False)
                display.write_img_ram(player_sprite[player_x],
                                      [player_x*player_pos["x"]-player_pos["x_decal"]+player_config_opti[player_x][0],
                                      player_pos["y_decal"]+player_config_opti[player_x ][1]],
                                      erase = True, ram_now = False)
                display.display_diff()

                buzzer(piezo_frequency["high"], [4 for i in range(3)])
                nb_projectile_current_vague = nb_projectile_per_vague

                # Loss life because score is up on specify value         
                if(life != 3 and nb_score_init != nb_score_sup(Score)):
                    buzzer(piezo_frequency["little_high"], [6 for i in range(3)])
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
                nb_score_init = nb_score_sup(Score)
                
                mark_on_screen()                
                bat_system.time_bat_conf(int(index_gen_projectile/nb_projectile_per_vague))
                
                # rewrite image on RAM screen
                for j in range(3-life):
                    display.write_img_ram(life_sprite[0], life_position(j))
                
                #Line for help visual
                for i in range(2):
                    display.write_img_ram(line_sprite[0],
                              [line_vertical_pos["x"]*i + line_vertical_pos["x_decal"], line_vertical_pos["y_decal"]],
                              erase = False)
                # line_horizontal 
                for i in range(3):
                    display.write_img_ram(line_horizontal_sprite[0],
                              [((i*line_horizontal_pos["x"])-line_horizontal_pos["x_decal"]),
                               (line_horizontal_pos["y_decal"])],
                              erase = False)
                        
                # Button
                for x in range(player_loc["x"]):
                    display.write_img_ram(button_sprite[x],
                                  [((x*player_pos["x"])-player_pos["x_decal"])+button_config_opti[x][0],
                                   (player_pos["y_decal"])+button_config_opti[x][1]],
                                  erase = False)
                
                # Tuyau up 
                for i in range(3):
                    display.write_img_ram(tuyau_up_sprite[i],
                              [((i*protect_pos["x"])-protect_pos["x_decal"])+tuyau_up_config_opti[i][0],
                               (protect_pos["y_up"])+tuyau_up_config_opti[i][1]],
                              erase = False)

                # David 
                display.write_img_ram(david_dodo_sprite[id_dodo],
                          [david_dodo_pos["x"]+david_dodo_config_opti[id_dodo][0],
                           david_dodo_pos["y"]+david_dodo_config_opti[id_dodo][1]],
                              erase = False)
                display.write_img_ram(david_dodo_fix_sprite[0],
                          [david_dodo_pos["x"]+david_dodo_fix_config_opti[0][0],
                           david_dodo_pos["y"]+david_dodo_fix_config_opti[0][1]],
                              erase = False)
                    
                display.write_img_ram(player_sprite[player_x],
                                      [player_x*player_pos["x"]-player_pos["x_decal"]+player_config_opti[player_x][0],
                                      player_pos["y_decal"]+player_config_opti[player_x ][1]])
                for i in range(len(protect_state)):
                    ind = i + protect_state[i]*player_loc["x"]
                    display.write_img_ram( protect_sprite[ind],
                                            [((i*protect_pos["x"])-protect_pos["x_decal"])+protect_config_opti[ind][0],
                                               (protect_pos["y_decal"])+protect_config_opti[ind][1]])
                add_score(0, only_write = True)


                display.display_partial(only_black = True)
                display.go_in_lut_diff()

        else :
            a = 0
            
        last_speed_end += 1
        frame_past()



    # /// Game Over ///
    buzzer(piezo_frequency["low"], [6 for i in range(5)])
    display.update_img_screen(life_sprite[0], life_position(3-life-1))
    blink_function(wait_restart)  
    # /// HighScore Update and Save
    if(high_score < Score):
        high_score = Score
        highscore_update()
        try:
            with open('data/rythme.txt', 'w') as f:
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
