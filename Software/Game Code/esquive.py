"""
© Anastase Valentin, 2024. All rights reserved.

This code is protected by copyright law. Unauthorized copying, distribution, or modification
of this code, in part or in whole, is strictly prohibited without prior written consent
from the copyright owner.
"""

""" Show my Itch.io page for see my other games ! https://retrovalou.itch.io """


from gc import mem_alloc, mem_free, collect
#print(f"Before Export Memory: {mem_alloc()} of {mem_free()} bytes used.")

from time import sleep
from game_basic_fct import button_action, button_right, button_left, button_up, button_down, randrange, update_input, maj_buffer, buzzer
from esquive_game_class import battement, projectile_mark, init_projectile, projectile, speed_fall, grid_multi, init_visual_projectile, can_create_projectile
from math import sin
from ssd1680_RV import display
from json import load
from utime import ticks_ms

def monotonic():
    return ticks_ms() / 1000

# ////////////////////////////////////////////////////////
# //// Parameter ////
# ////////////////////////////////////////////////////////

piezo_frequency = {"low": 240, "little_high": 400, "high": 480}

time_frame = 1/60
player_loc = {"x": 3, "y": 4}

gen_projectile_speed = 150
wait_reactivate = 60
wait_restart = 60+30+60
speed_blink = 6
wait_on_top = 9


grid_multi = {"x": 36, "x_decal": 12, "y": 62-10, "y_decal" : 62+16+16-4}
Player_pos_end = {"x": 20, "y": -16}
David_pos = {"x": 36, "x_decal": -10, "y_decal" : 58-4}
bordure_pos = {"x": 4, "y" : 60}

score_pos = [114, 64]


# size image
image_size = { "height" : 60, "width" :60 }

# Projectile generation
Projectile_gen_limit = {"min": 0, "max": 120}
Projectile_gen_increase = 1/40
Projectile_gen_random_power = 15
Projectile_gen_random_harmony = 1.4
nb_Projectile_gen_limit = {"min": 4, "max": -1}
nb_Projectile_gen_increase = 1/50
nb_Projectile_gen_random_power = 1.1
max_projectile_simultanee = 7
index_screen_moving = 0

# Score to add
score_end = 5
score_end_bonus_speed = 2
score_end_bonus_no_back = 2
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
    global index_screen_moving
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
        last_time_input = speed_fall(index_screen_moving)



def add_score(add, only_write = False, ram_red_after_upd = False, write_white_on_ram_before = False):
    global Score
    global display
    global score_pos
    Score += add
    Score_text = str(Score)
    for i in range(len(Score_text), 4):
        Score_text = "0" + Score_text
    display.write_number(Score_text, score_pos, inverse = True, erase_before = True, already_lut = True, only_write = only_write, ram_red_after_upd = ram_red_after_upd, write_white_on_ram_before = write_white_on_ram_before)
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


