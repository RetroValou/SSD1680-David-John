"""
© Anastase Valentin, 2024. All rights reserved.

This code is protected by copyright law. Unauthorized copying, distribution, or modification
of this code, in part or in whole, is strictly prohibited without prior written consent
from the copyright owner.
"""

""" Show my Itch.io page for see my other games ! https://retrovalou.itch.io """


from game_basic_fct import randrange
from math import sin
from json import load
from gc import mem_alloc, mem_free, collect


grid_multi = {"x": 44, "x_decal": 10, "y": 44, "y_decal" : 66}
grid_multi_sp_projectile_before = {"x": 50, "x_decal": 20, "y": 60, "y_decal" : 64}

Projectile_speed_limit = {"min": 25, "max": 45}
Projectile_speed_increase = 1/30
Projectile_speed_random_power = 8
Projectile_speed_random_harmony = 1.2
Projectile_wait_before_move_limit = {"min": 35, "max": 60+20} 
Projectile_blink = 12
Projectile_pos_add = {"before_y":-38, "before_x":4, "y":-5}

speed_fall_limit = {"min": 40, "max": 70}

pos_projectile_before_hidden = [0, 28]

sprite_sheet_projectile = 0
sprite_sheet_projectile_before = 0
sprite_projectile_before_hidden = 0
projectile_before_hidden_config_opti = 0
projectile_before_config_opti = 0
projectile_config_opti = 0
nb_projectile_before = 0

projectile_force_screen = 5

min_t_wait = 25



def init_projectile(display):
    global nb_projectile_before
    global sprite_projectile_before_hidden
    global pos_projectile_before_hidden
    global projectile_before_hidden_config_opti
    nb_projectile_before = 0
    

def init_visual_projectile(display):
    global sprite_sheet_projectile
    global sprite_sheet_projectile_before
    global sprite_projectile_before_hidden
    global projectile_before_config_opti
    global projectile_before_hidden_config_opti
    global projectile_config_opti

    # /// Projectile ///
    with open("/img/rythme/projectile_multi.json", 'r') as f:
        sprite_sheet_projectile, projectile_config_opti = display.pre_optimise_img(load(f)) 


def Projectile_speed(x):
    global Projectile_speed_limit
    global Projectile_speed_increase
    global Projectile_speed_random_power
    global Projectile_speed_random_harmony
    return Projectile_speed_limit["min"] + (Projectile_speed_limit["max"]- Projectile_speed_limit["min"])/(1+x*Projectile_speed_increase) + Projectile_speed_random_power * sin(x * Projectile_speed_random_harmony)


def speed_fall(x): # indexer sur projectile généré
    global speed_fall_limit
    global Projectile_speed_increase
    return max(speed_fall_limit["min"], speed_fall_limit["min"] + (speed_fall_limit["max"]- speed_fall_limit["min"])/(1+x*Projectile_speed_increase))


def projectile_wait(x): # indexer sur projectile généré
    global speed_fall_limit
    global Projectile_speed_increase
    return max(Projectile_wait_before_move_limit["min"], Projectile_wait_before_move_limit["min"] + (Projectile_wait_before_move_limit["max"]- Projectile_wait_before_move_limit["min"])/(1+x*Projectile_speed_increase))



class battement:
    
    def __init__(self, t_table_transformed):
        self.time_wait_change = 0
        self.t_wait = 0
        self.time_bat_conf(t_table_transformed)
        self.index_now = 0
        self.time_wait_change = self.t_wait
        self.new_index = True
        
    def time_bat_conf(self, t_table_transformed):
        global min_t_wait
        self.time_wait_change -= self.t_wait
        self.nb_bat = max(int(Projectile_speed(t_table_transformed)/min_t_wait), 1)
        self.t_wait = max(int(Projectile_speed(t_table_transformed)/ self.nb_bat), min_t_wait)
        self.time_wait_change += self.t_wait

    def update(self):
        self.new_index = False
        self.time_wait_change -= 1
        if(self.time_wait_change <= 0):
            self.time_wait_change = self.t_wait
            self.index_now += 1
            if(self.index_now >= self.nb_bat):
                self.index_now = 0
            self.new_index = True
            return True
        return False

    def move_ok(self, index_test):
        return self.new_index and ((index_test == self.index_now) or ((index_test >= self.nb_bat) and (self.index_now == 0)))
           


