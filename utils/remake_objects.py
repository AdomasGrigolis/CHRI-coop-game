import random

def remake_blackhole(screen_size, x_diff = 100, y_diff = 80):
    blackhole_x = random.randint(x_diff, screen_size[0] - x_diff)
    blackhole_y = random.randint(y_diff, screen_size[1] - y_diff)
    return blackhole_x, blackhole_y