def Projectile_nb_create(x):
    return max(min(nb_Projectile_gen_limit["min"] + (nb_Projectile_gen_limit["max"]- nb_Projectile_gen_limit["min"])/(1+x*nb_Projectile_gen_increase) + nb_Projectile_gen_random_power * sin(x * Projectile_gen_random_harmony), 2), 1) 


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
    return [106, (i)*18+4]

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
        for y in range(player_loc["y"]):
            pos_original = [((x*grid_multi["x"])-grid_multi["x_decal"]), (y*grid_multi["y"]+ grid_multi["y_decal"])] #+ grid_multi["x_decal"]-30
            display.write_img_ram(player_sprite[x + y*player_loc["x"]],
                                  [pos_original[0] + player_config_opti[x + y*player_loc["x"]][0],
                                   pos_original[1] + player_config_opti[x + y*player_loc["x"]][1]],
                                  ram_now = False, ram_before = False)
        collect()
    display.write_img_ram(player_sprite[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1],
                          [Player_pos_end["x"] + player_config_opti[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1][0],
                           Player_pos_end["y"]+ player_config_opti[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1][1]],
                            ram_now = False, ram_before = False)

    for David_x in range(player_loc["x"]):
        display.write_img_ram(David_sprite[David_x],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_config_opti[David_x][0],
                                       (David_pos["y_decal"])+David_config_opti[David_x][1]])
        for i in range(2):
            display.write_img_ram(David_help_sprite[David_x+player_loc["x"]*i],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_help_config_opti[David_x+player_loc["x"]*i][0],
                                       (David_pos["y_decal"])+David_help_config_opti[David_x+player_loc["x"]*i][1]])


    projectile_mark(player_loc, display)
    for i in range(3):
        display.write_img_ram(life_sprite[0], life_position(i), ram_now = False, ram_before = False)
        
    display.write_img_ram(bordure_sprite, [bordure_pos["x"],  bordure_pos["y"]], ram_now = False, ram_before = False)
    
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
        with open('data/esquive.txt', 'w') as f:
            f.write(str(0))
            f.close()
    except:
        print("Impossible to write in file")


# /// Player just load sprite ///
with open("/img/esquive/guy_multi.json", 'r') as f:
    player_sprite, player_config_opti = display.pre_optimise_img(load(f)[:-2])        

# /// Life ///
with open("/img/esquive/life.json", 'r') as f:
    life_sprite = load(f)       

# /// David ///
with open("/img/esquive/David.json", 'r') as f:
    David_sprite, David_config_opti = display.pre_optimise_img(load(f))
with open("/img/esquive/David_help.json", 'r') as f:
    David_help_sprite, David_help_config_opti = display.pre_optimise_img(load(f))
    
with open("/img/esquive/bordure.json", 'r') as f:
    bordure_sprite = load(f)[0]
    
collect()



