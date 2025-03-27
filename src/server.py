## !/usr/bin/env python3
## -*- coding: utf-8 -*-
import numpy as np
import math, json, os, socket, struct, time
import threading
from queue import Queue
import matplotlib.pyplot as plt
import pygame
import pymunk, pymunk.pygame_util
from utils.thread_utils import server_networking_thread, server_latency_thread
from utils.post_collision import post_collision, latest_impulse, player_collisions, ensure_no_overlap
from utils.create_arm import create_arm
import random
from utils.pymunk_simple_objects import *
from utils.append_to_csv import append_to_csv
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

# Latency socket
latency_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
latency_port = settings["server"]["latency_port"]  # Define a separate port for latency
latency_sock.bind((server_ip, latency_port))

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
window_width, window_height = window.get_size()
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
score = 0
# Pymunk
space = pymunk.Space()
space.gravity = (0, int(100 * cfg_simulation['gravity']))

init_object_pos = list(np.array(screen_size) * np.array(cfg_simulation['object']['init_position']))
object_mass = cfg_simulation['object']['mass']

ball = create_ball(space, init_object_pos, mass=100000, radius=random.randint(30, 100))
floor = create_static_wall(space, (400, 580))
arm1_link1, arm1_link2, end_effector_shape1 = create_arm(space, (xc-350, yc), 250, 200)
arm2_link1, arm2_link2, end_effector_shape2 = create_arm(space, (xc+350, yc), 250, 200)
#create_arm(space, (xc, yc), 150, 100)

# Create mouse circles
# circle1_shape = create_ball(space, tuple(p1), radius=10, mass=10)
# circle1_shape.color = (255, 0, 0, 255)
# circle1_shape.filter = pymunk.ShapeFilter(group=1)  # Add this line
end_effector_shape1.color = (255, 0, 0, 255)
end_effector_shape1.filter = pymunk.ShapeFilter(group=1)  # Add this line
mouse_body1 = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
mouse_joint1 = pymunk.PivotJoint(arm1_link2, mouse_body1, (200, 0), (0, 0))  # 100 是 arm2 的长度
mouse_joint1.max_force = 100000  # the force of following
mouse_joint1.error_bias = 0.01   # the smoothness of following
space.add(mouse_body1, mouse_joint1)

# circle2_shape = create_ball(space, tuple(p2), radius=10, mass=10)
# circle2_shape.color = (255, 255, 0, 0)
# circle2_shape.filter = pymunk.ShapeFilter(group=2)  # Add this line
end_effector_shape2.color = (255, 255, 0, 0)
end_effector_shape2.filter = pymunk.ShapeFilter(group=2)  # Add this line
mouse_body2 = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
mouse_joint2 = pymunk.PivotJoint(arm2_link2, mouse_body2, (200, 0), (0, 0))  # 100 是 arm2 的长度
mouse_joint2.max_force = 100000  # the force of following
mouse_joint2.error_bias = 0.01   # the smoothness of following
space.add(mouse_body2, mouse_joint2)


##ball.filter = pymunk.ShapeFilter(group=3)  # Assuming ball is the asteroid

circle1_type = 1
circle2_type = 2
ball_type = 3

# Assign these types to your shapes
end_effector_shape1.collision_type = circle1_type
end_effector_shape2.collision_type = circle2_type
##ball.collision_type = ball_type

# Create a collision handler
handler1 = space.add_collision_handler(circle1_type, ball_type)
handler1.post_solve = post_collision
handler2 = space.add_collision_handler(circle2_type, ball_type)
handler2.post_solve = post_collision

#Initial blackhole
blackhole_positioned = False

# Initial impulse
initial_impulse = pymunk.Vec2d(cfg_simulation['object']['init_impulse']["x"], cfg_simulation['object']['init_impulse']["y"])

# Pymunk-pygame
draw_options = pymunk.pygame_util.DrawOptions(window)

network_queue = Queue()
network_thread = threading.Thread(target=server_networking_thread, args=(sock, buffer_size, network_queue, players, DEBUG), daemon=True)
latency_thread_instance = threading.Thread(target=server_latency_thread, args=(latency_sock, buffer_size, DEBUG), daemon=True)
network_thread.start()
latency_thread_instance.start()

