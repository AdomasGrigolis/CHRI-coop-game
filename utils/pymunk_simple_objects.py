import pymunk

_default_elasticity = 0.2
_default_friction = 0.8

def create_box(space, position, size=(50, 50), mass=1, elasticity=_default_elasticity, friction=_default_friction):
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
    body.position = position
    shape = pymunk.Poly.create_box(body, size)
    shape.elasticity = elasticity
    shape.friction = friction
    space.add(body, shape)
    return shape

def create_static_wall(space, position, size=(800, 20), elasticity=_default_elasticity, friction=_default_friction):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = position
    shape = pymunk.Poly.create_box(body, size)
    shape.elasticity = elasticity
    shape.friction = friction
    space.add(body, shape)
    return shape

def create_ball(space, position, radius=20, mass=1, elasticity=_default_elasticity, friction=_default_friction):
    body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.elasticity = elasticity
    shape.friction = friction
    space.add(body, shape)
    return shape

def create_polygon(space, position, vertices, mass=1, elasticity=_default_elasticity, friction=_default_friction):
    moment = pymunk.moment_for_poly(mass, vertices)
    body = pymunk.Body(mass, moment)
    body.position = position
    shape = pymunk.Poly(body, vertices)
    shape.elasticity = elasticity
    shape.friction = friction
    space.add(body, shape)
    return shape

def create_spring(space, body_a, body_b, anchor_a, anchor_b, rest_length=50, stiffness=100, damping=5):
    spring = pymunk.DampedSpring(body_a, body_b, anchor_a, anchor_b, rest_length, stiffness, damping)
    space.add(spring)
    return spring