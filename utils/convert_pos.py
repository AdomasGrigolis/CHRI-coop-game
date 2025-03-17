def convert_pos(window_size, window_scale, positions):
    device_origin = (int(window_size[0]/2.0 + 0.038/2.0*window_scale),0)
    #invert x because of screen axes
    # 0---> +X
    # |
    # |
    # v +Y
    x = device_origin[0]-positions[0]*window_scale
    y = device_origin[1]+positions[1]*window_scale
    return [x,y]