#initialize variables
fail = False
success = False
high_force_start_time = 0
force_threshold_time = 5  # 5 seconds
timer = 3 
# MAIN LOOP
i = 0
start_time = time.time()
last_timer_update = time.time()
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
            force += 10 if event.key == pygame.K_c else -10 if event.key == pygame.K_y else 0
            success = True if event.key == pygame.K_x else False
            fail = True if event.key == pygame.K_z else False

    # Simulation
    # Process data from players
    while not network_queue.empty():
        data, addr = network_queue.get()
        pm = np.zeros(2)
        pm[0],pm[1], blackhole_positioned = np.array(struct.unpack('=2ib', data))

        # Update the correct player's mouse position
        if addr == players[1]:  # Player 1
            pm1 = pm
        elif addr == players[2]:  # Player 2
            pm2 = pm
    # Print current position
    #print(pm1, pm2)

    # save state
    current_state = [t, pm1, pm2, p1, p2, dp1, dp2, pr1, pr2, f1, f2, p_prev1, p_prev2]
    # log states for analysis
    #state.append(current_state)
    p1 = pm1
    p2 = pm2
    # Create random goal position
    if not blackhole_positioned:
        blackhole_x = random.randint(0, window_width - 220) #220 is blackhole height and width
        blackhole_y = random.randint(0, window_height - 220)
        score += 1
        space.remove(ball.body, ball)
        ball = create_ball(space, init_object_pos, mass=random.randint(100, 1000), radius=random.randint(30, 100))
        blackhole_positioned = True


    # Update circle for mouse position
    mouse_body1.position = tuple(p1)

    mouse_body2.position = tuple(p2)
    if latest_impulse[0] != 0 or latest_impulse[1] != 0:
        print(f"Latest collision impulse: {latest_impulse}")

    # Update circle for mouse position
    overlap1 = ensure_no_overlap(end_effector_shape1, ball)
    overlap2 = ensure_no_overlap(end_effector_shape2, ball)
    if overlap1:
        p1 = np.array(end_effector_shape1.body.position)
    if overlap2:
        p2 = np.array(end_effector_shape2.body.position)
    # Get positions
    arm1_link1_x, arm1_link1_y = arm1_link1.position
    arm1_link2_x, arm1_link2_y = arm1_link2.position

    arm2_link1_x, arm2_link1_y = arm2_link1.position
    arm2_link2_x, arm2_link2_y = arm2_link2.position
    # Get end effector positions
    end_effector1_position_x, end_effector1_position_y = end_effector_shape1.body.position
    end_effector2_position_x, end_effector2_position_y = end_effector_shape2.body.position
    
    # Send state to clients
    # Serialize
    serialized_state = struct.pack(
        '=fi2i2i2ii2ibiiii2f2f2f2f2f2f2f2f',  # Added 4 more '2f' for the arm and end effector positions
        t,
        i,
        int(p1[0]), int(p1[1]),
        int(p2[0]), int(p2[1]),
        int(ball.body.position[0]), int(ball.body.position[1]),
        int(ball.radius),
        int(blackhole_x), int(blackhole_y),
        int(blackhole_positioned),
        score, success, fail, timer,
        int(f1[0]), int(f1[1]),
        int(f2[0]), int(f2[1]),
        float(arm1_link1_x), float(arm1_link1_y),
        float(arm1_link2_x), float(arm1_link2_y),
        float(arm2_link1_x), float(arm2_link1_y),
        float(arm2_link2_x), float(arm2_link2_y),
        float(end_effector1_position_x), float(end_effector1_position_y),
        float(end_effector2_position_x), float(end_effector2_position_y)
    )

    # Send the serialized state to all players
    for player in players.values():
        try:
            sock.sendto(serialized_state, player)
        except socket.error as e:
            if DEBUG:
                print(f"Error sending game state to {player}: {e}")
    
    if success:
        score += 1
        timer = 3
        high_force_start_time = 0
        force_threshold_time = 5
        append_to_csv(1, filename="succes_rate")
        append_to_csv(time.time() - start_time)
        success = False
    
    if fail:
        timer = 3
        high_force_start_time = 0
        force_threshold_time = 5
        append_to_csv(0, filename="succes_rate")
        append_to_csv(time.time() - start_time)
        fail = False
    # timer for goal position
    position_blackhole = [blackhole_x, blackhole_y] #change to position where it is being blit
    position_asteroid = ball.body.position

    error_margin = 50

    if (abs(position_asteroid[0] - position_blackhole[0]) <= error_margin and 
        abs(position_asteroid[1] - position_blackhole[1]) <= error_margin):
        
        # Check if 1 second has passed since the last timer update
        current_time = time.time()
        if current_time - last_timer_update >= 1 and timer > 0:
            timer -= 1
            last_timer_update = current_time  # Update the last timer update time
        
        #countdown = TEXT_FONT.render(f'{timer}', True, (255, 255, 0))
        if timer == 0:
            #countdown = TEXT_FONT.render(f'SUCCES!', True, (255, 255, 0))
            blackhole_positioned = False
            success = True
        #window.blit(countdown, (position_asteroid[0], position_asteroid[1]))
    else:
        timer = 3
        last_timer_update = time.time()
    force = 40
    if 50 <= np.abs(force):
        if high_force_start_time == 0:
            high_force_start_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        if (current_time - high_force_start_time) / 1000 >= force_threshold_time:
            fail = True

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
