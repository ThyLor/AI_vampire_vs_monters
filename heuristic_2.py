# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 08:34:09 2019

@author: Lollo
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 00:57:47 2019

@author: Lollo
"""

import numpy as np
import compute_successors as cs

# --------------------------------- DEFINITION OF AUXILIARS FUNCTIONS

# for indexing
# List of possible directions
# FOR CONVENTION we'll use the map: direction ---> index of the list is the following
# this is a smart map:   phi_i : (d_x,d_y) --> 3*d_x + d_y + 4
# For d_x : -1 (left), 0 (center), 1 (right)
# For d_y : -1 (down), 0 (middle), 1 (up)
# it maps direction in the following way:
# (-1,-1) -> 0, (-1,0) -> 1 , (-1,1) -> 2, (0,-1) -> 3
# (0,0) -> 4, (0,1) -> 5, (1,-1) -> 6, (1,0) -> 7 , (1,1) -> 8

def dir_index_map(d_x,d_y):
    return 3*d_x + d_y + 4

def inv_index_map(val):
    if(val == 0):
        return [-1,-1]
    elif(val == 1):
        return [-1,0]
    elif(val == 2):
        return [-1,1]
    elif(val == 3):
        return [0,-1]
    elif(val == 4):
        return [0,0]
    elif(val == 5):
        return [0,1]
    elif(val == 6):
        return [1,-1]
    elif(val == 7):
        return [1,0]
    else:
        return [1,1]

# for geometry  
def distance_between_groups_principal_axis(x_1,y_1,x_2,y_2):
    if(x_1 == x_2):
        return abs(y_2-y_1) - 1
    elif(y_1 == y_2):
        return abs(x_2-x_1) - 1
    else:
        return -1
    
def distance_between_groups_diagonals(x_1,y_1,x_2,y_2):
    dist = abs(x_1 - x_2) 
    if(dist == abs(y_1 - y_2)):
        return dist - 1
    else:
        return -1

def distance_between_groups(x_1,y_1,x_2,y_2, adj_0 = False):
    d = distance_between_groups_principal_axis(x_1,y_1,x_2,y_2)
    if adj_0:
        if (d != -1):
            return d
        else:
             # we're not in the principal axis
             # check whether is right adjacent
            d = distance_between_groups_diagonals(x_1,y_1,x_2,y_2)
            if(d != -1):
                return d
            # this case is never evaluated in practice, but for the sake of clarity...
            elif(x_1 == x_2 and y_1 == y_2):
                return -1
            else: 
                #here is try to move in a position that belongs to the diagonal or to a principal axis
                # we're looking where the g2 is
                d = 1
                d_x = 0
                d_y = 0
                c_d_x = x_1
                c_d_y = y_1
                while(True):
                    # get the direction in which we have to point towards
                    if( x_2 > c_d_x):
                        d_x = 1
                    else:
                        d_x = -1
                    if( c_d_y > y_2):
                        d_y = 1
                    else:
                        d_y = -1                
                    # Update the coordinates
                    c_d_x += + d_x
                    c_d_y += - d_y
                    # Notice that the event diagonals and principal axis are partitions of events
                    dist = max(distance_between_groups_principal_axis(c_d_x,c_d_y,x_2,y_2),distance_between_groups_diagonals(c_d_x,c_d_y,x_2,y_2))
                    if(dist != -1):
                        return d + dist + 1
                    # otherwise i increase the distance
                    d += 1  
    else:
        if (d != -1):
            return d + 1
        else:
             # we're not in the principal axis
             # check whether is right adjacent
            d = distance_between_groups_diagonals(x_1,y_1,x_2,y_2)
            if(d != -1):
                return d + 1
            # this case is never evaluated in practice, but for the sake of clarity...
            elif(x_1 == x_2 and y_1 == y_2):
                return 0
            else: 
                #here is try to move in a position that belongs to the diagonal or to a principal axis
                # we're looking where the g2 is
                d = 1
                d_x = 0
                d_y = 0
                c_d_x = x_1
                c_d_y = y_1
                while(True):
                    # get the direction in which we have to point towards
                    if( x_2 > c_d_x):
                        d_x = 1
                    else:
                        d_x = -1
                    if( c_d_y > y_2):
                        d_y = 1
                    else:
                        d_y = -1                
                    # Update the coordinates
                    c_d_x += + d_x
                    c_d_y += - d_y
                    # Notice that the event diagonals and principal axis are partitions of events
                    dist = max(distance_between_groups_principal_axis(c_d_x,c_d_y,x_2,y_2),distance_between_groups_diagonals(c_d_x,c_d_y,x_2,y_2))
                    if(dist != -1):
                        return d + dist + 1
                    # otherwise i increase the distance
                    d += 1  
                    
def get_the_direction(xm,ym,xh,yh):
    # Geometry: just see where humans are wrt us
    # Set the initial directions to -1

    d_x = -1
    d_y = -1 
                       
    # For x
    if xm == xh:
        d_x = 0
    elif xh > xm:
        d_x = 1
    # For y
    if ym == yh:
        d_y = 0
    elif ym > yh:
        d_y = 1

    return d_x,d_y

# for battles                   
def expected_gain_humans(E1,H1): 
    #normalized to one
    EH = E1/H1
    if EH >= 1:
        P = 1
    else: # we do not consider the tem that converns the monsters in the conditional expectation
        P = (EH/2)
    
    # FRACTION of E1 + H1 that we will have in the next step    
    return (P**2)
    #return a function of E2 (here alctually we have to introduce another parameter, alpha)
def expected_gain_monster(E1,E2): 
    #alpha: how I want to be aggressive towards monster--> must augment during the game
    # alpha small --> really aggresive i dont care if we die or not. alpha high --> it's better to keep our monsters alive
    # different from alpha and beta at the begging.. its not the importance of monster it self
    #normalized to one
    E12 = E1/E2
    # analyzing our monster
    if E12 >= 1.5:
        P12 = 1
        our_alive_monsters = 1 
    elif E12 >= 1:
        P12 = E12 - 0.5
        our_alive_monsters = P12**2 
    else:
        P12 = 0.5*E12
        our_alive_monsters = P12**2 
        
    their_alive_monsters = (1-P12)**2 
        
    # our_alive_monsters in [0,1]
    # our_alive_monsters in [0,1]
    return our_alive_monsters, their_alive_monsters

# for the heuristics 
def activation_function_humans(value,par = 15): # par is a function of to_hg (the higher to_hg the higher par)
    return value**par

def activation_function_monsters(value,par = 10): # par is a function of to_hg (the higher to_mg the higher par)
    return value**par

def compute_score(heuristic,index_possible_directions):
    sum_partial_scores = 0
    for i in index_possible_directions:
        sum_partial_scores += heuristic[i]
    return sum_partial_scores * len(index_possible_directions)/8


def compute_score_state_player(our_monsters_list, their_monsters_list, humans_list, our_monsters_nb_groups, their_monsters_nb_groups, nb_groups_humans, nb_our_monsters, width, height, MAX_DIST, MAX_NB_HUMANS, INF, to_gh = 3, to_gm = 3, alpha_m_attack = 0.5 , alpha_m_direction = 0.7, lam_mh_attack = 0.5 , lam_mh_direction = 0.7, alpha_ins = 0.1, print_heuristic = False):
    # extreme situations
    if(len(our_monsters_list) == 0):
        return -INF
    if(len(their_monsters_list) == 0):
        return +INF 
    
    # compute some useful constants
    if(their_monsters_nb_groups == 0):
        MAX_NB_OTHER_MONSTERS = -1
        NB_OTHER_MONSTERS = 0
    else:
        MAX_NB_OTHER_MONSTERS = np.max([elem[2] for elem in their_monsters_list])
        NB_OTHER_MONSTERS =  np.sum([elem[2] for elem in their_monsters_list])
    
    # Current positions
    x_us = our_monsters_list[0][0]
    y_us = our_monsters_list[0][1]
    
    #----------------------------------------------------ADMISSIBLE POSITIONS
        
    possible_directions = cs.allowed_directions(x_us,y_us,width,height)
    nb_possible_directions = len(possible_directions)
    index_possible_directions = []
    for p in range(0,nb_possible_directions):
        index_possible_directions.append(dir_index_map(possible_directions[p][0],possible_directions[p][1]))
    
    #----------------------------------------------------HEURISTIC MESURES
        
    heuristic_humans = np.zeros((9,))
    heuristic_monsters = np.zeros((9,))
    
    compute_battles_score_monsters = 0     
    compute_battles_score_humans = 0    
    
    if nb_groups_humans > 0:
        #----------------------------------------------------ADMISSIBLES GROUPS OF HUMANS
        
        #Compute all the distances between the gruop of monsters and the humans and store them in distances_humans
        distances_humans = []
        distances_humans_evenif = []
        for i in range(nb_groups_humans):
            
            # Get the position of the first human group
            x_h = humans_list[i][0]
            y_h = humans_list[i][1]
            
            # Normally I compute the distance. 
            # BUT: if there are more humans than monsters d = MAX_DIST so that this solution won't be choosen
            # OR: if there exists an adversary that is nearer  than us to the group of humans is worthless to go towards that direction d = MAX_DIST
            # NOTE: limitation of the second case: see notes
            
            if humans_list[i][2] <= nb_our_monsters:
                
                dh_pivot = distance_between_groups(x_us,y_us,x_h,y_h)
                distances_humans_evenif.append(dh_pivot)
                # If also i'm nearer
                im_nearer = True
                for i_tm in range(their_monsters_nb_groups):
                    if(distance_between_groups(their_monsters_list[i_tm][0],their_monsters_list[i_tm][1],x_h,y_h) < dh_pivot):
                        im_nearer = False
                        break;
                if im_nearer:
                    distances_humans.append(dh_pivot)
                else:
                    distances_humans.append(MAX_DIST)
            else:
                distances_humans.append(MAX_DIST)
        
        go_towards_monsters = False
        
        if len(set(distances_humans)) == 1 and list(set(distances_humans))[0] == MAX_DIST:
            go_towards_monsters = True
            distances_humans = distances_humans_evenif
            
        # Normalize distances 
        to_nb_groups_humans_considered = min(to_gh,nb_groups_humans)
        normalized_distances_humans = [d/(MAX_DIST*to_nb_groups_humans_considered) for d in distances_humans]
        
        # And take the nearest groups 
        index_least_distances = np.argsort(normalized_distances_humans)[0:to_nb_groups_humans_considered]
        
        #----------------------------------------------------Part I: ILTD "I like this direction"
        
        for i in index_least_distances:
            # Get the number of humans in that specific position
            current_nb_humans = humans_list[i][2]
            
            # Get the position of the first human group
            x_h = humans_list[i][0]
            y_h = humans_list[i][1]
            
            d_x, d_y = get_the_direction(x_us,y_us,x_h,y_h)
            direction_index = dir_index_map(d_x,d_y)
            
            #if distance_between_groups(x_us,y_us,x_h,y_h) > 0:    
            if(direction_index in index_possible_directions):
                heuristic_humans[direction_index] += (current_nb_humans/MAX_NB_HUMANS) * activation_function_humans(1-normalized_distances_humans[i])
        
        # I like this direction, but what if: there is another group of humans > us in that direction?
        
        # If I dont d any battle what is the expected number of monsters (must be standardize to [0, 1])
        C_S_H = nb_our_monsters / (nb_our_monsters + MAX_NB_HUMANS)
        compute_battles_score_humans = C_S_H
        
        for i in range(nb_groups_humans):
            
            current_nb_humans = humans_list[i][2]
    
            # Get the position of the first human group
            x_h = humans_list[i][0]
            y_h = humans_list[i][1] 
            
            # If there is a battle
            if distance_between_groups(x_us,y_us,x_h,y_h) == 0:
                # we need to standardize this quantiy to a variable whose range is [0,1]
                # FOR OUTLIERS?
                 compute_battles_score_humans = expected_gain_humans(nb_our_monsters,current_nb_humans) * ( (nb_our_monsters + current_nb_humans) / (nb_our_monsters + MAX_NB_HUMANS) )  
            #N.B.: by def, compute_battle_score_humans < 
    
                #if nb_our_monsters < current_nb_humans: #meaning less, just testing 
                #    compute_battles_score_humans = -INF
                #else:
                #    compute_battles_score_humans += EGH
            
        #----------------------------------------------------ADMISSIBLES GROUPS OF MONSTERS
        #Compute all the distances between the group of vampires and the warewolves
        distances_their_monsters = []
        
        for i in range(their_monsters_nb_groups):
            
            x_them = their_monsters_list[i][0]
            y_them = their_monsters_list[i][1]
            
            # Normally I compute the distance. 
            # BUT: if the other are more than us than monsters d = MAX_DIST so that this solution won't be choosen
            dm_pivot = distance_between_groups(x_us,y_us,x_them,y_them)
            if not go_towards_monsters:
                if their_monsters_list[i][2] <= 1.5 * nb_our_monsters:
                    distances_their_monsters.append(dm_pivot)
                else:
                    distances_their_monsters.append(MAX_DIST)
            else:
                distances_their_monsters.append(dm_pivot)
        # Normalize distances 
        to_nb_groups_their_monsters_considered = min(to_gm,their_monsters_nb_groups)
        normalized_distances_their_monsters = [d/(MAX_DIST*to_nb_groups_their_monsters_considered) for d in distances_their_monsters]
        
        # And take the nearest groups 
        index_least_distances_their_monsters = np.argsort(normalized_distances_their_monsters)[0:to_nb_groups_their_monsters_considered]
        
        for i in index_least_distances_their_monsters:
            # Get the number of humans in that specific position
            current_nb_their_monsters = their_monsters_list[i][2]
            
            # Get the position of the first human group
            x_them = their_monsters_list[i][0]
            y_them = their_monsters_list[i][1]
            
            d_x, d_y = get_the_direction(x_us,y_us,x_them,y_them)
            
            # Compute the relative index
            direction_index = dir_index_map(d_x,d_y)
            
            if(direction_index in index_possible_directions):
                heuristic_monsters[direction_index] += activation_function_monsters(1-normalized_distances_their_monsters[i])*(current_nb_their_monsters/MAX_NB_OTHER_MONSTERS)
        
        C_S_M = nb_our_monsters / (NB_OTHER_MONSTERS) # what we look is the ration
        
        compute_battles_score_monsters = C_S_M
        for i in range(their_monsters_nb_groups):
            
            current_nb_their_monsters = their_monsters_list[i][2]
    
            # Get the position of the first human group
            x_them = their_monsters_list[i][0]
            y_them = their_monsters_list[i][1] 
            
            # If there is a battle
            if distance_between_groups(x_us,y_us,x_them,y_them) == 0:
                fraction_our_monster, fraction_their_monsters = expected_gain_monster(nb_our_monsters,current_nb_their_monsters)
                compute_battles_score_monsters = alpha_ins * (nb_our_monsters * fraction_our_monster) / ( NB_OTHER_MONSTERS + current_nb_their_monsters * ( fraction_their_monsters - 1) )
        
    else:
        distances_their_monsters = []
        
        for i in range(their_monsters_nb_groups):
            
            x_them = their_monsters_list[i][0]
            y_them = their_monsters_list[i][1]
            dm_pivot = distance_between_groups(x_us,y_us,x_them,y_them)
            distances_their_monsters.append(dm_pivot)
        # Normalize distances 
        to_nb_groups_their_monsters_considered = min(to_gm,their_monsters_nb_groups)
        normalized_distances_their_monsters = [d/(MAX_DIST*to_nb_groups_their_monsters_considered) for d in distances_their_monsters]
        
        # And take the nearest groups 
        index_least_distances_their_monsters = np.argsort(normalized_distances_their_monsters)[0:to_nb_groups_their_monsters_considered]
        
        for i in index_least_distances_their_monsters:
            # Get the number of humans in that specific position
            current_nb_their_monsters = their_monsters_list[i][2]
            
            # Get the position of the first human group
            x_them = their_monsters_list[i][0]
            y_them = their_monsters_list[i][1]
            
            d_x, d_y = get_the_direction(x_us,y_us,x_them,y_them)
            
            # Compute the relative index
            direction_index = dir_index_map(d_x,d_y)
            
            if(direction_index in index_possible_directions):
                heuristic_monsters[direction_index] += activation_function_monsters(1-normalized_distances_their_monsters[i])*(current_nb_their_monsters/MAX_NB_OTHER_MONSTERS)
        
        C_S_M = nb_our_monsters / (NB_OTHER_MONSTERS) # what we look is the ration
        
        battle = C_S_M < 1
        compute_battles_score_monsters = C_S_M
        for i in range(their_monsters_nb_groups):
            
            current_nb_their_monsters = their_monsters_list[i][2]
    
            # Get the position of the first human group
            x_them = their_monsters_list[i][0]
            y_them = their_monsters_list[i][1] 
            
            # If there is a battle
            if distance_between_groups(x_us,y_us,x_them,y_them) == 0:
                # here we are in very extreme cases
                if battle:
                    compute_battles_score_monsters =  + 2 * INF 
                else:
                    compute_battles_score_monsters = - 2 * INF
    # Nothing but a convex combination. Heuristic cannot be > 1
   
    val_heur =  lam_mh_direction * (compute_score(heuristic_humans,index_possible_directions)) + lam_mh_attack * compute_battles_score_humans + alpha_m_direction * (compute_score(heuristic_monsters,index_possible_directions)) + alpha_m_attack * compute_battles_score_monsters
     
    #print("Compute_battles_score_humans: "+str(compute_battles_score_humans))
    #print("Compute_battles_score_monstres: "+str(compute_battles_score_monsters))
    #print("Val heuristique: "+str(val_heur))
    #if print_heuristic:
    #    print("S.H.D. = "+str(lam_mh_direction * compute_score(heuristic_humans,index_possible_directions)))
    #    print("S.H.A. = "+str(lam_mh_attack * compute_battles_score_humans))
    #    print("Compute_battles_score_humans: "+str(compute_battles_score_humans))
    #    print("S.M.D. = "+str(alpha_m_direction * compute_score(heuristic_monsters,index_possible_directions)))
    #    print("S.M.A. = "+str(alpha_m_attack * compute_battles_score_monsters))
    
    return val_heur
              
              
def compute_score_state(s_act, s_prec2, s_prec4, player, print_heuristic = False):
    
    # Grid parameter
    width = s_act.width
    height = s_act.height
    
    # ---------------------------------------- For the current state
    
    ## Get the list
    humans_list = s_act.get_humans_list()
    vampires_list = s_act.get_vampires_list()
    werewolves_list = s_act.get_werewolves_list()
    
    ## Numbers of groups for each species
    nb_groups_humans = len(humans_list)
    nb_groups_vampires = len(vampires_list)
    nb_groups_werewolves = len(werewolves_list)
    
    ## Absolute number of
    nb_vampires = s_act.get_nb_vampires()
    nb_werewolves = s_act.get_nb_werewolves()
    
    # ---------------------------------------- For the previous state
    ## Absolute number of
    nb_vampires_prec2 = s_prec2.get_nb_vampires()
    nb_werewolves_prec2 = s_prec2.get_nb_werewolves()
    
    # --------------------------------------- FOr the previous - previous state
    
    nb_vampires_prec4 = s_prec4.get_nb_vampires()
    nb_werewolves_prec4 = s_prec4.get_nb_werewolves()
    
    
    #constants
    INF = 10**4
    MAX_DIST = distance_between_groups(0,0,width-1,height-1)
    
    if(nb_groups_humans == 0):
        MAX_NB_HUMANS = -1
    else:
        MAX_NB_HUMANS = np.max([elem[2] for elem in humans_list])
       
    if (player == "vampires"):
        
        # Parametres heuristique
        lam_vh_attack = 1
        lam_vh_direction = 1
        
        alpha_v_attack = 1
        alpha_v_direction = 1 - lam_vh_direction # either i go towards monsters or humans
        
        alpha_insanity_vampires = 1  # if > 1 they will be really aggressive
        
        # How is important the results of a battle
        IMPORTANCE_BATTLES = 10
        
        # ratio number of vampires
        if nb_vampires_prec2 > 0 and nb_vampires_prec4 > 0:
            RATIO_BETWEEN_STATES_2 = nb_vampires/nb_vampires_prec2
            RATIO_BETWEEN_STATES_4 = nb_vampires_prec2/nb_vampires_prec4
        else:
            RATIO_BETWEEN_STATES_2 = RATIO_BETWEEN_STATES_4 = 1

        heuristic_par_vampires = [IMPORTANCE_BATTLES * alpha_v_attack, alpha_v_direction, IMPORTANCE_BATTLES * lam_vh_attack, lam_vh_direction]
        heuristic_par_vampires_norm = [elem/np.sum(heuristic_par_vampires) for elem in heuristic_par_vampires]
        #print("R2:"+str(RATIO_BETWEEN_STATES_2))
        #print("R4:"+str(RATIO_BETWEEN_STATES_4))
        return (5 * RATIO_BETWEEN_STATES_4 + RATIO_BETWEEN_STATES_2) * compute_score_state_player(vampires_list, werewolves_list, humans_list, nb_groups_vampires, nb_groups_werewolves, nb_groups_humans, nb_vampires, width, height, MAX_DIST, MAX_NB_HUMANS, INF, to_gh = 2, to_gm = 2, alpha_m_attack = heuristic_par_vampires_norm[0], alpha_m_direction = heuristic_par_vampires_norm[1], lam_mh_attack = heuristic_par_vampires_norm[2] , lam_mh_direction = heuristic_par_vampires_norm[3], alpha_ins = alpha_insanity_vampires, print_heuristic = print_heuristic)
    
    elif(player == "werewolves"): 
        
          
        lam_wh_attack = 1
        lam_wh_direction = 1
        
        alpha_w_attack = 1
        alpha_w_direction = 1 - lam_wh_direction
        
        alpha_insanity_werewolves = 1
        
        # How is important the results of a battle
        IMPORTANCE_BATTLES = 10
        
        heuristic_par_werewolves = [IMPORTANCE_BATTLES * alpha_w_attack, alpha_w_direction, IMPORTANCE_BATTLES * lam_wh_attack, lam_wh_direction]
        heuristic_par_werevolves_norm = [elem/np.sum(heuristic_par_werewolves) for elem in heuristic_par_werewolves]
        
        if nb_werewolves_prec2 > 0 and nb_werewolves_prec4 > 0:
            
            RATIO_BETWEEN_STATES_2 = nb_werewolves/nb_werewolves_prec2
            RATIO_BETWEEN_STATES_4 = nb_werewolves_prec2/nb_werewolves_prec4
        else:
            RATIO_BETWEEN_STATES_2 = RATIO_BETWEEN_STATES_4 = 1

            
        #print("R2:"+str(RATIO_BETWEEN_STATES_2))
        #print("R4:"+str(RATIO_BETWEEN_STATES_4))
        
        return ( 5 * RATIO_BETWEEN_STATES_4 + RATIO_BETWEEN_STATES_2) * compute_score_state_player(werewolves_list, vampires_list, humans_list, nb_groups_werewolves, nb_groups_vampires, nb_groups_humans, nb_werewolves, width, height, MAX_DIST, MAX_NB_HUMANS, INF, to_gh = 2, to_gm = 2, alpha_m_attack = heuristic_par_werevolves_norm[0], alpha_m_direction = heuristic_par_werevolves_norm[1], lam_mh_attack = heuristic_par_werevolves_norm[2] , lam_mh_direction = heuristic_par_werevolves_norm[3], alpha_ins = alpha_insanity_werewolves)
    
    
    # NOTE: lam_h and alpha may vary depending on the situation. We will do an estimation procedure. But before we have to make several simulations
        