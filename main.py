# -*- coding: UTF-8 -*-

import argparse
import socket
import struct
import time
import state as st
import alpha_beta as ab
import alpha_beta_2 as ab2
import sys

#HOST = "138.195.205.141"
try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
except:
    HOST = "localhost"
    PORT = "5555" 

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("port")

#args = parser.parse_args()


def receive_data(sock, size, fmt):
    data = bytes()
    while len(data) < size:
        data += sock.recv(size - len(data))
    return struct.unpack(fmt, data)
       

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, int(PORT)))

# NME
sock.send("NME".encode("ascii"))
sock.send(struct.pack("1B",  3))
sock.send('LJM'.encode("ascii"))

# SET
header = sock.recv(3).decode("ascii")
if header != "SET":
    print("Protocol Error at SET")
else:
    (height, width)= receive_data(sock, 2, "2B")

# HUM
header = sock.recv(3).decode("ascii")
if header != "HUM":
    print("Protocol Error at HUM")
else:
    number_of_homes = receive_data(sock, 1, "1B")[0]
    homes_raw = receive_data(sock, number_of_homes * 2, "{}B".format(number_of_homes * 2))
    
# HME
header = sock.recv(3).decode("ascii")
if header != "HME":
    print("Protocol Error at HME")
else:
    start_position = tuple(receive_data(sock, 2, "2B"))

# MAP
header = sock.recv(3).decode("ascii")
if header != "MAP":
    print("Protocol Error at MAP")
else:
    number_map_commands = receive_data(sock,1, "1B")[0]
    map_commands_raw = receive_data(sock, number_map_commands * 5, "{}B".format(number_map_commands * 5))

 
    
initial_state = st.State(st.split_in_chunks(map_commands_raw), width, height)  
#l'état reçu par map est le tout premier état du systeme.
#Il est contenu dans map_commands_raw

player = st.get_player(start_position, initial_state)
intermediary_state = initial_state


# get the good player (in start_position)
entree = True


while entree:
    reply = sock.recv(3)
    if not reply:   
        time.sleep(0.02)
        
    elif reply.decode("ascii") == "END" or reply.decode("ascii") == "BYE":
        entree = False
    
    else:
        # UPD
        header = reply.decode("ascii")
        if header != "UPD":
            print("Protocol Error at UPD")
        else:
            print("received UPD")
            number_upd_commands = receive_data(sock,1, "1B")[0]
            upd_commands_raw = receive_data(sock, number_upd_commands * 5, "{}B".format(number_upd_commands * 5))
        
            
        
            #obtention de l'etat intermediaire de la carte
            modifications = st.split_in_chunks(upd_commands_raw)
            intermediary_state = intermediary_state.new_state(modifications)
 
            # MOV        
            ########## HERE RESULTS MOVES WANT"""" 
            alpha = -10**99
            beta = 10**99 
            depth = 0
            depth_max = 4
            
            if depth_max == 2:
                list_movements = ab.compute_best_direction(intermediary_state, alpha, beta, player, depth, depth_max)
            else:
                list_movements = ab2.compute_best_direction(intermediary_state, alpha, beta, player, depth, depth_max)
            

    
    #list_movements = ab.direction_only_zero(intermediary_state, player)
            
    
            NUMBEROFMOVESTOPERFORM = len(list_movements)
            print(player)
            sock.send("MOV".encode("ascii"))
            sock.send(struct.pack("1B",  NUMBEROFMOVESTOPERFORM))
            for i in range(NUMBEROFMOVESTOPERFORM):
                for j in range(5):
                    sock.send(struct.pack("1B",  list_movements[i][j])) 