# /// Init Score Text ///
# HighScore
high_score = 0
with open('data/esquive.txt', 'r') as f:
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

    index_screen_moving = 1
    
    bat_system = battement(index_screen_moving)
        
    # Init Player
    player_x = int(player_loc["x"]/2)
    player_y = player_loc["y"]-1
    player_x_old = player_x
    player_y_old = player_y
    max_up = player_y

    # init david
    David_x = randrange(index_screen_moving*1.2+6, 0, player_loc["x"]-1)
    David_state = 0
    display.write_img_ram(David_sprite[David_x],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_config_opti[David_x][0],
                                       (David_pos["y_decal"])+David_config_opti[David_x][1]])
    
    display.write_img_ram(bordure_sprite, [bordure_pos["x"],  bordure_pos["y"]])

    # Score
    Score = 0
    is_back = False
    last_speed_end = 0
    highscore_update(only_write = True)
    
    # Projectile
    list_projectile = []
    index_gen_projectile = 1
    last_gen_projectile = Projectile_creation_speed(index_gen_projectile)
    init_projectile(display)

    # other
    activ_mode = True
    last_time_input = speed_fall(index_screen_moving)

    display.display_partial(only_black = True)
    display.go_in_lut_diff()
    display.disable_analog()


    button_left.update()
    button_right.update()

    while(button_left.value != 2 and button_right.value != 2):
        frame_past()
        button_left.update()
        button_right.update()

    buzzer(piezo_frequency["high"], [2])
    display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"]],
                          [((player_x*grid_multi["x"])-grid_multi["x_decal"])+player_config_opti[player_x + player_y*player_loc["x"]][0],
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
            
            # Up
            if button_up.value == 2:
                last_time_input = speed_fall(index_screen_moving)
                # check projectile collider
                for i in range(0, len(list_projectile)):
                    if(list_projectile[i].is_same_pos(player_x, player_y)): # OUTCH
                        collider_with_projectile(i)
                        player_y += 1
                        break
                player_y -= 1
                if(player_y < 0 and David_x != player_x): # Not on david -> Not get it
                    player_y = 0
                else:
                    buzzer(piezo_frequency["little_high"], [2])


                
            # Down
            if button_down.value == 2:
                last_time_input = speed_fall(index_screen_moving)
                player_y = player_y + min(1, player_loc["y"]-player_y-1)            
                # check projectile collider
                for i in range(0, len(list_projectile)):
                    if(list_projectile[i].is_same_pos(player_x, player_y)): # OUTCH
                        collider_with_projectile(i)
                        break
                is_back = True
                buzzer(piezo_frequency["little_high"], [2])
                
            # right
            if button_right.value == 2:
                last_time_input = speed_fall(index_screen_moving)
                player_x = player_x - min(1, player_x)
                buzzer(piezo_frequency["high"], [2])

            # left
            if button_left.value == 2:
                last_time_input = speed_fall(index_screen_moving)
                player_x = player_x + min(1, player_loc["x"]-player_x-1)
                buzzer(piezo_frequency["high"], [2])

       #////Player at end 
            if(player_y < 0):
                nb_score_init = nb_score_sup(Score)

                nb_blink = 1
                score_to_add = score_end
                if(is_back == False):
                    score_to_add += score_end_bonus_no_back
                    nb_blink += 1
                if(last_speed_end <= speed_bonus_speed):
                    score_to_add += score_end_bonus_speed
                    nb_blink += 1
                last_speed_end = 0
                is_back = False
                
                add_score(score_to_add, only_write = True, ram_red_after_upd = True, write_white_on_ram_before = True)
                for i in range(len(list_projectile)):
                    list_projectile[i].hidden_now(display, player_loc, ram_red_after_upd = True)
                    
                display.write_img_ram(David_sprite[David_x],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_config_opti[David_x][0],
                                       (David_pos["y_decal"])+David_config_opti[David_x][1]], erase = True, ram_red_after_upd = True)
                display.write_img_ram(bordure_sprite, [bordure_pos["x"],  bordure_pos["y"]], erase = True, ram_red_after_upd = True)

                display.delete_and_update_img_screen(player_sprite[player_x_old + player_y_old*player_loc["x"]],
                        [player_x_old*grid_multi["x"]-grid_multi["x_decal"]+player_config_opti[player_x_old + player_y_old*player_loc["x"]][0],
                         player_y_old*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x_old + player_y_old*player_loc["x"]][1]],
                    player_sprite[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1],
                        [Player_pos_end["x"]+player_config_opti[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1][0],
                         Player_pos_end["y"]+player_config_opti[(player_loc["x"]-1) + (player_loc["y"]-1)*player_loc["x"]+1][1]])
                
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
                collect()
                
                player_y = player_loc["y"]-1
                player_x = int(player_loc["x"]/2)

                player_x_old = player_x
                player_y_old = player_y

                display.write_img_ram(player_sprite[player_x + player_y*player_loc["x"]],
                                      [((player_x*grid_multi["x"])-grid_multi["x_decal"])+player_config_opti[player_x + player_y*player_loc["x"]][0],
                                       (player_y*grid_multi["y"]+ grid_multi["y_decal"])+player_config_opti[player_x + player_y*player_loc["x"]][1]])
                add_score(0, only_write = True)
                
                for i in range(len(list_projectile)):
                    list_projectile[i].hidden_now(display, player_loc, erase = False, ram_red_after_upd = False)
                for i in range(3-life):
                    display.write_img_ram(life_sprite[0], life_position(i))
                
                index_screen_moving += 1
                
                # init david
                David_x = randrange(index_screen_moving*1.2+6, 0, player_loc["x"]-1)
                David_state = 0
                display.write_img_ram(David_sprite[David_x],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_config_opti[David_x][0],
                                       (David_pos["y_decal"])+David_config_opti[David_x][1]], erase = False, ram_red_after_upd = False)
                display.write_img_ram(bordure_sprite, [bordure_pos["x"],  bordure_pos["y"]], ram_red_after_upd = False)

                display.display_partial(only_black = True)
                display.go_in_lut_diff()




            
      #//// Move visual Sprite
            if(player_x != player_x_old or player_y != player_y_old):
                display.write_img_ram(David_help_sprite[David_x+player_loc["x"]*David_state],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_help_config_opti[David_x+player_loc["x"]*David_state][0],
                                       (David_pos["y_decal"])+David_help_config_opti[David_x+player_loc["x"]*David_state][1]], erase = True, ram_red_after_upd = True)
                David_state = (David_state +1)%2
                display.write_img_ram(David_help_sprite[David_x+player_loc["x"]*David_state],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_help_config_opti[David_x+player_loc["x"]*David_state][0],
                                       (David_pos["y_decal"])+David_help_config_opti[David_x+player_loc["x"]*David_state][1]], erase = False, ram_red_after_upd = True)
                display.delete_and_update_img_screen(player_sprite[player_x_old + player_y_old*player_loc["x"]],
                                                         [player_x_old*grid_multi["x"]-grid_multi["x_decal"]+player_config_opti[player_x_old + player_y_old*player_loc["x"]][0],
                                                          player_y_old*grid_multi["y"]+ grid_multi["y_decal"]+player_config_opti[player_x_old + player_y_old*player_loc["x"]][1]],
                                                     player_sprite[player_x + player_y*player_loc["x"]],
                                                         [player_x*grid_multi["x"]-grid_multi["x_decal"]+player_config_opti[player_x + player_y*player_loc["x"]][0],
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
                if(list_projectile[i].flag_destroy): # destroy
                    list_projectile[i].destroy(display, player_loc)
                    list_projectile.pop(i)
                elif(v_is_same_pos and v_is_moving): # OUTCH
                    collider_with_projectile(i)
                else:
                    i += 1    
                    
            last_gen_projectile -= 1
            if(last_gen_projectile <= 0 and can_create_projectile() and bat_system.new_index and len(list_projectile) < max_projectile_simultanee ):
                nb_generate = min(Projectile_nb_create(index_gen_projectile),
                                      max_projectile_simultanee - len(list_projectile))
                if(nb_generate == 1): # 1 projectile to generate -> Random Pos
                    new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now)
                    index_gen_projectile += 1
                    last_gen_projectile = Projectile_creation_speed(index_screen_moving) #index_gen_projectile
                    list_projectile.append(new_proj)
                else: # nb_generate == 2
                    # first -> Random pos
                    new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now)
                    index_gen_projectile += 1
                    last_gen_projectile = Projectile_creation_speed(index_screen_moving) #index_gen_projectile
                    list_projectile.append(new_proj)
                    # Second -> right pos to first
                    x_p = (new_proj.pos_x+1)%player_loc["x"]
                    new_proj = projectile(display, player_loc, index_gen_projectile, bat_system.index_now, force_x = x_p)
                    index_gen_projectile += 1
                    last_gen_projectile = Projectile_creation_speed(index_screen_moving) #index_gen_projectile
                    list_projectile.append(new_proj)

                
                v_is_moving = True
                
            if(v_is_moving):
                display.write_img_ram(David_help_sprite[David_x+player_loc["x"]*David_state],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_help_config_opti[David_x+player_loc["x"]*David_state][0],
                                       (David_pos["y_decal"])+David_help_config_opti[David_x+player_loc["x"]*David_state][1]], erase = True, ram_red_after_upd = True)
                David_state = (David_state +1)%2
                display.write_img_ram(David_help_sprite[David_x+player_loc["x"]*David_state],
                                    [(David_x*David_pos["x"]+ David_pos["x_decal"])+David_help_config_opti[David_x+player_loc["x"]*David_state][0],
                                       (David_pos["y_decal"])+David_help_config_opti[David_x+player_loc["x"]*David_state][1]], erase = False, ram_red_after_upd = True)
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
            with open('data/esquive.txt', 'w') as f:
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
 