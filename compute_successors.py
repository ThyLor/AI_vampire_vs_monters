# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 17:55:03 2018

@author: assae
"""

import state as st
import numpy as np
import itertools
import time

def allowed_directions(x, y, w, h):
    if x >= w or y >= h:
        print("Position error")
    elif (x == 0 and y == 0):
        return [[0,-1], [1,-1], [1,0]]
    elif (x == w-1 and y == 0):
        return [[-1,0], [-1,-1], [0,-1]]
    elif (x == 0 and y == h-1):
        return [[0,1], [1,1], [1,0]]
    elif (x == w-1 and y == h-1):
        return [[-1,0], [-1,1], [0,1]]
    elif (x == 0 and y != 0 and y != h-1):
        return [[0,1], [0,-1], [1,-1], [1,1], [1,0]]
    elif (x == w-1 and y != 0 and y != h-1):
        return [[0,1], [0,-1], [-1,1], [-1,-1], [-1,0]]
    elif (x != 0 and x != w-1 and y == 0):
       return [[-1,0], [1,0], [-1,-1], [1,-1], [0,-1]]
    elif (x != 0 and x != w-1 and y == h-1):
       return [[-1,0], [1,0], [-1,1], [1,1], [0,1]]
    else:
        return [[1,0], [1,1], [0,1], [-1,1], [-1,0], [-1,-1], [0,-1], [1,-1]]
    
    
    
def compute_successors(s, player):
    """return sucessors of state s as [proba, [directions], [successor state]]"""
    
    humans_list = s.get_humans_list()
    vampires_list = s.get_vampires_list()
    werewolves_list = s.get_werewolves_list()
    nb_groups_humans = len(humans_list)
    nb_groups_vampires = len(vampires_list)
    nb_groups_werewolves = len(werewolves_list)
    nb_humans =  s.get_nb_humans()
    nb_vampires = s.get_nb_vampires()
    nb_werewolves = s.get_nb_werewolves()
    width = s.width
    height = s.height
    
    if player == "vampires":      
        possible_directions = []
        moves = []
         
        for group in vampires_list:
            possible_directions = allowed_directions(group[0], group[1], width, height)
            """We add as the first term the possible directions so that we can easily have it afterwards, 
            so, in the state some elements will have 6 elements, the first being the direction.
            To remove for calculations and add back afterwards."""
            moves.append([[[possible_directions[j][0], possible_directions[j][1]], [group[0], group[1], group[2], group[0]+ possible_directions[j][0], 
                            group[1]- possible_directions[j][1]]] for j in range(len(possible_directions))])
        moves = cartesian_product(*moves)
        new_states = []
        for i in range(len(moves)):
            new_states.append(compute_states_after_moves(s, list(moves[i]), player))
            
        final = []
        interm = []
        for i in range(len(new_states)):
            if len(new_states[i]) != 3 and new_states[i][0] != 1:
                interm.append(new_states[i])
            else:
                final.append(new_states[i])
        for i in range(len(interm)):
            final.append(interm[i][0])
            final.append(interm[i][1])

        for i in range(len(final)):
            final[i][2] = st.State(final[i][2], width, height)
        return final
    
    elif player == "werewolves":      
        possible_directions = []
        moves = []

        for group in werewolves_list:
            possible_directions = allowed_directions(group[0], group[1], width, height)
            moves.append([[[possible_directions[j][0], possible_directions[j][1]], [group[0], group[1], group[2], group[0]+ possible_directions[j][0],
                          group[1]- possible_directions[j][1]]] for j in range(len(possible_directions))])
        moves = cartesian_product(*moves)
        new_states = []
        for i in range(len(moves)):
            new_states.append(compute_states_after_moves(s, list(moves[i]), player))
        
        final = []
        interm = []
        for i in range(len(new_states)):
            if len(new_states[i]) != 3 and new_states[i][0] != 1:
                interm.append(new_states[i])
            else:
                final.append(new_states[i])
        for i in range(len(interm)):
            final.append(interm[i][0])
            final.append(interm[i][1])

        for i in range(len(final)):
            final[i][2] = st.State(final[i][2], width, height)
        return final

            


def compute_states_after_moves(state, moves, player):
    """state: a state as usual
    moves: [[[direction], [x, y, nb, newx,, newy], ....]]
    
    Have to return :
         [proba, [directions], state]"""

    w = state.width
    h = state.height
    stte = state.state_list
    s = stte.copy()
    moves = list(moves)
    
    directions = []
    moves_liste = []
    
    for i in range(len(moves)):
        directions.append(moves[i][0])
        moves_liste.append(moves[i][1])
    
    if player == "vampires":        
        modif_with_proba = []
        move_to_remove = []
        state_to_remove1 = []
        state_to_remove2 = []
        
        for i in range(len(moves_liste)):
            for j in range(len(s)):
                if is_not_empty(s[j], moves_liste[i]):
                    origin = look_for_case(s, moves_liste[i][0], moves_liste[i][1])
                    s[origin] = [s[origin][0], s[origin][1], s[origin][2], s[origin][3] - moves_liste[i][2], s[origin][4]]
                    if result(s[j], moves_liste[i][2], player) not in modif_with_proba:
                        modif_with_proba.append(result(s[j], moves_liste[i][2], player))
                    if moves_liste[i] not in move_to_remove:
                        move_to_remove.append(moves_liste[i])
                    
        for k in range(len(s)):
            if s[k][2] == 0 and s[k][3] == 0 and s[k][4] == 0:
                state_to_remove1.append(s[k])
                
        for item in state_to_remove1:
            s.remove(item)
                        
        for m in move_to_remove:
            moves_liste.remove(m)
         
        """now only remain move in a case which is not already in state"""
        
        for i in range(len(moves_liste)):
            origin = look_for_case(s, moves_liste[i][0], moves_liste[i][1])
            if s[origin][3] - moves_liste[i][2] <= 0:
                s[origin] = [s[origin][0], s[origin][1], s[origin][2], 0, s[origin][4]]
            else:
                s[origin] = [s[origin][0], s[origin][1], s[origin][2], s[origin][3] - moves_liste[i][2], s[origin][4]]
            modif_with_proba.append([1, [moves_liste[i][3], moves_liste[i][4], 0, moves_liste[i][2], 0]])
            
        for k in range(len(s)):
            if s[k][2] == 0 and s[k][3] == 0 and s[k][4] == 0:
                state_to_remove2.append(s[k])
                
        for item in state_to_remove2:
            s.remove(item)
        
        
        for i in range(len(s)):
            modif_with_proba.append([1, s[i]])
            
        states_with_proba = from_modifs_to_states(s, modif_with_proba)
        
        try:
            for i in range(len(states_with_proba)):
                states_with_proba[i].insert(1, directions)
        except:
            states_with_proba.insert(1, directions)
            
            
        return states_with_proba
            
        
    elif player == "werewolves":        
        modif_with_proba = []
        move_to_remove = []
        state_to_remove1 = []
        state_to_remove2 = []
        
        for i in range(len(moves_liste)):
            for j in range(len(s)):
                if is_not_empty(s[j], moves_liste[i]):
                    origin = look_for_case(s, moves_liste[i][0], moves_liste[i][1])
                    s[origin] = [s[origin][0], s[origin][1], s[origin][2], s[origin][3], s[origin][4] - moves_liste[i][2]]
                    if result(s[j], moves_liste[i][2], player) not in modif_with_proba:
                        modif_with_proba.append(result(s[j], moves_liste[i][2], player))
                    if moves_liste[i] not in move_to_remove:
                        move_to_remove.append(moves_liste[i])
                    
        for k in range(len(s)):
            if s[k][2] == 0 and s[k][3] == 0 and s[k][4] == 0:
                state_to_remove1.append(s[k])
                
        for item in state_to_remove1:
            s.remove(item)
                        
        for m in move_to_remove:
            moves_liste.remove(m)
         
        """now only remain move in a case which is not already in state"""
        
        for i in range(len(moves_liste)):
            origin = look_for_case(s, moves_liste[i][0], moves_liste[i][1])
            if  s[origin][4] - moves_liste[i][2] <= 0:
                s[origin] = [s[origin][0], s[origin][1], s[origin][2], s[origin][3], 0]
            else:
                s[origin] = [s[origin][0], s[origin][1], s[origin][2], s[origin][3], s[origin][4] - moves_liste[i][2]]
            modif_with_proba.append([1, [moves_liste[i][3], moves_liste[i][4], 0, 0, moves_liste[i][2]]])
            
        for k in range(len(s)):
            """remove empty states"""
            if s[k][2] == 0 and s[k][3] == 0 and s[k][4] == 0:
                state_to_remove2.append(s[k])
                
        for item in state_to_remove2:
            s.remove(item)
        
        
        for i in range(len(s)):
            modif_with_proba.append([1, s[i]])
            
        states_with_proba = from_modifs_to_states(s, modif_with_proba)
        
        try:
            for i in range(len(states_with_proba)):
                states_with_proba[i].insert(1, directions)
        except:
            states_with_proba.insert(1, directions)
            
        return states_with_proba


def from_modifs_to_states(state, modifs):
    """ from a list of modifs like this one [[[0.75, [4, 1, 0, 4, 0]], [0.25, [4, 1, 0, 0, 1]]], 
    [1, [7, 7, 0, 4, 0]], [1, [1, 5, 0, 2, 0]], [1, [4, 1, 0, 0, 4]], [1, [2, 3, 4, 0, 0]], 
    [1, [5, 8, 0, 4, 0]], [1, [1, 4, 0, 2, 0]]], build modifs"""
#    print(state)
#    print("m", modifs)
    nb = 0
    common_final_state = []
    to_spread = []
    
    for i in range(len(modifs)):
        if type(modifs[i][0]) == list and modifs[i][0][0] != 1:
            nb += 1
            to_spread.append(modifs[i])            
        else:
            try:
                common_final_state.append(modifs[i][0][1])
            except:
                common_final_state.append(modifs[i][1])

    
    if len(to_spread) == 0:
         end_states = [1, common_final_state]
         return end_states
    else:
        nb_states = 2**nb   
        states_list = []   
        intermediary = []
        liste_possibilities = iterate_possibilities(len(to_spread))
#        print(nb_states)
#        print(len(to_spread))
        
        if len(to_spread) != 0:
            for i in range(nb_states):
                for couple in list(zip([w for w in range(len(to_spread))], liste_possibilities[i])):
#                    print(liste_possibilities)
#                    print(couple)
#                    print(to_spread)
                    intermediary.append(to_spread[couple[0]][couple[1]])
                states_list.append(intermediary)
                intermediary = []
        
        """ now i have my states_list, just have to extract for each of them the probabilities and
        the states"""
        
        end_states = []
        if len(states_list) != 0:
            for i in range(len(states_list)):
                n = len(states_list[i])
                proba = states_list[i][0][0]
                one_state = [states_list[i][0][1]]
                for j in range(1,n):
                    proba = proba * states_list[i][j][0]
                    one_state.append(states_list[i][j][1])
                end_states.append([proba, one_state])
            
        for i in range(len(end_states)):
            for j in range(len(common_final_state)):
                end_states[i][1].append(common_final_state[j])
                
        return end_states
        
                     
                    
def is_not_empty(case, move):
    not_empty = False
    if case[0] == move[3] and case[1] == move[4]:
        not_empty = True
    return not_empty
        
        
    
def result(case, nb_player_moved, player):
    """ we have a case [x, y nb_h, nb_v, nb_w] and we move nb_player_moved of 
    monsters of categories player in this case: this function return the new case as a tuple:
        (probability of this case, the case)"""
        
    if player == "vampires":
        modif = []
        if case[2]!=0:
            """battle human/vampires"""
            issues = battle_with_humans(nb_player_moved, case[2])
            for i in range(len(issues)):
                modif.append([issues[i][0], [case[0], case[1], issues[i][2], issues[i][1], 0]])
        elif case[3]!=0:
            """add vampires and vampires"""
            modif.append([1, [case[0], case[1], 0, case[3] + nb_player_moved, 0]])
        elif case[4]!=0:
            """battles vampires/werewolves"""
            issues = battle_with_monsters(nb_player_moved, case[4])
            for i in range(len(issues)):
                modif.append([issues[i][0], [case[0], case[1], 0, issues[i][1], issues[i][2]]])
        else:
            modif.append([1, [case[0], case[1], 0, nb_player_moved, 0]])
        return modif
    
    elif player == "werewolves":
        modif = []
        if case[2]!=0:
            issues = battle_with_humans(nb_player_moved, case[2])
            for i in range(len(issues)):
                modif.append([issues[i][0], [case[0], case[1], issues[i][2], 0, issues[i][1]]])
        elif case[4]!=0:
            modif.append([1, [case[0], case[1], 0, 0, case[4] + nb_player_moved]])
        elif case[3]!=0:
            issues = battle_with_monsters(nb_player_moved, case[3])
            for i in range(len(issues)):
                modif.append([issues[i][0], [case[0], case[1], 0, issues[i][2], issues[i][1]]])
        else:
            modif.append([1, [case[0], case[1], 0, 0, nb_player_moved]])
        return modif
            

    


def look_for_case(state_liste, x, y):
    for i in range(len(state_liste)):
        if state_liste[i][0] == x and state_liste[i][1] == y:
            return i
            

def cartesian_product(*arrays):
    cart_prod = []
    for element in itertools.product(*arrays):
        cart_prod.append(element)
    return cart_prod

def iterate_possibilities(nb_modifs_with_prob):
    liste = []
    for element in itertools.product('01', repeat=nb_modifs_with_prob):
        liste.append(list(element))
    for i in range(len(liste)):
        liste[i] = [int(x) for x in liste[i]]
    return liste
    
    


def battle_with_humans(E1,E2):
    """If battle with humans return each case possible as [proba, nb_monsters, nb_humans]"""
    if(E1 >= E2):
        return [[1, E2+E1, 0]]
    else:
        proba_win = E1/(2*E2)
        proba_lose = 1 - proba_win
        return [[proba_win, round(proba_win * (E1+E2)), 0], [proba_lose, 0, round(proba_lose * E2)]]


def battle_with_monsters(E1,E2):
    """If battle with humans return each case possible as [proba, nb_monsters1, nb_monsters2]"""
    if(E1 >= 1.5*E2):
        return [[1, E1, 0]]
    elif(E1 <= 0.666 * E2):
        return [[1, 0, E2]]
    elif(E1 == E2):
        proba = 0.5
        return [[0.5, round(0.5*E1), 0], [0.5, 0, round(0.5*E2)]]
    elif(E1 < E2):
        proba_win = E1/(2*E2)
        proba_lose = 1 - proba_win
        return [[proba_win, round(proba_win * E1), 0], [proba_lose, 0, round(proba_lose * E2)]]
    elif(E1 > E2):
        proba_win = (E1/E2)-0.5
        proba_lose = 1 - proba_win
        return [[proba_win, round(proba_win * E1), 0], [proba_lose, 0, round(proba_lose * E2)]]




#t1 = time.time()
#alpha = -10**99
#beta = 10**99  
#state = st.State([[0, 0, 0, 4, 0], [4, 1, 0, 0, 4], [9, 0, 3, 0, 0], [2, 3, 4, 0, 0], [5, 1, 0, 4, 0], [1, 4, 0, 0, 4]], 10, 5)           
#state2 = st.State( [[9, 0, 2, 0, 0], [4, 2, 0, 4, 0], [2, 2, 0, 11, 0], [9, 4, 2, 0, 0], [1, 4, 0, 4, 0] ] , 10, 5)           
#player = "vampires"
#moves  = [[[1, 0], [6,7,4,7,7]], [[0, 1], [4,2,5,4,1]], [[0, -1],[1,4,2,1,5]]]
#modifs = [[[0.75, [4, 1, 0, 4, 0]], [0.25, [4, 1, 0, 0, 1]]], [[0.65, [4, 1, 0, 4, 0]], [0.35, [4, 1, 0, 0, 1]]], [1, [7, 7, 0, 4, 0]], [1, [1, 5, 0, 2, 0]], [1, [4, 1, 0, 0, 4]], [1, [2, 3, 4, 0, 0]], [1, [5, 8, 0, 4, 0]], [1, [1, 4, 0, 2, 0]]]
#a = compute_successors(state, player)
#print(a)
##a = from_modifs_to_states(state, modifs)
#depth = 0
#depth_max = 4
##st_pre = preprocessing_before_alphabeta(state)
##b = max_value(st_pre, alpha, beta, player, depth, depth_max) 
##print(b)
#t2 = time.time()
#print(t2-t1)