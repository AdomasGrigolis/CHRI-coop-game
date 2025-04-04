#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import json, os, time
import socket, struct, threading
from queue import Queue
import pygame
from utils.physics import Physics
from utils.convert_pos import convert_pos
from utils.thread_utils import client_networking_rec_thread, client_latency_thread
from utils.create_arm import draw_arm_segment

# Link dimensions
LINK_WIDTH = 5
LINK_LENGTH_1 = 200  # This should match your arm segment length
LINK_LENGTH_2 = 200
JOINT_RADIUS = 8
END_EFFECTOR_WIDTH = 20
END_EFFECTOR_HEIGHT = 80
# Define colors (RGB)
BLUE = (0, 0, 255)         # Arm 1 Link 1
GREEN = (0, 255, 0)        # Arm 1 Link 2
RED = (255, 0, 0)          # End Effector 1
PURPLE = (128, 0, 128)     # Arm 2 Link 1
ORANGE = (255, 165, 0)     # Arm 2 Link 2
YELLOW = (255, 255, 0)     # End Effector 2

# Settings
config_set_path = os.path.join(os.path.dirname(__file__), "../config/settings.json")
config_usr_path = os.path.join(os.path.dirname(__file__), "../config/usr_settings.json")
config_sim_path = os.path.join(os.path.dirname(__file__), "../config/simulation.json")
# Assets
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

# Screen parameters
screen_size = [settings['screen_size']['width'], settings['screen_size']['height']]

# SIMULATION PARAMETERS
dt = cfg_simulation['timeStep'] # simulation step time
max_force = cfg_simulation["max_force"]

# Haptic device parameters
force_scale = settings["haptic_device"]["force_scale"]
hardware_scale = settings["haptic_device"]["hardware_scale"]
vertical_offset = settings["haptic_device"]["vertical_offset"]
device_connected = False

# Lobby arbitration
server_ip = settings["server"]["ip"]
port = settings["server"]["port"]
latency_port = settings["server"]["latency_port"]
buffer_size = settings["server"]["buffer_size"]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Hello", (server_ip, port))

# Latency socket
latency_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Lobby loop
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
G_ff = np.diag([1, 1])
G_fb = np.diag([1 / max_force * force_scale, 1 / max_force * force_scale])
# Connect the device
if player_number == 1:
    physics = Physics(hardware_version=2)
    device_connected = physics.is_device_connected()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "900,50"
    if DEBUG: print(f"Device connected: {device_connected}")
if player_number == 2:
    os.environ['SDL_VIDEO_WINDOW_POS'] = "50,50"

# Pygame setup
pygame.init() # start pygame
window = pygame.display.set_mode(tuple(screen_size)) # create a window (size in pixels)
pygame.display.set_icon(asteroid) # application icon
pygame.mouse.set_visible(False)  # Hide the mouse cursor
window.fill((255,255,255)) # white background
xc, yc = window.get_rect().center # window center
pygame.display.set_caption(f'Space Station Saver - Client {player_number}') # window name
clock = pygame.time.Clock() # initialise clock
FPS =  cfg_usr["FPS"] # refresh rate
font = pygame.font.Font('freesansbold.ttf', 12) # printing text font and font size
text = font.render('Waiting for data', True, (0, 0, 0), (255, 255, 255)) # printing text object
textRect = text.get_rect()
textRect.topleft = (10, 10) # printing text position with respect to the top-left corner of the window
TEXT_FONT = pygame.font.Font(font_path, 32)
title = TEXT_FONT.render(f'SPACE STATION SAVER!', True, (0, 255, 0))

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

