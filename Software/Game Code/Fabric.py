"""
© Anastase Valentin, 2024. All rights reserved.

This code is protected by copyright law. Unauthorized copying, distribution, or modification
of this code, in part or in whole, is strictly prohibited without prior written consent
from the copyright owner.
"""

""" Show my Itch.io page for see my other games ! https://retrovalou.itch.io """

from gc import mem_alloc, mem_free, collect

from time import sleep
from game_basic_fct import button_right, button_left, button_action, button_down, button_up, randrange, update_input, maj_buffer, buzzer
from Fabric_game_class import battement, projectile_mark, init_projectile, projectile, speed_fall, init_visual_projectile
from math import sin
from ssd1680_RV import display, size_number
from json import load
from utime import ticks_ms

def monotonic():
    return ticks_ms() / 1000

# ////////////////////////////////////////////////////////
# //// Parameter ////
# ////////////////////////////////////////////////////////

grid_multi = {"x_decal": -26, "y": 62-12, "y_decal" : 62-26}
grid_david = {"x": 96, "x_decal": 0, "y": 62-12, "y_decal" : 60-18}
grid_projectile_exploded = {"x": 40, "x_decal": 15-20, "y_decal" : 280}
grid_decors = {"x": 98, "x_decal": -18, "y": 62-12, "y_decal" : 72}

piezo_frequency = {"low": 240, "little_high": 400, "high": 480}

time_frame = 1/60
player_loc = {"x": 2, "y": 5}

gen_projectile_speed = 150
wait_reactivate = 60
wait_restart = 60+30+60
speed_blink = 6
wait_on_top = 9

Player_pos_end = {"x": 56, "y": 5}

score_pos = [8, 4]

nb_projectile_per_vague = 12

# Projectile generation
Projectile_gen_limit = {"min": 3, "max": 100}
Projectile_gen_increase = 1/35
Projectile_gen_random_power = 30
Projectile_gen_random_harmony = 1.4


# Score to add
score_end_vague = 5
score_get = 1
score_set = 2

score_end_bonus_speed = 2
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
        


def add_score(add, only_write = False, ram_red_after_upd = False, only_need = False, write_white_on_ram_before = False):
    global Score
    global display
    global score_pos
    # Only need Semble ne pas trop influencer la vitesse à cause de l'attente de analog ...
    
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
    return Projectile_gen_limit["min"] + (Projectile_gen_limit["max"]- Projectile_gen_limit["min"])/(1+x*Projectile_gen_increase) + Projectile_gen_random_power * sin(x * Projectile_gen_random_harmony)

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
    return [2 + (3-i-1)*16, 16]

first_start = True



