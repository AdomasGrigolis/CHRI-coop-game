#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import math, json, os, socket, struct, time
import threading
from queue import Queue
import pygame
from utils.convert_pos import convert_pos

# Settings
config_set_path = os.path.join(os.path.dirname(__file__), "../config/settings.json")
config_usr_path = os.path.join(os.path.dirname(__file__), "../config/usr_settings.json")
config_sim_path = os.path.join(os.path.dirname(__file__), "../config/simulation.json")
with open(config_set_path, "r") as file:
    settings = json.load(file)
with open(config_sim_path, "r") as file:
    cfg_simulation = json.load(file)
with open(config_usr_path, "r") as file:
    cfg_usr = json.load(file)

# Debug
DEBUG = settings["debug"]
if DEBUG: print("Debug mode enabled")

screen_size = [settings['screen_size']['width'], settings['screen_size']['height']]

# Lobby arbitration
server_ip = settings["server"]["ip"]
port = settings["server"]["port"]
buffer_size = settings["server"]["buffer_size"]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Hello", (server_ip, port))

running = True
while running:
    try:
        data, addr = sock.recvfrom(buffer_size)
        if "Game Start" in data.decode():
            running = False
        elif data.decode() in ['1', '2']:
            player_number = int(data.decode())
            if DEBUG: print(f"Received player number: {player_number}")

    except socket.error:
        pass

    time.sleep(0.5)

# Pygame setup
pygame.init() # start pygame
window = pygame.display.set_mode(tuple(screen_size)) # create a window (size in pixels)
window.fill((255,255,255)) # white background
xc, yc = window.get_rect().center # window center
pygame.display.set_caption(f'Client {player_number}')
clock = pygame.time.Clock() # initialise clock
FPS =  cfg_usr["FPS"] # refresh rate

# SIMULATION PARAMETERS
dt = cfg_simulation['timeStep'] # simulation step time

# Simulation variables
pm = np.zeros(2)
self_pos = np.array([xc, yc])
opponent_pos = np.array([xc, yc])

def networking_thread(sock, buffer_size, network_queue):
    while True:
        try:
            data, addr = sock.recvfrom(buffer_size)
            network_queue.put((data, addr))  # Add received data to the queue
        except socket.error:
            pass

network_queue = Queue()
network_thread = threading.Thread(target=networking_thread, args=(sock, buffer_size, network_queue), daemon=True)
network_thread.start()

# MAIN LOOP
i = 0
run = True
while run:
    # Receive data from server
    while not network_queue.empty():
        data, addr = network_queue.get()
        try:
            message = data.decode()
            if message == "shutdown":
                if DEBUG: print("Server shutdown")
                run = False
        except UnicodeDecodeError:
            try:
                t, i_server, p1_x, p1_y, p2_x, p2_y = struct.unpack('=fi2i2i', data)
                self_pos = np.array([p1_x, p1_y])
                opponent_pos = np.array([p2_x, p2_y])
                if DEBUG: print(f"Received game state: {t}, {i_server}, {p1_x}, {p1_y}, {p2_x}, {p2_y}")
            except struct.error as e:
                if DEBUG: print(f"Failed to unpack binary data: {e}")

    
    # Event handling
    for event in pygame.event.get(): # interrupt function
        if event.type == pygame.QUIT: # force quit with closing the window
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord(cfg_usr["keybinds"]["quit_game"]): # force quit with q button
                run = False
    
    # Read mouse position
    pm = np.array(pygame.mouse.get_pos())
    #if DEBUG: print(f"Mouse position: {pm}")

    # Send data to server
    packed_data = bytearray(struct.pack("=2i", pm[0], pm[1]))
    sock.sendto(packed_data, (server_ip, port))

    # Rendering
    window.fill((255,255,255)) # clear window
    pygame.draw.circle(window, (0, 255, 0), self_pos, 5) 
    pygame.draw.circle(window, (0, 0, 255), opponent_pos, 5) 

    # Update pygame
    pygame.display.flip() # update display
    clock.tick(FPS)

    i += 1

    if run == False:
        if DEBUG: print("Closing client...")
        sock.close()
        break