#Initialize variables
force_vector = np.array([0, 0])
success = False
fail = False
score = 0
i = 0
t_server = 0.0
run = True
start_time = time.time()
last_timer_update = time.time()
# MAIN LOOP
while run:
    t = i * dt
    # Receive data from server
    while not network_queue.empty():
        data, addr = network_queue.get()
        try: # shutdown command
            message = data.decode()
            if message == "shutdown":
                if DEBUG: print("Server shutdown")
                run = False
        except UnicodeDecodeError: # binary data
            try:
                t_server, i_server, \
                p1_x, p1_y, p2_x, p2_y, pobj_x, pobj_y,\
                rad_obj, blackhole_x, blackhole_y, \
                score, success, fail, timer, \
                force_vector1_x, force_vector1_y, force_vector2_x, force_vector2_y, \
                arm1_link1_x, arm1_link1_y, arm1_link2_x, arm1_link2_y, \
                arm2_link1_x, arm2_link1_y, arm2_link2_x, arm2_link2_y, \
                end_effector1_x, end_effector1_y, end_effector2_x, end_effector2_y \
                = struct.unpack('=fi2i2i2ii2iiiii2f2f2f2f2f2f2f2f', data)
                # parse received data
                player_1_pos, player_2_pos = np.array([p1_x, p1_y]), np.array([p2_x, p2_y])
                if player_number == 1: force_vector = np.array([force_vector1_x, force_vector1_y])
                else: force_vector = np.array([force_vector2_x, force_vector2_y])
            except struct.error as e:
                if DEBUG: print(f"Failed to unpack binary data: {e}")

    
    # Pygame event handling
    for event in pygame.event.get(): # interrupt function
        if event.type == pygame.QUIT: # force quit with closing the window
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord(cfg_usr["keybinds"]["quit_game"]): # force quit with q button
                run = False
    
    # Haptic device force update
    if device_connected: #set forces only if the device is connected
        physics.update_force(G_fb @ - force_vector)
    
    # Read mouse position
    # Haptic device position
    if device_connected:
        pA0,pB0,pA,pB,pE = physics.get_device_pos() #positions of the various points of the pantograph
        pm = convert_pos(pygame.display.get_surface().get_size(), hardware_scale, vertical_offset, pE) #convert the physical positions to screen coordinates
        pm = G_ff @ pm # apply position scaling
    else: # mouse position
        pm = np.array(pygame.mouse.get_pos())

    # Success/Fail conditions
    if success:
        window.blit(correct, (0, 0))
        pygame.display.flip()
        pygame.time.delay(1000)
        background = pygame.image.load(image_path)
        asteroid = pygame.image.load(image_asteroid)
        blackhole = pygame.image.load(image_blackhole)
        warning = pygame.image.load(image_warning)
        correct = pygame.image.load(image_correct)
        wrong = pygame.image.load(image_wrong)
        start_time = time.time()
    
    if fail:
        window.blit(wrong, (0, 0))
        pygame.display.flip()
        #pygame.time.delay(1000)
        background = pygame.image.load(image_path)
        asteroid = pygame.image.load(image_asteroid)
        blackhole = pygame.image.load(image_blackhole)
        warning = pygame.image.load(image_warning)
        correct = pygame.image.load(image_correct)
        wrong = pygame.image.load(image_wrong)

    # Send data to server
    packed_data = bytearray(struct.pack("=2i", pm[0], pm[1]))
    sock.sendto(packed_data, (server_ip, port))

    # Rendering
    # Load the background image (adjust the file path to your actual image path)
    window.fill((255, 255, 255))  # Clear window

    background = pygame.transform.scale(background, screen_size)
    correct = pygame.transform.scale(correct, screen_size)
    wrong = pygame.transform.scale(wrong, screen_size)
    
    scale_factor = 2.2
    asteroid = pygame.transform.scale(asteroid, (rad_obj*scale_factor, rad_obj*scale_factor))
    # Blit the background image first (ensure it's drawn before other elements)
    window.blit(background, (0, 0))  # Position (0, 0) means the top-left corner of the window
    window.blit(title, (screen_size[0]/2, 0))
    asteroid_position_x = pobj_x - 1/2 *rad_obj*scale_factor
    asteroid_position_y = pobj_y - 1/2 *rad_obj*scale_factor
    window.blit(asteroid, (asteroid_position_x , asteroid_position_y))

    pygame.draw.circle(window, (0, 255, 0), pm, 10)
    pygame.draw.circle(window, (255, 0, 0), player_1_pos, 15)
    pygame.draw.circle(window, (0, 0, 255), player_2_pos, 15)
    
    # Add force meter
    force_meter_bg = pygame.Rect(10, 25, 200, 20)  # Background rectangle

    # Force normalisation
    # Normalize the force vector to fit within the meter
    normalized_force = min(np.linalg.norm(force_vector) / max_force, 1.0)  # Clamp to [0, 1]
    force_meter_fill_width = int(normalized_force * 200)  # Scale to meter width (200 pixels)

    force_meter_fill = pygame.Rect(10, 25, force_meter_fill_width, 20)
    max_force_line_x = 10 + 200 
    pygame.draw.line(window, (255, 0, 0), (max_force_line_x, 25), (max_force_line_x, 45), 2)

    if normalized_force < 0.25: 
        pygame.draw.rect(window, (0, 255, 0), force_meter_fill)  # Draw fill (green)
    elif 0.25 <= normalized_force < 0.5:
        pygame.draw.rect(window, (255, 255, 0), force_meter_fill)  # Draw fill (yellow)
    else:
        warning = pygame.transform.scale(warning, (50, 50))
        window.blit(warning, (pm[0], pm[1]))
        pygame.draw.rect(window, (255, 0, 0), force_meter_fill)  # Draw fill (red)
    
    if timer != 3:
        countdown = TEXT_FONT.render(f'{timer}', True, (255, 255, 0))  
        window.blit(countdown, (asteroid_position_x, asteroid_position_y))
    if timer == 0:
        countdown = TEXT_FONT.render(f'SUCCES!', True, (255, 255, 0))
        window.blit(countdown, (asteroid_position_x, asteroid_position_y))

    # Get base positions (these would be fixed based on your setup)
    arm1_base_x, arm1_base_y = xc-350, yc  # Use the actual base coordinates from your setup
    arm2_base_x, arm2_base_y = xc+350, yc  # Use the actual base coordinates from your setup

    # Draw complete arms with both links
    # Arm 1
    draw_arm_segment(window, (arm1_base_x, arm1_base_y), (arm1_link1_x, arm1_link1_y), LINK_WIDTH, RED)
    draw_arm_segment(window, (arm1_link1_x, arm1_link1_y), (arm1_link2_x, arm1_link2_y), LINK_WIDTH, RED)
    draw_arm_segment(window, (arm1_link2_x, arm1_link2_y), (end_effector1_x, end_effector1_y), LINK_WIDTH, RED)

    # Arm 2
    draw_arm_segment(window, (arm2_base_x, arm2_base_y), (arm2_link1_x, arm2_link1_y), LINK_WIDTH, BLUE)
    draw_arm_segment(window, (arm2_link1_x, arm2_link1_y), (arm2_link2_x, arm2_link2_y), LINK_WIDTH, BLUE)
    draw_arm_segment(window, (arm2_link2_x, arm2_link2_y), (end_effector2_x, end_effector2_y), LINK_WIDTH, BLUE)

    # Draw end effectors as squares
    # Draw end effectors as rectangles
    # For end effector 1
    pygame.draw.rect(window, RED, 
                    (end_effector1_x - END_EFFECTOR_WIDTH//2, 
                    end_effector1_y - END_EFFECTOR_HEIGHT//2, 
                    END_EFFECTOR_WIDTH, END_EFFECTOR_HEIGHT))

    # For end effector 2
    pygame.draw.rect(window, BLUE, 
                    (end_effector2_x - END_EFFECTOR_WIDTH//2, 
                    end_effector2_y - END_EFFECTOR_HEIGHT//2, 
                    END_EFFECTOR_WIDTH, END_EFFECTOR_HEIGHT))


    # Draw blackhole
    blackhole = pygame.transform.scale(blackhole, (rad_obj*scale_factor, rad_obj*scale_factor))
    # Calculate the top-left corner to center the black hole at (blackhole_x, blackhole_y)
    blackhole_width, blackhole_height = blackhole.get_size()
    top_left_x = blackhole_x - blackhole_width // 2
    top_left_y = blackhole_y - blackhole_height // 2

    # Draw the black hole
    window.blit(blackhole, (top_left_x, top_left_y))
    
    if DEBUG: print('score:', score)
    # score

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
