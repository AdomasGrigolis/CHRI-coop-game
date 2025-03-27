#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import math, json, os, socket, struct, time
import threading
from queue import Queue
import pygame
from utils.convert_pos import convert_pos
from utils.thread_utils import client_networking_rec_thread, client_latency_thread
from utils.physics import Physics
import random
# Settings
config_set_path = os.path.join(os.path.dirname(__file__), "../config/settings.json")
config_usr_path = os.path.join(os.path.dirname(__file__), "../config/usr_settings.json")
config_sim_path = os.path.join(os.path.dirname(__file__), "../config/simulation.json")
image_path = os.path.join("assets", "beautiful-view-stars-night-sky.jpg")
image_asteroid = os.path.join("assets", "asteroidd.png")
font_path = os.path.join("assets", "Game Bubble.otf")
image_blackhole = os.path.join("assets", "blackhole.png")
image_warning = os.path.join("assets", "warning.png")
image_correct = os.path.join("assets", "correct.png")
image_wrong =os.path.join("assets", "wrong.png")

background = pygame.image.load(image_path)
asteroid = pygame.image.load(image_asteroid)
blackhole = pygame.image.load(image_blackhole)
warning = pygame.image.load(image_warning)
correct = pygame.image.load(image_correct)
wrong = pygame.image.load(image_wrong)

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
latency_port = settings["server"]["latency_port"]
buffer_size = settings["server"]["buffer_size"]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Hello", (server_ip, port))

# Latency socket
latency_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

# Haptic device initiate
device_connected = False
G_ff = np.diag([1, 1])
G_fb = np.diag([1, 1])
# Connect the device
if player_number == 1:
    physics = Physics(hardware_version=2)
    device_connected = physics.is_device_connected()
    if DEBUG: print(f"Device connected: {device_connected}")

# Pygame setup
pygame.init() # start pygame
window = pygame.display.set_mode(tuple(screen_size)) # create a window (size in pixels)
pygame.mouse.set_visible(False)  # Hide the mouse cursor
window.fill((255,255,255)) # white background
xc, yc = window.get_rect().center # window center
pygame.display.set_caption(f'Client {player_number}')
clock = pygame.time.Clock() # initialise clock
FPS =  cfg_usr["FPS"] # refresh rate

font = pygame.font.Font('freesansbold.ttf', 12) # printing text font and font size
text = font.render('Waiting for data', True, (0, 0, 0), (255, 255, 255)) # printing text object
textRect = text.get_rect()
textRect.topleft = (10, 10) # printing text position with respect to the top-left corner of the window

# SIMULATION PARAMETERS
dt = cfg_simulation['timeStep'] # simulation step time

# Simulation variables
pm = np.zeros(2)
player_1_pos = np.array([xc, yc])
player_2_pos = np.array([xc, yc])

# Queues and threads for networking
network_queue = Queue()
latency_queue = Queue()
network_thread = threading.Thread(target=client_networking_rec_thread, args=(sock, buffer_size, network_queue, DEBUG), daemon=True)
latency_thread_instance = threading.Thread(target=client_latency_thread, args=(latency_sock, buffer_size, server_ip, latency_port, latency_queue, 1.0, DEBUG), daemon=True)
network_thread.start()
latency_thread_instance.start()

TEXT_FONT = pygame.font.Font(font_path, 32)
title = TEXT_FONT.render(f'SPACE STATION SAVER!', True, (0, 255, 0))

