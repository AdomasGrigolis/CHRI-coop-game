import numpy as np
import math
import matplotlib.pyplot as plt
import pygame
import pymunk
import pymunk.pygame_util
import socket, struct

# UDP setup
UDP_IP_recv = "127.0.0.1"
UDP_PORT_recv = 5005
sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind((UDP_IP_recv, UDP_PORT_recv))
sock_recv.setblocking(0)  # Make socket non-blocking

UDP_IP_send = "127.0.0.2"
UDP_PORT_send = 5006
sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MESSAGE = 'hehe'.encode('utf-8')
sock_send.sendto(MESSAGE, (UDP_IP_send, UDP_PORT_send))

'''ROBOT MODEL'''
class robot_arm_2dof:
    def __init__(self, l):
        self.l = l  # link length
    
    # arm Jacobian matrix
    def Jacobian(self, q):
        J = np.array([[-self.l[0]*np.sin(q[0]) - self.l[1]*np.sin(q[0] + q[1]),
                     -self.l[1]*np.sin(q[0] + q[1])],
                    [self.l[0]*np.cos(q[0]) + self.l[1]*np.cos(q[0] + q[1]),
                     self.l[1]*np.cos(q[0] + q[1])]])
        return J
    
    # inverse kinematics
    def IK(self, p):
        q = np.zeros([2])
        r = np.sqrt(p[0]**2+p[1]**2)
        q[1] = np.pi - math.acos((self.l[0]**2+self.l[1]**2-r**2)/(2*self.l[0]*self.l[1]))
        q[0] = math.atan2(p[1],p[0]) - math.acos((self.l[0]**2-self.l[1]**2+r**2)/(2*self.l[0]*r))
        return q

'''SIMULATION'''
# SIMULATION PARAMETERS
dt = 0.01  # integration step time
dts = dt*1  # desired simulation step time

# ROBOT PARAMETERS
x0 = 0.0  # base x position
y0 = 0.0  # base y position
l1 = 0.33  # link 1 length
l2 = 0.33  # link 2 length (includes hand)
l = [l1, l2]  # link length

# IMPEDANCE CONTROLLER PARAMETERS
Ks = np.diag([1000, 100])  # stiffness in the endpoint stiffness frame [N/m]
theta = 0.0  # rotation of the endpoint stiffness frame
stiffness_value_increment = 100  # for tele-impedance [N/m]
stiffness_angle_increment = 10*np.pi/180  # for tele-impedance [rad]

# SIMULATOR
# Initialize pygame
pygame.init()
window = pygame.display.set_mode((800, 600))
window.fill((255, 255, 255))
xc, yc = window.get_rect().center
pygame.display.set_caption('robot arm')

# Initialize pymunk
space = pymunk.Space()
space.gravity = (0, 0)  # No gravity in our 2D plane simulation

# Set up pygame-pymunk conversion
draw_options = pymunk.pygame_util.DrawOptions(window)
window_scale = 800  # conversion from meters to pixels

# Create robot arm in pymunk
def create_robot_arm():
    # Base (fixed point)
    base_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    base_body.position = (xc, yc)
    base_shape = pymunk.Circle(base_body, 9)
    base_shape.color = (0, 0, 0, 255)
    space.add(base_body, base_shape)
    
    # Link 1
    link1_body = pymunk.Body(1, 1000)
    link1_body.position = (xc + l1 * window_scale / 2, yc)
    link1_shape = pymunk.Segment(link1_body, (-l1 * window_scale / 2, 0), (l1 * window_scale / 2, 0), 6)
    link1_shape.color = (0, 0, 255, 255)
    space.add(link1_body, link1_shape)
    
    # Joint between base and link1
    joint1 = pymunk.PivotJoint(base_body, link1_body, base_body.position)
    space.add(joint1)
    
    # Link 2
    link2_body = pymunk.Body(1, 1000)
    link2_body.position = (xc + l1 * window_scale + l2 * window_scale / 2, yc)
    link2_shape = pymunk.Segment(link2_body, (-l2 * window_scale / 2, 0), (l2 * window_scale / 2, 0), 6)
    link2_shape.color = (0, 0, 255, 255)
    space.add(link2_body, link2_shape)
    
    # Joint between link1 and link2
    joint2 = pymunk.PivotJoint(link1_body, link2_body, (xc + l1 * window_scale, yc))
    space.add(joint2)
    
    # End effector
    end_body = pymunk.Body(0.5, 100)  # Mass of 0.5, moment of 100
    end_body.position = (xc + l1 * window_scale + l2 * window_scale, yc)
    end_shape = pymunk.Circle(end_body, 5)
    end_shape.color = (255, 0, 0, 255)
    space.add(end_body, end_shape)
    
    # Fix end effector to link2
    end_joint = pymunk.PivotJoint(link2_body, end_body, end_body.position)
    space.add(end_joint)
    
    return base_body, link1_body, link2_body, end_body

