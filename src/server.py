#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import math, json, os, socket, struct, time
import threading
from queue import Queue
import matplotlib.pyplot as plt
import pygame
import pymunk, pymunk.pygame_util

from utils.pymunk_simple_objects import *

# Settings
config_set_path = os.path.join(os.path.dirname(__file__), "../config/settings.json")
config_sim_path = os.path.join(os.path.dirname(__file__), "../config/simulation.json")
with open(config_set_path, "r") as file:
    settings = json.load(file)
with open(config_sim_path, "r") as file:
    cfg_simulation = json.load(file)

# Debug
DEBUG = settings["server"]["debug"]
if DEBUG:
    print("Debug mode enabled")
    print("Configuration loaded")

screen_size = [settings['screen_size']['width'], settings['screen_size']['height']]

# Socket
players = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ip = settings["server"]["ip"]
port = settings["server"]["port"]
buffer_size = settings["server"]["buffer_size"]
sock.bind((server_ip, port))
sock.setblocking(False)

# Lobby
print(f"Server started on {server_ip}:{port}, waiting for players...")

while len(players) < 2:
    try:
        _, addr = sock.recvfrom(buffer_size)

        # Check if player already joined (avoid duplicate entries)
        if addr in players.values():
            continue

        # Assign player number automatically
        player_number = 1 if 1 not in players else 2
        players[player_number] = addr

        # Send assigned number to the player
        send_data = bytearray(struct.pack('=1i', player_number))
        sock.sendto(f"{player_number}".encode(), addr)
        if DEBUG: print(f"Sent player number {player_number} to {addr}")
        print(f"Player {player_number} joined from {addr}")
    except socket.error:
        pass
    time.sleep(0.5)

print("Both players joined. Starting game...")
for player in players.values():
    sock.sendto(b"Game Start", player)
    if DEBUG: print(f"Sent Game Start to {player}")

'''SIMULATION'''

# SIMULATION PARAMETERS
dt = cfg_simulation['timeStep'] # simulation step time

# initialise real-time plot with pygame
pygame.init() # start pygame
window = pygame.display.set_mode(tuple(screen_size)) # create a window (size in pixels)
window.fill((255,255,255)) # white background
xc, yc = window.get_rect().center # window center
pygame.display.set_caption('Server')

font = pygame.font.Font('freesansbold.ttf', 12) # printing text font and font size
text = font.render('test', True, (0, 0, 0), (255, 255, 255)) # printing text object
textRect = text.get_rect()
textRect.topleft = (10, 10) # printing text position with respect to the top-left corner of the window

clock = pygame.time.Clock() # initialise clock
FPS = int(1/dt) # refresh rate

# initial conditions
t = 0.0 # time
pm1 = np.zeros(2) # mouse position player 1
pm2 = np.zeros(2) # mouse position player 2
p1 = np.zeros(2) # actual endpoint position player 1
p2 = np.zeros(2) # actual endpoint position player 2
dp1 = np.zeros(2) # actual endpoint velocity
dp2 = np.zeros(2) # actual endpoint velocity
pr1 = np.zeros(2) # reference endpoint position player 1
pr2 = np.zeros(2) # reference endpoint position player 2
f1 = np.zeros(2) # endpoint force player 1
f2 = np.zeros(2) # endpoint force player 2
p_prev1 = np.zeros(2) # previous endpoint position player 1
p_prev2 = np.zeros(2) # previous endpoint position player 2
i = 0 # loop counter
current_state = []
state = [] # state vector

# Pymunk
space = pymunk.Space()
space.gravity = (0, int(100 * cfg_simulation['gravity']))

init_object_pos = list(np.array(screen_size) * np.array(cfg_simulation['object']['init_position']))
object_mass = cfg_simulation['object']['mass']
ball = create_ball(space, init_object_pos, mass=object_mass)
floor = create_static_wall(space, (400, 580))

# Initial impulse
initial_impulse = pymunk.Vec2d(cfg_simulation['object']['init_impulse']["x"], cfg_simulation['object']['init_impulse']["y"])

# Pymunk-pygame
draw_options = pymunk.pygame_util.DrawOptions(window)

def networking_thread(sock, buffer_size, network_queue, players):
    while True:
        try:
            # Receive data from players
            data, addr = sock.recvfrom(buffer_size)
            
            # Check if the player is already registered
            if addr not in players.values():
                continue
            
            # Add received data to the queue
            network_queue.put((data, addr))
        except socket.error:
            pass

network_queue = Queue()
print("Starting networking thread...")
network_thread = threading.Thread(target=networking_thread, args=(sock, buffer_size, network_queue, players), daemon=True)
network_thread.start()

# MAIN LOOP
i = 0
run = True
while run:
    for event in pygame.event.get(): # interrupt function
        if event.type == pygame.QUIT: # force quit with closing the window
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord(settings["server"]["keybinds"]["quit_serv"]): # force quit with q button
                run = False
            elif event.key == ord(settings["server"]["keybinds"]["start_sim"]):  # Apply force when spacebar is pressed
                #ball.body.apply_force_at_local_point(initial_impulse, (0, 0))
                ball.body.velocity = initial_impulse

    # Simulation
    # Process data from players
    while not network_queue.empty():
        data, addr = network_queue.get()
        pm = np.array(struct.unpack('=2i', data))

        # Update the correct player's mouse position
        if addr == players[1]:  # Player 1
            pm1 = pm
        elif addr == players[2]:  # Player 2
            pm2 = pm
    # Print current position
    print(pm1, pm2)

    # save state
    current_state = [t, pm1, pm2, p1, p2, dp1, dp2, pr1, pr2, f1, f2, p_prev1, p_prev2]
    # log states for analysis
    #state.append(current_state)
    
    # integration
    #ddp = F/m
    #dp += ddp*dt
    #p += dp*dt
    #t += dt

    # increase loop counter
    i = i + 1
    
    # real-time plotting
    window.fill((255,255,255)) # clear window
    
    # print data
    text = font.render("FPS = " + str( round( clock.get_fps() ) ), True, (0, 0, 0), (255, 255, 255))
    window.blit(text, textRect)
    
    space.step(1/FPS)
    space.debug_draw(draw_options)
    pygame.display.flip() # update display
    
    # try to keep it real time with the desired step time
    clock.tick(FPS)
    
    if run == False:
        # Shutdown command
        for player in players.values():
            sock.sendto(b"shutdown", player)
            if DEBUG: print(f"Sent shutdown to {player}")
        print("Server shutdown")
        sock.close()
        break

pygame.quit() # stop pygame
