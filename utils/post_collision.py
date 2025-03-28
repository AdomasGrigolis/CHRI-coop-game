import time
import pymunk
latest_impulse = [0, 0]
# Define a post_solve callback to capture impulse information
# Define a structure to track collisions for each player
player_collisions = {
    1: {
        "position": (0, 0),
        "normal": (0, 0),
        "impulse": (0, 0),
        "time": 0,
        "active": False
    },
    2: {
        "position": (0, 0),
        "normal": (0, 0),
        "impulse": (0, 0),
        "time": 0,
        "active": False
    }
}

def post_collision(arbiter, space, data):
    global player_collisions
    
    # Get collision data
    impulse = arbiter.total_impulse
    points = arbiter.contact_point_set.points
    
    if not points:
        return True
    
    # Determine which player was involved in this collision
    shapes = arbiter.shapes
    # One shape is the asteroid, the other is a player circle
    if shapes[0].collision_type in [1, 2]:
        player_num = shapes[0].collision_type  # 1 or 2
    else:
        player_num = shapes[1].collision_type  # 1 or 2
    
    # Get position and normal
    contact_position = points[0].point_a
    normal = arbiter.contact_point_set.normal

    # Update that player's collision data
    player_collisions[player_num] = {
        "position": contact_position,
        "normal": normal,
        "impulse": impulse,
        "time": time.time(),
        "active": True,
        "processed": False  # Add this flag
    }
    
    #print(f"Player {player_num} impulse of {impulse}")
    
    return True



def ensure_no_overlap(circle_shape, asteroid_shape):
    """
    Ensures that the circle doesn't overlap with the asteroid by adjusting its position
    """
    circle_pos = circle_shape.body.position
    asteroid_pos = asteroid_shape.body.position
    
    # Calculate the distance between the circle and asteroid centers
    distance = ((circle_pos[0] - asteroid_pos[0])**2 + 
                (circle_pos[1] - asteroid_pos[1])**2)**0.5
    
    # Calculate the minimum distance to avoid overlap
    min_distance = circle_shape.radius + asteroid_shape.radius
    
    # If there's an overlap, adjust the circle's position
    if distance < min_distance:
        # Calculate the direction vector from asteroid to circle
        direction_x = circle_pos[0] - asteroid_pos[0]
        direction_y = circle_pos[1] - asteroid_pos[1]
        
        # Normalize the direction vector
        if distance > 0:  # Avoid division by zero
            direction_x /= distance
            direction_y /= distance
            
            # Set circle position at minimum distance from asteroid surface
            new_x = asteroid_pos[0] + direction_x * min_distance
            new_y = asteroid_pos[1] + direction_y * min_distance
            
            # Update the circle's position
            circle_shape.body.position = (new_x, new_y)
            
            return True  # Indicate that an adjustment was made
    
    return False  # No adjustment needed


# In your main loop, replace direct position setting with this:
def update_player_position(body, target_position, max_speed=200):
    current_position = body.position
    
    # Calculate direction vector to target
    dx = target_position[0] - current_position[0]
    dy = target_position[1] - current_position[1]
    
    # Calculate distance
    distance = ((dx**2) + (dy**2))**0.5
    
    if distance > 0.1:  # Only move if there's a meaningful distance
        # Normalize direction
        dx /= distance
        dy /= distance
        
        # Calculate appropriate velocity (faster when farther away)
        speed = min(max_speed, distance * 5)  # Scale with distance up to max_speed
        
        # Set velocity instead of position
        body.velocity = (dx * speed, dy * speed)
    else:
        # Close enough, stop moving
        body.velocity = (0, 0)