# Create wall
def create_wall():
    wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    wall_pos = 0.1666 * window_scale + xc
    wall_body.position = (wall_pos + 5, yc)  # Position the wall (5 is half the thickness)
    wall_shape = pymunk.Poly.create_box(wall_body, (10, 600))  # Wall is 10 pixels thick, 600 high
    wall_shape.color = (0, 255, 0, 255)
    wall_shape.friction = 0.5
    wall_shape.elasticity = 0.5
    space.add(wall_body, wall_shape)
    return wall_body, wall_shape

# Create block obstacle
def create_block():
    block_body = pymunk.Body(10, 1000)  # Mass of 10, moment calculated by pymunk
    block_body.position = (xc + 200, yc - 100)
    block_width, block_height = 100, 80
    block_shape = pymunk.Poly.create_box(block_body, (block_width, block_height))
    block_shape.color = (0, 0, 255, 255)
    block_shape.friction = 0.5
    block_shape.elasticity = 0.2
    space.add(block_body, block_shape)
    return block_body, block_shape

# Create all bodies
base_body, link1_body, link2_body, end_body = create_robot_arm()
wall_body, wall_shape = create_wall()
block_body, block_shape = create_block()

# Setup for rendering
font = pygame.font.Font('freesansbold.ttf', 12)
text = font.render('robot arm', True, (0, 0, 0), (255, 255, 255))
textRect = text.get_rect()
textRect.topleft = (10, 10)

clock = pygame.time.Clock()
FPS = int(1/dts)

# Initial conditions
t = 0.0
pm = np.zeros(2)
pr = np.zeros(2)
p = np.array([0.1, 0.1])
dp = np.zeros(2)
F = np.zeros(2)
q = np.zeros(2)
p_prev = np.zeros(2)
m = 0.5
i = 0
state = []

# Wait until start button is pressed
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.KEYUP:
            if event.key == ord('e'):
                run = False