class projectile:
    pos_x = 0
    pos_y = 0
    flag_destroy = False
    color = 0
    
    def __init__(self, display, player_loc, t, index_bat, force_x = -1):
        global sprite_sheet_projectile
        global projectile_config_opti
        global nb_projectile_before
        global grid_multi
        global Projectile_pos_add
        global projectile_force_screen
        
        nb_projectile_before += 1
        self.pos_y = 0
        if(force_x == -1 ):
            self.pos_x = randrange(t, 0, player_loc["x"] - 1)
        else:
            self.pos_x = force_x
        self.flag_destroy = False
        self.last_blink = 0
        self.curr_state = "down"
        self.index = index_bat
        self.color = randrange((t*3)+1, 0, 1)
        ind = self.pos_x + self.pos_y * player_loc["x"] *2 + self.color*player_loc["x"]
        display.write_img_ram(sprite_sheet_projectile[ind],
                              [self.pos_x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[ind][0],
                               self.pos_y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"] + projectile_config_opti[ind][1]],
                              erase = False, ram_red_after_upd = True)

        
    def destroy(self, display, player_loc):
        global sprite_sheet_projectile
        global projectile_config_opti
        global grid_multi
        global Projectile_pos_add
        if(self.curr_state != "destroy"):
            self.curr_state = "destroy"
            ind = self.pos_x + self.pos_y * player_loc["x"] *2 + self.color*player_loc["x"]
            display.write_img_ram(sprite_sheet_projectile[ind],
                              [self.pos_x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[ind][0],
                               self.pos_y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"] + projectile_config_opti[ind][1]],
                              erase = True, ram_red_after_upd = True)
        return True
             


    def move_down(self, display, player_loc):
        global sprite_sheet_projectile
        global projectile_config_opti
        global grid_multi
        global Projectile_pos_add
        self.pos_y += 1
        if(self.pos_y >= player_loc["y"]):
            self.flag_destroy = True
            self.pos_y -= 1            
        else:
            ind = self.pos_x + (self.pos_y-1) * player_loc["x"] *2 + self.color*player_loc["x"]
            display.write_img_ram(sprite_sheet_projectile[ind],
                              [self.pos_x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[ind][0],
                               (self.pos_y-1)*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"] + projectile_config_opti[ind][1]],
                              erase = True, ram_red_after_upd = True)
            ind = self.pos_x + (self.pos_y) * player_loc["x"] *2 + self.color*player_loc["x"]
            display.write_img_ram(sprite_sheet_projectile[ind],
                              [self.pos_x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[ind][0],
                               self.pos_y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"]+ projectile_config_opti[ind][1]],
                              erase = False, ram_red_after_upd = True)
        
    def verify_move_down(self, display, player_loc, battement):
        global nb_projectile_before
        global grid_multi
        global Projectile_pos_add
        if(not(battement.move_ok(self.index))):
            return False
        elif(self.curr_state == "down"):
            self.move_down(display, player_loc)
            return True
        elif(self.curr_state == "destroy"):
            return True
        return False

        
    def is_same_pos(self, p_pos_x, p_pos_y):
        return (p_pos_x == self.pos_x) and (p_pos_y == self.pos_y) and (self.curr_state == "down")
        
    def start_mode(self):
        return (self.curr_state == "before")


            
            
        
            
def projectile_mark(player_loc, display):
    global sprite_sheet_projectile
    global sprite_sheet_projectile_before
    global projectile_before_config_opti
    global sprite_projectile_before_hidden
    global projectile_before_hidden_config_opti
    global projectile_config_opti
    global grid_multi
    
    for x in range(player_loc["x"]):
        for y in range(player_loc["y"]):
            for c in ([0, 1]):
                ind = x + y * player_loc["x"] *2 + c*player_loc["x"]
                display.write_img_ram(sprite_sheet_projectile[ind],
                              [x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[ind][0],
                               y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"]+ projectile_config_opti[ind][1]],
                                                                                        ram_now = False, ram_before = False)
    collect()