def estimate_new_projectile_to_fall(destroy_pos = [-1, -1]):
    global david_index_proj
    global david_pos
    global list_projectile_get
    global list_projectile_set

    # List of projectile is empty
    if(len(list_projectile_get) == 0 and len(list_projectile_set) == 0):
        if(david_index_proj != -1): # david not invisible
            david_index_proj = -1
            display.write_img_ram(before_destroy_sprite[david_pos[0] + david_pos[1]*player_loc["x"]],
                                [david_pos[0]*grid_david["x"]-grid_david["x_decal"]+before_destroy_config_opti[david_pos[0] + david_pos[1]*player_loc["x"]][0],
                                 david_pos[1]*grid_david["y"]+ grid_david["y_decal"]+before_destroy_config_opti[david_pos[0] + david_pos[1]*player_loc["x"]][1]],
                                  erase = True, ram_red_after_upd = True)
            return True
        else:
            return False

    # find fall value of curr projectile we have choose for falling the first
    curr_value_fall = 8*64
    if(david_index_proj != -1 and destroy_pos != david_pos):
        i = 0
        if(david_pos[0] == 0): # is on get list
            while i < len(list_projectile_get) and david_index_proj != list_projectile_get[i].index_p:
                i+=1
            curr_value_fall = list_projectile_get[i].time_before_fall
        else: # is on set list
            while i < len(list_projectile_set) and david_index_proj != list_projectile_set[i].index_p:
                i+=1
            curr_value_fall = list_projectile_set[i].time_before_fall
    old_david_index_proj = david_index_proj
    old_david_pos = david_pos
    
    # find new projectile can fall
    for i in range(len(list_projectile_get)):
        if(curr_value_fall > list_projectile_get[i].time_before_fall):
            curr_value_fall = list_projectile_get[i].time_before_fall
            david_pos = [list_projectile_get[i].pos_x, list_projectile_get[i].pos_y]
            david_index_proj = list_projectile_get[i].index_p
    for i in range(len(list_projectile_set)):
        if(curr_value_fall > list_projectile_set[i].time_before_fall):
            curr_value_fall = list_projectile_set[i].time_before_fall
            david_pos = [list_projectile_set[i].pos_x, list_projectile_set[i].pos_y]
            david_index_proj = list_projectile_set[i].index_p

    # projectile fall first are change -> Update Visual
    if(david_index_proj != old_david_index_proj):
        # Destroy before if need
        if(old_david_index_proj != -1):
            display.write_img_ram(before_destroy_sprite[old_david_pos[0] + old_david_pos[1]*player_loc["x"]],
                                [old_david_pos[0]*grid_david["x"]-grid_david["x_decal"]+before_destroy_config_opti[old_david_pos[0] + old_david_pos[1]*player_loc["x"]][0],
                                 old_david_pos[1]*grid_david["y"]+ grid_david["y_decal"]+before_destroy_config_opti[old_david_pos[0] + old_david_pos[1]*player_loc["x"]][1]],
                                  erase = True, ram_red_after_upd = True)

        display.write_img_ram(before_destroy_sprite[david_pos[0] + david_pos[1]*player_loc["x"]],
                                [david_pos[0]*grid_david["x"]-grid_david["x_decal"]+before_destroy_config_opti[david_pos[0] + david_pos[1]*player_loc["x"]][0],
                                 david_pos[1]*grid_david["y"]+ grid_david["y_decal"]+before_destroy_config_opti[david_pos[0] + david_pos[1]*player_loc["x"]][1]],
                              erase = False, ram_red_after_upd = True)
        return True
    
    return False




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
    projectile_mark(player_loc, display)
    
    for i in range(3):
        display.write_img_ram(life_sprite[0], life_position(i), ram_now = False, ram_before = False)

    for i in range(2):
        display.write_img_ram(projectile_exploded_sprite[i],
                                          [grid_projectile_exploded["x"]*i-grid_projectile_exploded["x_decal"]+projectile_exploded_config_opti[i][0],
                                           grid_projectile_exploded["y_decal"] + projectile_exploded_config_opti[i][1]] , erase = False, ram_red_after_upd = True)

    for x in range(player_loc["x"]):
        for y in range(player_loc["y"]):
            display.write_img_ram(before_destroy_sprite[x + y*player_loc["x"]],
                                [x*grid_david["x"]-grid_david["x_decal"]+before_destroy_config_opti[x + y*player_loc["x"]][0],
                                 y*grid_david["y"]+ grid_david["y_decal"]+before_destroy_config_opti[x + y*player_loc["x"]][1]],
                                  ram_now = False, ram_before = False)
            for p in range(2):
                display.write_img_ram(player_sprite[x + y*player_loc["x"] + p*5*player_loc["x"]],
                                  [-grid_multi["x_decal"]+player_config_opti[x + y*player_loc["x"]+ p*5*player_loc["x"]][0],
                                   y*grid_multi["y"]+ grid_multi["y_decal"] + player_config_opti[x + y*player_loc["x"]+ p*5*player_loc["x"]][1]],
                                  ram_now = False, ram_before = False)
        collect()

        for y in range(player_loc["y"]):
            for x in range(player_loc["x"]):
                display.write_img_ram(decors_sprite, [x*grid_decors["x"]+grid_decors["x_decal"], y*grid_decors["y"]+ grid_decors["y_decal"]],
                                  ram_now = False, ram_before = False)
    
    # Problem memory -> Out of memory during process
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
        with open('data/Fabric.txt', 'w') as f:
            f.write(str(0))
            f.close()
    except:
        print("Impossible to write in file")


# /// Player just load sprite ///
with open("/img/fabric/escalator.json", 'r') as f:
    player_sprite, player_config_opti = display.pre_optimise_img(load(f))        

