#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import math, json, os
import matplotlib.pyplot as plt
import pygame
import pymunk, pymunk.pygame_util

from src.physics import Physics
from utils.pymunk_simple_objects import *
from utils.convert_pos import convert_pos

# Settings
config_set_path = os.path.join(os.path.dirname(__file__), "../config/settings.json")
config_sim_path = os.path.join(os.path.dirname(__file__), "../config/simulation.json")
with open(config_set_path, "r") as file:
    settings = json.load(file)
with open(config_sim_path, "r") as file:
    cfg_simulation = json.load(file)

'''SIMULATION'''

# SIMULATION PARAMETERS
dt = cfg_simulation['timeStep'] # simulation step time

# initialise real-time plot with pygame
pygame.init() # start pygame
window = pygame.display.set_mode((settings['screen_size']['width'], settings['screen_size']['height'])) # create a window (size in pixels)
window.fill((255,255,255)) # white background
xc, yc = window.get_rect().center # window center
pygame.display.set_caption('test')

font = pygame.font.Font('freesansbold.ttf', 12) # printing text font and font size
text = font.render('test', True, (0, 0, 0), (255, 255, 255)) # printing text object
textRect = text.get_rect()
textRect.topleft = (10, 10) # printing text position with respect to the top-left corner of the window

clock = pygame.time.Clock() # initialise clock
FPS = int(1/dt) # refresh rate

# initial conditions
t = 0.0 # time
pm = np.zeros(2) # mouse position
pr = np.zeros(2) # reference endpoint position
p = np.array([0.1,0.1]) # actual endpoint position
dp = np.zeros(2) # actual endpoint velocity
F = np.zeros(2) # endpoint force
q = np.zeros(2) # joint position
p_prev = np.zeros(2) # previous endpoint position
i = 0 # loop counter
state = [] # state vector

# Pymunk
space = pymunk.Space()
space.gravity = (0, int(100*cfg_simulation['gravity']))

box = create_box(space, (400, 550))
ball = create_ball(space, (400, 400))
floor = create_static_wall(space, (400, 580))

draw_options = pymunk.pygame_util.DrawOptions(window)

# Haptic device
physics = Physics(hardware_version=2)
device_connected = physics.is_device_connected()

# wait until the start button is pressed
run = True
while run:
    for event in pygame.event.get(): # interrupt function
        if event.type == pygame.KEYUP:
            if event.key == ord('e'): # enter the main loop after 'e' is pressed
                run = False

# MAIN LOOP
i = 0
run = True
while run:
    for event in pygame.event.get(): # interrupt function
        if event.type == pygame.QUIT: # force quit with closing the window
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord('q'): # force quit with q button
                run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Apply force when spacebar is pressed
                box.body.apply_force_at_local_point((5000, 0), (0, 0))
    # Haptic device
    if device_connected:
        pA0,pB0,pA,pB,pE = physics.get_device_pos() #positions of the various points of the pantograph
        pm = convert_pos(pygame.display.get_surface().get_size(), settings['hardware_scale'], pE) #convert the physical positions to screen coordinates
    else:
        pm = np.array(pygame.mouse.get_pos())

	# previous endpoint position for velocity calculation
    p_prev = p.copy()

    # log states for analysis
    state.append([t, pr[0], pr[1], p[0], p[1], dp[0], dp[1], F[0], F[1]])
    
    # integration
    #ddp = F/m
    #dp += ddp*dt
    #p += dp*dt
    #t += dt

    # increase loop counter
    i = i + 1
    
    # real-time plotting
    window.fill((255,255,255)) # clear window
    
    # Haptic device
    if device_connected: #set forces only if the device is connected
        physics.update_force(F)
    
    # print data
    text = font.render("FPS = " + str( round( clock.get_fps() ) ), True, (0, 0, 0), (255, 255, 255))
    window.blit(text, textRect)
    
    space.step(1/FPS)
    space.debug_draw(draw_options)
    pygame.display.flip() # update display
        
    
    # try to keep it real time with the desired step time
    clock.tick(FPS)
    
    if run == False:
        physics.close()
        break

pygame.quit() # stop pygame
