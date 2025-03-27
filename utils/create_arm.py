import pygame,pymunk
import math

def create_arm(space, base_pos, length1, length2):
    WHITE=(255,255,255)
    BLACK=(0,0,0)
    RED=(255,0,0)
    BLUE=(0,0,255)
    GREEN=(0,128,0)
    YELLOW = (255, 255, 0)
    LIGHT_SILVER = (192, 192, 192)  
    # create the base
    line_body=pymunk.Body(body_type=pymunk.Body.STATIC)
    line_shape=pymunk.Segment(line_body,(base_pos[0],base_pos[1]-10),(base_pos[0],base_pos[1]+10),5)
    line_shape.elasticity=0.7
    space.add(line_body,line_shape)

    # 第一个臂段]
    arm1_moment = pymunk.moment_for_segment(1, (0, 0), (length1, 0), 5)
    arm1_body = pymunk.Body(1, arm1_moment)
    arm1_body.position = base_pos
    arm1_shape = pymunk.Segment(arm1_body, (0, 0), (length1, 0), 5)
    arm1_shape.elasticity = 0.1
    
    # 将第一个臂段固定在基座上（静态线）
    arm1_joint = pymunk.PivotJoint(line_body, arm1_body, base_pos)
    arm1_joint.collide_bodies = False
    
    # 第二个臂段
    arm2_moment = pymunk.moment_for_segment(1, (0, 0), (length2, 0), 5)
    arm2_body = pymunk.Body(1, arm2_moment)
    arm2_body.position = (arm1_body.position.x + length1, arm1_body.position.y)
    arm2_shape = pymunk.Segment(arm2_body, (0, 0), (length2, 0), 5)
    arm2_shape.elasticity = 0.1
    
    # 连接两个臂段
    arm2_joint = pymunk.PivotJoint(arm1_body, arm2_body, (length1, 0),(0,0))
    arm2_joint.collide_bodies = False
    
    # 限制关节旋转范围（可选）
    # limit1 = pymunk.RotaryLimitJoint(arm1_body, line_body, -math.pi/2, math.pi/2)
    # limit2 = pymunk.RotaryLimitJoint(arm2_body, arm1_body, -math.pi/2, math.pi/2)
    
    space.add(arm1_body, arm1_shape, arm1_joint, 
              arm2_body, arm2_shape, arm2_joint)
              # limit1, limit2)
    ## add initial stiffness to the joint
    spring1 = pymunk.DampedRotarySpring(line_body, arm1_body, rest_angle=0, stiffness=5000, damping=100)
    spring2 = pymunk.DampedRotarySpring(arm1_body, arm2_body, rest_angle=0, stiffness=5000, damping=100)
    space.add(spring1, spring2)

    # create the rectangle end effector
    arm1 = arm1_body
    arm2 = arm2_body
    rect_width = 20
    rect_height = 80

    # 创建一个新的刚体（矩形不会旋转）
    end_effector_body = pymunk.Body(1, pymunk.moment_for_box(1, (rect_width, rect_height)), body_type=pymunk.Body.DYNAMIC)
    end_effector_body.position = (arm2.position.x + length2, arm2.position.y)  # 初始放在 arm2 末端
    end_effector_shape = pymunk.Poly.create_box(end_effector_body, (rect_width, rect_height))
    end_effector_shape.elasticity = 0.5
    end_effector_shape.collision_type = 10
    space.add(end_effector_body, end_effector_shape)

    # 让矩形连接到 arm2 末端
    # pivot_joint = pymunk.PivotJoint(arm2, end_effector_body, (100, 0), (0, 0))
    # space.add(pivot_joint)

    pivot = pymunk.PivotJoint(arm2, end_effector_body, 
                         (length2, 0),  # arm2 末端的局部坐标
                         (0, 0))    # 末端执行器中心的局部坐标
    pivot.collide_bodies = False

    # 2. 可选：限制旋转范围（如允许360度无限制旋转）
    # 如果不限制，则完全自由旋转
    limit = pymunk.RotaryLimitJoint(
        end_effector_body,
        space.static_body,  # 相对于静态世界固定角度
        0, 0  # min=max=0，强制角度始终为0（竖直）
    )
    space.add(pivot, limit)

    return arm1, arm2, end_effector_shape

def draw_arm_segment(screen, start_pos, end_pos, width, color):
    # Calculate angle and length
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    angle = math.atan2(dy, dx)
    length = math.sqrt(dx**2 + dy**2)
    
    # Create a surface for the rectangle
    rect_surface = pygame.Surface((length, width), pygame.SRCALPHA)
    pygame.draw.rect(rect_surface, color, (0, 0, length, width))
    
    # Rotate the surface
    rotated_surface = pygame.transform.rotate(rect_surface, -math.degrees(angle))
    
    # Calculate position to blit
    rect = rotated_surface.get_rect()
    rect.center = (start_pos[0] + dx/2, start_pos[1] + dy/2)
    
    # Draw on screen
    screen.blit(rotated_surface, rect)
    
    # Draw joint circles
    JOINT_RADIUS = 8
    pygame.draw.circle(screen, color, (int(start_pos[0]), int(start_pos[1])), JOINT_RADIUS)