# Main loop
i = 0
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord('q'):
                run = False
            elif event.key == pygame.K_x:
                Ks[0,0] = min(1000, Ks[0,0] + stiffness_value_increment)
            elif event.key == pygame.K_z:
                Ks[0,0] = max(0, Ks[0,0] - stiffness_value_increment)
            elif event.key == pygame.K_d:
                Ks[1,1] = min(1000, Ks[1,1] + stiffness_value_increment)
            elif event.key == pygame.K_c:
                Ks[1,1] = max(0, Ks[1,1] - stiffness_value_increment)
            elif event.key == pygame.K_a:
                theta = min(np.pi/2, theta + stiffness_angle_increment)
            elif event.key == pygame.K_s:
                theta = max(-np.pi/2, theta - stiffness_angle_increment)
    
    # Try to receive UDP position data
    try:
        position, addr = sock_recv.recvfrom(12)
        position = struct.unpack("=2f", position)
        pr[0], pr[1] = position
        pr[0] = (pr[0] - 300)/1000
        pr[1] = -(pr[1] - 200)/1000
    except socket.error:
        # No data available, use mouse position instead
        pm = pygame.mouse.get_pos()
        pm = ((pm[0] - xc)/window_scale, -(pm[1] - yc)/window_scale)
        pr = np.array(pm)  # Convert tuple to numpy array

    
    # Get current end effector position from pymunk
    p_prev = p.copy()
    p[0] = (end_body.position.x - xc) / window_scale
    p[1] = -(end_body.position.y - yc) / window_scale
    
    # Calculate velocity
    dp = (p - p_prev) / dt
    
    # Calculate force based on impedance control
    d_p = p - pr
    F[0] = -Ks[0,0] * d_p[0] - 35 * dp[0]
    F[1] = -Ks[1,1] * d_p[1] - 35 * dp[1]
    
    # Apply force to end effector
    end_body.apply_force_at_local_point((F[0] * window_scale, -F[1] * window_scale), (0, 0))
    
    # Update pymunk simulation
    space.step(dt)
    
    # Get joint angles from pymunk body positions (for visualization)
    link1_angle = math.atan2(link1_body.position.y - base_body.position.y, 
                           link1_body.position.x - base_body.position.x)
    link2_angle = math.atan2(link2_body.position.y - link1_body.position.y,
                           link2_body.position.x - link1_body.position.x)
    
    # Log states for analysis
    state.append([t, pr[0], pr[1], p[0], p[1], dp[0], dp[1], F[0], F[1], Ks[0,0], Ks[1,1]])
    
    # Send force data via UDP
    send_data = bytearray(struct.pack("=%sf" % F.size, *F))
    sock_send.sendto(send_data, (UDP_IP_send, UDP_PORT_send))
    
    # Rendering
    window.fill((255, 255, 255))
    
    # Draw objects
    space.debug_draw(draw_options)
    
    # Draw reference position
    pygame.draw.circle(window, (0, 255, 0), 
                       (int(pr[0] * window_scale + xc), int(-pr[1] * window_scale + yc)), 5)
    
    # Draw force vector
    force_scale = 50/(window_scale*(l1*l1))
    pygame.draw.line(window, (0, 255, 255), 
                     (end_body.position.x, end_body.position.y),
                     (end_body.position.x + F[0] * force_scale,
                      end_body.position.y - F[1] * force_scale), 2)
    
    # Visualize manipulability and stiffness ellipses
    model = robot_arm_2dof(l)
    q[0], q[1] = link1_angle, link2_angle - link1_angle
    J = model.Jacobian(q)
    
    # Manipulability ellipse
    Js = np.linalg.pinv(J @ J.T)
    J_eigvals, J_eigvec = np.linalg.eig(Js)
    
    scale_factor = 10
    eig_sorted_indices = np.argsort(J_eigvals)[::-1]
    major_axis = np.sqrt(J_eigvals[eig_sorted_indices[0]]) * scale_factor
    minor_axis = np.sqrt(J_eigvals[eig_sorted_indices[1]]) * scale_factor
    
    ellipse_rect_force = pygame.Rect(
        p[0] * window_scale + xc - major_axis/2,
        -p[1] * window_scale + yc - minor_axis/2,
        major_axis,
        minor_axis
    )
    pygame.draw.ellipse(window, (255, 0, 0), ellipse_rect_force, 2)
    
    # Stiffness ellipse
    K_eigvals, K_eigvec = np.linalg.eig(Ks)
    
    scale_factor_2 = 1
    eig_sorted_indices = np.argsort(K_eigvals)[::-1]
    major_axis_2 = np.sqrt(K_eigvals[eig_sorted_indices[0]]) * scale_factor_2
    minor_axis_2 = np.sqrt(K_eigvals[eig_sorted_indices[1]]) * scale_factor_2
    
    ellipse_rect_stiff = pygame.Rect(
        p[0] * window_scale + xc - major_axis_2/2,
        -p[1] * window_scale + yc - minor_axis_2/2,
        major_axis_2,
        minor_axis_2
    )
    pygame.draw.ellipse(window, (255, 0, 255), ellipse_rect_stiff, 2)
    
    # Display info
    text = font.render("FPS = " + str(round(clock.get_fps())) + 
                      "   K = " + str([Ks[0,0], Ks[1,1]]) + " N/m" + 
                      "   x = " + str(np.round(p, 3)) + " m" + 
                      "   F = " + str(np.round(F, 0)) + " N", 
                      True, (0, 0, 0), (255, 255, 255))
    window.blit(text, textRect)
    
    pygame.display.flip()
    clock.tick(FPS)
    t += dt
    i += 1
    
    if not run:
        break

pygame.quit()

# ANALYSIS (same as before)
state = np.array(state)

plt.figure(3)
plt.subplot(411)
plt.title("VARIABLES")
plt.plot(state[:,0],state[:,1],"b",label="x")
plt.plot(state[:,0],state[:,2],"r",label="y")
plt.legend()
plt.ylabel("pr [m]")

plt.subplot(412)
plt.plot(state[:,0],state[:,3],"b")
plt.plot(state[:,0],state[:,4],"r")
plt.ylabel("p [m]")

plt.subplot(413)
plt.plot(state[:,0],state[:,7],"b")
plt.plot(state[:,0],state[:,8],"r")
plt.ylabel("F [N]")

plt.subplot(414)
plt.plot(state[:,0],state[:,9],"c")
plt.plot(state[:,0],state[:,10],"m")
plt.ylabel("K [N/m]")
plt.xlabel("t [s]")

plt.tight_layout()

plt.figure(4)
plt.title("ENDPOINT BEHAVIOUR")
plt.plot(0,0,"ok",label="shoulder")
plt.plot(state[:,1],state[:,2],"lime",label="reference")
plt.plot(state[:,3],state[:,4],"r",label="actual")
plt.axis('equal')
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.legend()

plt.tight_layout()