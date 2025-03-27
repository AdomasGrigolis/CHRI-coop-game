def convert_pos(window_size, window_scale, vertical_offset, positions):
    device_origin = (int(window_size[0]/2.0 + 0.038/2.0*window_scale),0)
    #invert x because of screen axes
    # 0---> +X
    # |
    # |
    # v +Y
    x = int(device_origin[0]-positions[0]*window_scale)
    y = int(device_origin[1]+positions[1]*window_scale)-vertical_offset
    return [x,y]