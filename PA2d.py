# -*- coding: utf-8 -*-
import sys
import math
import time
import numpy as np
import pygame
import os

from Physics import Physics
from Graphics import Graphics

#Hints:
#1: You can create your own persistant variables in the __init__() or run() functions by prefacing them with "self".
#     - For example: "self.prev_xh = xh"
#2: Change the values of "fe" and those forces will be sent to the device or simulated if no device is connected
#     - Note that this occurs AT THE END OF THE RUN FUNCTION
#     - fe is in SI units
#     - The Haply device can only exert a limited amount of force, so at some point setting very high forces will be useless
#3: Graphical components are all encapsulated in self.graphics (variable "g" in the run() function)
#     - These include the screenHaptics and screenVR surfaces which are the right and left display screens respectively
#     - Thus drawing a line on the right screen would be:
#            "pygame.draw.lines(g.screenHaptics, (0,255,0), False,[(0,0),(400,400)],1)"
#     - The orange proxy object is "g.haptic" and has an initial size of 48x48
#           - g.haptic has several parameters that can be read or updated such as:
#                 - haptic.w and haptic.h: haptic proxy rectangle width and height
#                 - haptic.center: haptic proxy center position
#4: Graphics contains two conversion functions to convert from and to SI units
#     - "g.convert_pos( (x,y) )" converts from the haply's physical coordinates to the graphical coordinates. Remember that the axes may not be aligned the same way!
#     - "g.inv_convert_pos( (x,y) )" converts from the graphical coordinates to the haply's physical coordinates
#     - Both functions can take in a single or multiple point written as a tuple or list with two elements
#           - point = g.convert_pos( (x,y) )
#           - p0,p1 = g.convert_pos( (x0,y0),(x1,y1) )
#     - For simple scale conversion, use the pixels-per-meter value, "g.window_scale"
#5: Other useful parameters of graphics
#     - The framerate of the graphics rendering can be accessed (and changed if you really want) via the "g.FPS" parameter
#     - "g.debug_text" is the debug string that will be drawn in the upper left. This string can be added to for debug purposes
#6: If you want to use pygame's collision detection ( for example, colliderect() ) while also changing the shape of the haptic proxy to represent impedance,
#       consider using the equivalent haptic proxy on the screenHaptic side (g.effort_cursor), as it is the same size as g.haptic and is at the same position.

###############################################
import socket, struct
UDP_IP_send = "127.0.0.1"
UDP_PORT_send = 5005

sock_send = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


UDP_IP_recv = "127.0.0.2"
UDP_PORT_recv = 5006

sock_recv = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock_recv.bind((UDP_IP_recv, UDP_PORT_recv))
#MESSAGE = 'dummycodetostart'.encode('utf-8')
#sock_send.sendto(MESSAGE, (UDP_IP_send, UDP_PORT_send))
# while True:
#     data, addr = sock_recv.recvfrom(1024) # buffer size is 1024 bytes
#     sock_send.sendto(MESSAGE, (UDP_IP_send, UDP_PORT_send))
#     print("received message: %s" % data)

###############################################




