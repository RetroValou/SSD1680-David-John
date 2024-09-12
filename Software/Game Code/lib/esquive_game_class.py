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


grid_multi = {"x": 36, "x_decal": 12, "y": 62-10, "y_decal" : 62+16-4}
grid_multi_sp_projectile_before = {"x": 34, "x_decal": 12+4, "y": 60, "y_decal" : 20+14}

Projectile_speed_limit = {"min": 5, "max": 40}
Projectile_speed_increase = 1/30
Projectile_speed_random_power = 8
Projectile_speed_random_harmony = 1.2
Projectile_wait_before_move_limit = {"min": 30, "max": 60+20} 
Projectile_blink = 12
Projectile_pos_add = {"before_y":-38, "before_x":4, "y":-5}

speed_fall_limit = {"min": 40, "max": 70}


sprite_sheet_projectile = 0
sprite_sheet_projectile_before = 0
projectile_before_config_opti = 0
projectile_config_opti = 0
nb_projectile_before = 0

projectile_force_screen = 5

min_t_wait = 25


def can_create_projectile(nb_max = 1):
    global nb_projectile_before
    return nb_projectile_before < nb_max


def init_projectile(display):
    global nb_projectile_before
    nb_projectile_before = 0
    

def init_visual_projectile(display):
    global sprite_sheet_projectile
    global sprite_sheet_projectile_before
    global projectile_before_config_opti
    global projectile_config_opti

    # /// Projectile ///
    with open("/img/esquive/projectile_multi.json", 'r') as f:
        sprite_sheet_projectile, projectile_config_opti = display.pre_optimise_img(load(f)) 
    with open("/img/esquive/projectile_before_multi.json", 'r') as f:
        sprite_sheet_projectile_before, projectile_before_config_opti = display.pre_optimise_img(load(f))   


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
        self.nb_bat = 1 #max(int(Projectile_speed(t_table_transformed)/min_t_wait), 1)
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
    
    def __init__(self, display, player_loc, t, index_bat, force_x = -1):
        global sprite_sheet_projectile_before
        global projectile_before_config_opti
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
        self.curr_state = "before"
        self.index = index_bat
        
        display.write_img_ram(sprite_sheet_projectile_before[self.pos_x + self.pos_y * player_loc["x"]],
                              [self.pos_x*grid_multi_sp_projectile_before["x"] - grid_multi_sp_projectile_before["x_decal"] + Projectile_pos_add["before_x"]+ projectile_before_config_opti[self.pos_x + self.pos_y * player_loc["x"]][0],
                               grid_multi_sp_projectile_before["y_decal"] + Projectile_pos_add["before_y"] + projectile_before_config_opti[self.pos_x + self.pos_y * player_loc["x"]][1]],
                              erase = False, ram_red_after_upd = True)
        
        
    def destroy(self, display, player_loc):
        global sprite_sheet_projectile
        global projectile_config_opti
        global grid_multi
        global Projectile_pos_add
        if(self.curr_state != "destroy"):
            self.curr_state = "destroy"
            display.write_img_ram(sprite_sheet_projectile[self.pos_x + self.pos_y * player_loc["x"]],
                              [self.pos_x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[self.pos_x + self.pos_y * player_loc["x"]][0],
                               self.pos_y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"] + projectile_config_opti[self.pos_x + self.pos_y * player_loc["x"]][1]],
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
            return
        display.write_img_ram(sprite_sheet_projectile[self.pos_x + (self.pos_y-1) * player_loc["x"]],
                              [self.pos_x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[self.pos_x + (self.pos_y-1) * player_loc["x"]][0],
                               (self.pos_y-1)*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"] + projectile_config_opti[self.pos_x + (self.pos_y-1) * player_loc["x"]][1]],
                              erase = True, ram_red_after_upd = True)
        display.write_img_ram(sprite_sheet_projectile[self.pos_x + self.pos_y*player_loc["x"]],
                              [self.pos_x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[self.pos_x + self.pos_y * player_loc["x"]][0],
                               self.pos_y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"]+ projectile_config_opti[self.pos_x + self.pos_y * player_loc["x"]][1]],
                              erase = False, ram_red_after_upd = True)

    def verify_move_down(self, display, player_loc, battement):
        global nb_projectile_before
        global sprite_sheet_projectile_before
        global projectile_before_config_opti
        global sprite_sheet_projectile
        global projectile_config_opti
        global grid_multi
        global Projectile_pos_add
        if(not(battement.move_ok(self.index))):
            return False
        elif(self.curr_state == "before"):
            display.write_img_ram(sprite_sheet_projectile_before[self.pos_x + self.pos_y * player_loc["x"]],
                [self.pos_x*grid_multi_sp_projectile_before["x"] - grid_multi_sp_projectile_before["x_decal"] + Projectile_pos_add["before_x"]+ projectile_before_config_opti[self.pos_x + self.pos_y * player_loc["x"]][0],
                grid_multi_sp_projectile_before["y_decal"] + Projectile_pos_add["before_y"] + projectile_before_config_opti[self.pos_x + self.pos_y * player_loc["x"]][1]],
                    erase = True, ram_red_after_upd = True)
            display.write_img_ram(sprite_sheet_projectile[self.pos_x + self.pos_y * player_loc["x"]],
                [self.pos_x*grid_multi["x"] - grid_multi["x_decal"]+ projectile_config_opti[self.pos_x + self.pos_y * player_loc["x"]][0],
                 self.pos_y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"]+ projectile_config_opti[self.pos_x + self.pos_y * player_loc["x"]][1]],
                erase = False, ram_red_after_upd = True)
            nb_projectile_before -= 1
            self.curr_state = "down"
            return True
        elif(self.curr_state == "down"):
            self.move_down(display, player_loc)
            return True
        elif(self.curr_state == "destroy"):
            return True
        return False
        
    def is_same_pos(self, p_pos_x, p_pos_y):
        return (p_pos_x == self.pos_x) and (p_pos_y == self.pos_y) and (self.curr_state == "down")

    def hidden_now(self, display, player_loc, erase = True, ram_red_after_upd = False):
        global sprite_sheet_projectile_before
        global projectile_before_config_opti
        global sprite_sheet_projectile
        global projectile_config_opti
        global grid_multi
        global grid_multi_sp_projectile_before
        global Projectile_pos_add
        if(self.curr_state == "down" or self.curr_state == "destroy"):
            display.write_img_ram(sprite_sheet_projectile[self.pos_x + self.pos_y * player_loc["x"]],
                              [self.pos_x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[self.pos_x + self.pos_y * player_loc["x"]][0],
                               self.pos_y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"] + projectile_config_opti[self.pos_x + self.pos_y * player_loc["x"]][1]],
                              erase = erase, ram_red_after_upd = ram_red_after_upd)
        else: # Before mode
            display.write_img_ram(sprite_sheet_projectile_before[self.pos_x + self.pos_y * player_loc["x"]],
                              [self.pos_x*grid_multi_sp_projectile_before["x"] - grid_multi_sp_projectile_before["x_decal"]+ Projectile_pos_add["before_x"]+ projectile_before_config_opti[self.pos_x + self.pos_y * player_loc["x"]][0],
                               grid_multi_sp_projectile_before["y_decal"] + Projectile_pos_add["before_y"]+ projectile_before_config_opti[self.pos_x + self.pos_y * player_loc["x"]][1]],
                              erase = erase, ram_red_after_upd = ram_red_after_upd)

    def start_mode(self):
        return (self.curr_state == "before")


            
            
            
            
            
def projectile_mark(player_loc, display):
    global sprite_sheet_projectile
    global sprite_sheet_projectile_before
    global projectile_before_config_opti
    global projectile_config_opti
    global grid_multi
    
    for i in range(player_loc["x"]):
        display.write_img_ram(sprite_sheet_projectile_before[i],
                              [i*grid_multi_sp_projectile_before["x"] - grid_multi_sp_projectile_before["x_decal"]+ Projectile_pos_add["before_x"]+ projectile_before_config_opti[i][0],
                               grid_multi_sp_projectile_before["y_decal"] + Projectile_pos_add["before_y"]+ projectile_before_config_opti[i][1]],
                                                                                    ram_now = False, ram_before = False)
    for x in range(player_loc["x"]):
        for y in range(player_loc["y"]):
            display.write_img_ram(sprite_sheet_projectile[x + y * player_loc["x"]],
                              [x*grid_multi["x"] - grid_multi["x_decal"] + projectile_config_opti[x + y * player_loc["x"]][0],
                               y*grid_multi["y"] + grid_multi["y_decal"] + Projectile_pos_add["y"] + projectile_config_opti[x + y * player_loc["x"]][1]],
                                                                                        ram_now = False, ram_before = False)
        collect()