# /// Life ///
with open("/img/fabric/life.json", 'r') as f:
    life_sprite = load(f)
    
# /// david ///
with open("/img/fabric/before_destroy.json", 'r') as f:
    before_destroy_sprite, before_destroy_config_opti = display.pre_optimise_img(load(f))
    
# /// Projectile exploded ///
with open("/img/fabric/projectile_expoded.json", 'r') as f:
    projectile_exploded_sprite, projectile_exploded_config_opti = display.pre_optimise_img(load(f))        

# /// decors ///
with open("/img/fabric/decors.json", 'r') as f:
    decors_sprite = load(f)[0]

collect()


# /// Init Score Text ///
# HighScore
high_score = 0
with open('data/Fabric.txt', 'r') as f:
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
    
    # /////////////////////////////////////////////////////
    # Initialisation of variable
    # /////////////////////////////////////////////////////
        
    # life
    life = 3
        
    # Init Player
    player_x = 0
    player_y = player_loc["y"]-1
    player_x_old = player_x
    player_y_old = player_y
    player_has_p = 0
    player_has_p_old = player_has_p

    # Score
    Score = 0
    is_falling = False
    last_speed_end = 0
    highscore_update(only_write = True)
    nb_score_init = nb_score_sup(Score)
    
    # Projectile
    list_projectile_get = []
    list_projectile_set = []
    list_pos_projectile_get = [i for i in range(player_loc["y"])]
    list_pos_projectile_set = [i for i in range(player_loc["y"])]
    index_gen_projectile = 1
    last_gen_projectile = Projectile_creation_speed(index_gen_projectile)
    init_projectile(display)
    nb_projectile_current_vague = nb_projectile_per_vague
    david_index_proj = -1
    david_pos = [0, 0]
    
    bat_system = battement(int(index_gen_projectile/nb_projectile_per_vague))

    # other
    activ_mode = True
    
    for y in range(player_loc["y"]):
        for x in range(player_loc["x"]):
            display.write_img_ram(decors_sprite,
                                  [x*grid_decors["x"]+grid_decors["x_decal"],
                                   y*grid_decors["y"]+ grid_decors["y_decal"]])

    display.display_partial(only_black = True)
    display.go_in_lut_diff()
    display.disable_analog()

    button_action.update()
    while(button_action.value != 2):
        frame_past()
        button_action.update()
        
    buzzer(piezo_frequency["little_high"], [2])
    display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"]],
                          [-grid_multi["x_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][0],
                          player_y*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][1]],
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
            
            # Up
            if button_action.value == 2 :
                player_x = (player_x+1)%2
                buzzer(piezo_frequency["little_high"], [2])

            # Left and right
            if button_right.value == 2 or button_down.value == 2:
                if(player_y <player_loc["y"]-1):
                    player_y += 1
                    buzzer(piezo_frequency["little_high"], [4])

            if button_left.value == 2 or button_up.value == 2:
                if(player_y > 0):
                    player_y -= 1
                    buzzer(piezo_frequency["little_high"], [4])


            if(True): # s'execute à chaque boucle, à voir pour l'opti plus pour s'exécuter que quand ya besoin
                # get mode
                if(player_has_p == 0 and player_x == 0):
                    i = 0
                    while(i < len(list_projectile_get) and list_projectile_get[i].is_same_pos(player_x, player_y) == False ):
                        i += 1
                    if(i < len(list_projectile_get)):
                        buzzer(piezo_frequency["high"], [3])
                        p = list_projectile_get.pop(i)
                        list_pos_projectile_get.append(p.pos_y)
                        p.destroy(display, player_loc)
                        player_has_p = 1
                        estimate_new_projectile_to_fall([player_x, player_y])
                        add_score(score_get, only_write = True, ram_red_after_upd = True, only_need = True)

    
                # set mode
                if(player_has_p == 1 and player_x == 1):
                    i = 0
                    while(i < len(list_projectile_set) and list_projectile_set[i].is_same_pos(player_x, player_y) == False ):
                        i += 1
                    if(i < len(list_projectile_set)):
                        buzzer(piezo_frequency["high"], [3])
                        p = list_projectile_set.pop(i)
                        list_pos_projectile_set.append(p.pos_y)
                        p.destroy(display, player_loc)
                        player_has_p = 0
                        estimate_new_projectile_to_fall([player_x, player_y])
                        add_score(score_set, only_write = True, ram_red_after_upd = True, only_need = True)



      #//// Move visual Sprite
            if(player_x != player_x_old or player_y != player_y_old or player_has_p_old != player_has_p):
                # Verify if get or set projectile on pos
                display.delete_and_update_img_screen(player_sprite[player_x_old + player_y_old*player_loc["x"] + player_has_p_old*5*player_loc["x"]],
                                                         [-grid_multi["x_decal"]+player_config_opti[player_x_old + player_y_old*player_loc["x"] + player_has_p_old*5*player_loc["x"]][0],
                                                          player_y_old*grid_multi["y"]+ grid_multi["y_decal"] + player_config_opti[player_x_old + player_y_old*player_loc["x"] + player_has_p_old*5*player_loc["x"]][1]],
                                                     player_sprite[player_x + player_y*player_loc["x"] + player_has_p*5*player_loc["x"]],
                                                         [-grid_multi["x_decal"]+player_config_opti[player_x + player_y*player_loc["x"]+ player_has_p*5*player_loc["x"]][0],
                                                          player_y*grid_multi["y"]+ grid_multi["y_decal"] + player_config_opti[player_x + player_y*player_loc["x"]+ player_has_p*5*player_loc["x"]][1]] , already_lut = True)
                player_x_old = player_x
                player_y_old = player_y
                player_has_p_old = player_has_p

         
     #////Projectile
            v_is_moving = False
  
            # Generate Projectile
            last_gen_projectile -= 1
            if(last_gen_projectile <= 0 and bat_system.new_index and len(list_projectile_get) < player_loc["y"] and len(list_projectile_set) < player_loc["y"] and nb_projectile_current_vague > 0):
                # get
                i = min(randrange(index_gen_projectile, 0, len(list_pos_projectile_get)-1), len(list_pos_projectile_get)-1)
                pos = [0, list_pos_projectile_get.pop(i)]
                new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now, pos)
                index_gen_projectile += 1
                list_projectile_get.append(new_proj)

                i = min(randrange(index_gen_projectile, 0, len(list_pos_projectile_set)-1), len(list_pos_projectile_set)-1)
                pos = [1, list_pos_projectile_set.pop(i)]
                new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now, pos)
                index_gen_projectile += 1
                list_projectile_set.append(new_proj)

                nb_projectile_current_vague -= 1
                last_gen_projectile = Projectile_creation_speed(index_gen_projectile)
                 
                # find new projectile can fall
                estimate_new_projectile_to_fall()

                v_is_moving = True
                
            # check state of projetile
            lost_life = False
            ind_projectile_explosed = 0
            # get
            for i in range(len(list_projectile_get)):
                list_projectile_get[i].verify_move_down(display, player_loc, bat_system)
                if(list_projectile_get[i].time_before_fall <= 0):
                    lost_life = True
                    # visual projectile fail
                    p = list_projectile_get.pop(i)
                    p.destroy(display, player_loc)
                    ind_projectile_explosed = 0
                    break
            # Set
            for i in range(len(list_projectile_set)):
                list_projectile_set[i].verify_move_down(display, player_loc, bat_system)
                if(list_projectile_set[i].time_before_fall <= 0):
                    lost_life = True
                    # visual projectile fail
                    p = list_projectile_set.pop(i)
                    p.destroy(display, player_loc)
                    nb_projectile_current_vague += 1
                    ind_projectile_explosed = 1
                    break
                
            if(lost_life):
                last_blink = 0
                activ_mode = False
                life -= 1
                display.write_img_ram(projectile_exploded_sprite[ind_projectile_explosed],
                                          [grid_projectile_exploded["x"]*ind_projectile_explosed-grid_projectile_exploded["x_decal"]+projectile_exploded_config_opti[ind_projectile_explosed][0],
                                           grid_projectile_exploded["y_decal"] + projectile_exploded_config_opti[ind_projectile_explosed][1]] , erase = False, ram_red_after_upd = True)
                if(life > 0):
                    buzzer(piezo_frequency["low"], [6 for i in range(2)])
                    display.update_img_screen(life_sprite[0], life_position(3-life-1), erase = False)
                    blink_function(wait_reactivate)
                    v_is_moving = False
                    for j in range(len(list_projectile_get)):
                        list_projectile_get[j].destroy(display, player_loc)
                    for j in range(len(list_projectile_set)):
                        list_projectile_set[j].destroy(display, player_loc)
                        nb_projectile_current_vague += 1
                    list_projectile_set = []
                    list_projectile_get = []
                    list_pos_projectile_get = [i for i in range(player_loc["y"])]
                    list_pos_projectile_set = [i for i in range(player_loc["y"])]
                    if(player_has_p == 1):
                        player_has_p = 0
                        display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"] + 1*5*player_loc["x"]],
                                                         [-grid_multi["x_decal"]+player_config_opti[player_x + player_y*player_loc["x"]+ 1*5*player_loc["x"]][0],
                                                          player_y*grid_multi["y"]+ grid_multi["y_decal"] + player_config_opti[player_x + player_y*player_loc["x"]+ 1*5*player_loc["x"]][1]] , erase = True, ram_red_after_upd = True)
                        display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"] + player_has_p*5*player_loc["x"]],
                                                         [-grid_multi["x_decal"]+player_config_opti[player_x + player_y*player_loc["x"]+ player_has_p*5*player_loc["x"]][0],
                                                          player_y*grid_multi["y"]+ grid_multi["y_decal"] + player_config_opti[player_x + player_y*player_loc["x"]+ player_has_p*5*player_loc["x"]][1]] , erase = False, ram_red_after_upd = True)
                    display.write_img_ram(projectile_exploded_sprite[ind_projectile_explosed],
                                          [grid_projectile_exploded["x"]*ind_projectile_explosed-grid_projectile_exploded["x_decal"]+projectile_exploded_config_opti[ind_projectile_explosed][0],
                                           grid_projectile_exploded["y_decal"] + projectile_exploded_config_opti[ind_projectile_explosed][1]] , erase = True, ram_red_after_upd = True)
                    estimate_new_projectile_to_fall()
                    v_is_moving = True
                    
                    
                
            # Need to update screen
            if(v_is_moving):
                display.display_diff()


            # END OF VAGUE
            if(nb_projectile_current_vague <= 0 and len(list_projectile_get) <= 0 and len(list_projectile_set) <= 0):
                
                add_score(score_end_vague, only_write = True, ram_red_after_upd = True, write_white_on_ram_before = True)
                buzzer(piezo_frequency["high"], [4 for i in range(3)])
                nb_projectile_current_vague = nb_projectile_per_vague
                display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"]],
                                      [-grid_multi["x_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][0],
                                      player_y*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][1]],
                                      erase = True, ram_now = False)
                display.display_diff()

                # Loss life because score is up on specify value         
                if(life != 3 and nb_score_init != nb_score_sup(Score)):
                    buzzer(piezo_frequency["little_high"], [6 for i in range(3)])
                    #list_visual_life[life].hidden = True
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

                display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"]],
                                                         [-grid_multi["x_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][0],
                                                          player_y*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][1]])
                add_score(0, only_write = True)
                
                for y in range(player_loc["y"]):
                    for x in range(player_loc["x"]):
                        display.write_img_ram(decors_sprite, [x*grid_decors["x"]+grid_decors["x_decal"], y*grid_decors["y"]+ grid_decors["y_decal"]])

                display.display_partial(only_black = True)
                display.go_in_lut_diff()

              

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
            with open('data/Fabric.txt', 'w') as f:
                f.write(str(high_score))
                f.close()
        except:
            print("Impossible to write in file")
    
    for j in range(len(list_projectile_get)):
        p = list_projectile_get.pop(0)
        p.destroy(display, player_loc)
    for j in range(len(list_projectile_set)):
        p = list_projectile_set.pop(0)
        p.destroy(display, player_loc)
            
    display.clean_screen(long = True)
    first_start = True


# ////////////////// DEBUG /////////////////////////////////////                
mark_on_screen(True)

sleep(5)

# ////////////////// DEBUG /////////////////////////////////////                
 