class PA:
    def __init__(self):
        self.physics = Physics(hardware_version=3) #setup physics class. Returns a boolean indicating if a device is connected
        self.device_connected = self.physics.is_device_connected() #returns True if a connected haply device was found
        self.graphics = Graphics(self.device_connected) #setup class for drawing and graphics.
        #  - Pass along if a device is connected so that the graphics class knows if it needs to simulate the pantograph
        xc,yc = self.graphics.screenVR.get_rect().center
        ##############################################
        #ADD things here that you want to run at the start of the program!
        
        #variables for stiffness and dampingcoefficient
        self.k_spring = 50
        self.be = 5  
        self.m = 0.001
        
        self.spring_rest_pos = np.array(self.graphics.screenVR.get_rect().center)  # Center of the screen
        self.spring_rest_pos_physics = self.graphics.inv_convert_pos(self.spring_rest_pos)  # Convert to physics coordinates
        #self.center_phys = self.graphicsE.inv_convert_pos(self.graphics.screenVR.get_rect().center)
        
        # velocity calculation
        self.prev_pos = None
        self.prev_time = time.time()
        self.velocity = np.array([0.0, 0.0])
        
        # acceleration calculation (for mass simulation)
        self.prev_velocity = np.array([0.0, 0.0])
        self.acceleration = np.array([0.0, 0.0])
        
        # Simulation mode
        self.mode = "spring"  # Can be "spring", "damper", "mass"
        ##############################################
    
    def run(self):
        p = self.physics #assign these to shorthand variables for easier use in this function
        g = self.graphics
        #get input events for both keyboard and mouse
        keyups,xm = g.get_events()
        #  - keyups: list of unicode numbers for keys on the keyboard that were released this cycle
        #  - pm: coordinates of the mouse on the graphics screen this cycle (x,y)      
        #get the state of the device, or otherwise simulate it if no device is connected (using the mouse position)
        if self.device_connected:
            pA0,pB0,pA,pB,pE = p.get_device_pos() #positions of the various points of the pantograph
            pA0,pB0,pA,pB,xh = g.convert_pos(pA0,pB0,pA,pB,pE) #convert the physical positions to screen coordinates
        else:
            xh = g.haptic.center
            #set xh to the current haptic position, which is from the last frame.
            #This previous position will be compared to the mouse position to pull the endpoint towards the mouse
        fe = np.array([0.0,0.0]) #fx,fy
        xh = np.array(xh) #make sure fe is a numpy array
        xc,yc = g.screenVR.get_rect().center
        g.erase_screen()
        ##############################################
        #ADD things here that run every frame at ~100fps!
        for key in keyups:
            if key==ord("q"): #q for quit, ord() gets the unicode of the given character
                sys.exit(0) #raises a system exit exception so the "PA.close()" function will still execute
            if key == ord('m'): #Change the visibility of the mouse
                pygame.mouse.set_visible(not pygame.mouse.get_visible())
            if key == ord('r'): #Change the visibility of the linkages
                g.show_linkages = not g.show_linkages
            if key == ord('d'): #Change the visibility of the debug text
                g.show_debug = not g.show_debug
            #you can add more if statements to handle additional key characters
        
        # Step 1 & 2: Simulate spring, damper, and mass
        
        # Calculate time step
        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time
        
        # Convert haptic position to physical coordinates for force calculation
        xh_phys = np.array(g.inv_convert_pos(xh))
        
        # Calculate velocity (if we have a previous position)
        if self.prev_pos is not None:
            self.velocity = (xh_phys - self.prev_pos) / dt
        self.prev_pos = xh_phys.copy()
        
        # Calculate acceleration (for mass simulation)
        if np.all(self.prev_velocity != 0):
            self.acceleration = (self.velocity - self.prev_velocity) / dt
        self.prev_velocity = self.velocity.copy()
        
        # Reset force
        fe = np.array([0.0, 0.0])
        
        # Calculate displacement from rest position
        displacement = np.array([xc-xh[0], yc - xh[1]])/3000
        
        # Apply appropriate force based on mode
        if self.mode == "spring":
            # Spring force (F = -k * x)
            spring_force = self.k_spring * displacement
            fe = spring_force
            
            # Draw the spring in the VR environment
            pygame.draw.line(g.screenVR, (255, 0, 0), xh, self.spring_rest_pos, 2)
            pygame.draw.circle(g.screenVR, (0, 0, 255), self.spring_rest_pos, 10)
            
        elif self.mode == "damper":
            # Damping force (F = -b * v)
            damping_force = -self.be * self.velocity
            fe = damping_force
            
            # Draw the damper in the VR environment
            pygame.draw.line(g.screenVR, (0, 255, 0), xh, self.spring_rest_pos, 2)
            pygame.draw.circle(g.screenVR, (0, 0, 255), self.spring_rest_pos, 10)
            
        elif self.mode == "mass":
            # Mass force (F = -m * a)
            # Simulate a mass connected to the haptic device by applying a force opposite to acceleration
            mass_force = -self.m * self.acceleration   #added /1000 because other wise the system was usntable
            # print('acceleration', self.acceleration)
            # print('mass force:',mass_force)
            fe = mass_force
            
            
            
        ##############################################################
        #SEND DATA
        print('lol')
        send_data = bytearray(struct.pack("=%sf" % xh.size, *xh))
        sock_send.sendto(send_data, (UDP_IP_send, UDP_PORT_send))
        print('xh', xh)
        ##############################################################
        #RECEIVE DATA    
        data, addr = sock_recv.recvfrom(8) # buffer size is 1024 bytes
        force = struct.unpack("=2f", data)

        
        # print('Force=', fe)
        # print('ddata=',  force)
        ##############################################################

        
        ##############################################
        if self.device_connected: #set forces only if the device is connected
            p.update_force(fe)
        else:
            xh = g.sim_forces(xh,fe,xm,mouse_k=0.5,mouse_b=0.8) #simulate forces with mouse haptics
            pos_phys = g.inv_convert_pos(xh)
            pA0,pB0,pA,pB,pE = p.derive_device_pos(pos_phys) #derive the pantograph joint positions given some endpoint position
            pA0,pB0,pA,pB,xh = g.convert_pos(pA0,pB0,pA,pB,pE) #convert the physical positions to screen coordinates
        g.render(pA0,pB0,pA,pB,xh,fe,xm)
        
    def close(self):
        ##############################################
        #ADD things here that you want to run right before the program ends!
        
        ##############################################
        self.graphics.close()
        self.physics.close()

if __name__=="__main__":
    pa = PA()
    try:
        while True:
            pa.run()
    finally:
        pa.close()