#Initialize variables
force_vector = np.array([0, 0])
blackhole_positioned = True 
success = False
fail = False
score = 0
# MAIN LOOP
i = 0
t_server = 0.0
run = True
start_time = time.time()
last_timer_update = time.time()
while run:
    t = i * dt
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
                t_server, i_server, p1_x, p1_y, p2_x, p2_y,pobj_x, pobj_y,\
                rad_obj, \
                blackhole_x, blackhole_y, blackhole_positioned, \
                score1, success, fail, timer = struct.unpack('=fi2i2i2ii2ibiiii', data)
                player_1_pos, player_2_pos = np.array([p1_x, p1_y]), np.array([p2_x, p2_y])
                #if DEBUG: print(f"Received game state: {t}, {i_server}, {p1_x}, {p1_y}, {p2_x}, {p2_y}")
            except struct.error as e:
                if DEBUG: print(f"Failed to unpack binary data: {e}")

    
    # Event handling
    for event in pygame.event.get(): # interrupt function
        if event.type == pygame.QUIT: # force quit with closing the window
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_p:
                blackhole_positioned = False
            else:
                blackhole_positioned = True
            force += 10 if event.key == pygame.K_u else -10 if event.key == pygame.K_y else 0
            if event.key == ord(cfg_usr["keybinds"]["quit_game"]): # force quit with q button
                run = False
    
    # Haptic device force update
    if device_connected: #set forces only if the device is connected
        physics.update_force(G_fb @ force_vector)
    
    # Read mouse position
    # Haptic device position
    if device_connected:
        pA0,pB0,pA,pB,pE = physics.get_device_pos() #positions of the various points of the pantograph
        pm = convert_pos(pygame.display.get_surface().get_size(), settings["hardware_scale"], settings["vertical_offset"], pE) #convert the physical positions to screen coordinates
        pm = G_ff @ pm
    else:
        pm = np.array(pygame.mouse.get_pos())
    #if DEBUG: print(f"Mouse position: {pm}")

    # Send data to server
    if success:
        end_time = time.time()
        time_elapsed = end_time - start_time
        print('Time elapsed:', time_elapsed)
        blackhole_positioned = False
        success = False
        force = 0
        window.blit(correct, (0, 0))
        pygame.display.flip()
        pygame.time.delay(1000)
        background = pygame.image.load(image_path)
        asteroid = pygame.image.load(image_asteroid)
        blackhole = pygame.image.load(image_blackhole)
        warning = pygame.image.load(image_warning)
        correct = pygame.image.load(image_correct)
        wrong = pygame.image.load(image_wrong)
        score += 1
        start_time = time.time()
    
    if fail:
        blackhole_positioned = False
        fail = False
        force = 0
        window.blit(wrong, (0, 0))
        pygame.display.flip()
        pygame.time.delay(1000)
        background = pygame.image.load(image_path)
        asteroid = pygame.image.load(image_asteroid)
        blackhole = pygame.image.load(image_blackhole)
        warning = pygame.image.load(image_warning)
        correct = pygame.image.load(image_correct)
        wrong = pygame.image.load(image_wrong)
        score += 0

    
    packed_data = bytearray(struct.pack("=2ib", pm[0], pm[1], int(blackhole_positioned)))
    if DEBUG: print(blackhole_positioned)
    sock.sendto(packed_data, (server_ip, port))
    #print('x_object:', pobj_x)
    # Rendering
    # Load the background image (adjust the file path to your actual image path)
    window.fill((255, 255, 255))  # Clear window

    window_width, window_height = window.get_size()
    background = pygame.transform.scale(background, (window_width, window_height))
    correct = pygame.transform.scale(correct, (window_width, window_height))
    wrong = pygame.transform.scale(wrong, (window_width, window_height))
    
    scale_factor = 2.2
    asteroid = pygame.transform.scale(asteroid, (rad_obj*scale_factor, rad_obj*scale_factor))
     # Blit the background image first (ensure it's drawn before other elements)
    window.blit(background, (0, 0))  # Position (0, 0) means the top-left corner of the window
    window.blit(title, (window_width/2, 0))
    asteroid_position_x = pobj_x - 1/2 *rad_obj*scale_factor
    asteroid_position_y = pobj_y - 1/2 *rad_obj*scale_factor
    window.blit(asteroid, (asteroid_position_x , asteroid_position_y))

    pygame.draw.circle(window, (0, 255, 0), pm, 10)
    pygame.draw.circle(window, (255, 0, 0), player_1_pos, 15)
    pygame.draw.circle(window, (0, 0, 255), player_2_pos, 15)
    
    # Add force meter
    force_meter_bg = pygame.Rect(10, 25, 200, 20)  # Background rectangle
    force_meter_fill = pygame.Rect(10, 25, np.linalg.norm(force_vector) * 2, 20)  # Foreground rectangle that changes with force
    pygame.draw.rect(window, (200, 200, 200), force_meter_bg)  # Draw background (light gray)
    if 0<np.abs(np.linalg.norm(force_vector)) <25: 
        pygame.draw.rect(window, (0, 255, 0), force_meter_fill)  # Draw fill (green)
    elif 25<np.abs(np.linalg.norm(force_vector)) <50:
        pygame.draw.rect(window, (255, 255, 0), force_meter_fill)  # Draw fill (YELLOW)

    elif 50 <= np.abs(np.linalg.norm(force_vector)):
        warning = pygame.transform.scale(warning, (50, 50))
        window.blit(warning, (pm[0], pm[1]))
        pygame.draw.rect(window, (255, 0, 0), force_meter_fill)
        #if high_force_start_time == 0:
        #    high_force_start_time = pygame.time.get_ticks()

        #current_time = pygame.time.get_ticks()
        #if (current_time - high_force_start_time) / 1000 >= force_threshold_time:
            #fail = True
    
    if timer != 3:
        countdown = TEXT_FONT.render(f'{timer}', True, (255, 255, 0))  
        window.blit(countdown, (asteroid_position_x, asteroid_position_y))
    if timer == 0:
        countdown = TEXT_FONT.render(f'SUCCES!', True, (255, 255, 0))
        window.blit(countdown, (asteroid_position_x, asteroid_position_y))
    

    if DEBUG: print('FORCE IS NOW:', force)
    #pygame.draw.circle(window, (0, 255, 255), (pobj_x, pobj_y), rad_obj) #Object 

    #add blackhole
    blackhole = pygame.transform.scale(blackhole, (rad_obj*scale_factor, rad_obj*scale_factor))

    # Generate random x and y coordinates within the window
    window.blit(blackhole, (blackhole_x, blackhole_y))
    
    if DEBUG: print('score:', score)


    # add score

    score_text = TEXT_FONT.render(f'SCORE: {score}/10', True, (0, 255, 255))
    window.blit(score_text, (10, 45) )

    # Latency
    if not latency_queue.empty():
        latency = latency_queue.get()
        text = font.render("Ping: " + str(round(latency, 2)) + " ms" + " FPS: " + str(round(clock.get_fps())), True, (0, 0, 0), (255, 255, 255))
    window.blit(text, textRect)

    # Update pygame
    pygame.display.flip() # update display
    clock.tick(FPS)

    i += 1

    if run == False:
        if DEBUG: print("Closing client...")
        sock.close()
        break
