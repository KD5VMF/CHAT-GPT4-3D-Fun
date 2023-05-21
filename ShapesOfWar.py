import pygame
import random
import pymunk
from pygame.locals import *
from pymunk import Vec2d

# Configuration variables
STRIKE_COLOR = (0, 255, 0)  # RGB (min: (0, 0, 0), max: (255, 255, 255), default: (0, 255, 0))
STRUCK_COLOR = (255, 255, 255)  # RGB (min: (0, 0, 0), max: (255, 255, 255), default: (255, 255, 255))
SLOWEST_CUBE_COLOR = (255, 0, 0)  # RGB (min: (0, 0, 0), max: (255, 255, 255), default: (255, 0, 0))
GRAVITY = (0.2, 0.2)  # Gravity (min: (-inf, -inf), max: (inf, inf), default: (0.0, 0.0))
CUBE_SPEED = 50  # Cube speed (min: 0, max: inf, default: 25)
CUBE_SIZE = 20  # Cube size (min: 1, max: SCREEN_SIZE min dimension, default: 20)
NUM_CUBES = 100  # Number of cubes (min: 1, max: inf, default: 10)
CUBE_MASS = 50.0  # Mass of each cube (min: 0.1, max: inf, default: 50.0)
ELASTICITY = 1.2  # Elasticity of the cubes (min: 0, max: inf, default: 1.0)
FRICTION = 0.0  # Friction of the cubes (min: 0, max: 1, default: 0.0)
SCREEN_SIZE = [1024, 768]  # Screen size (min: [100, 100], max: [max monitor width, max monitor height], default: [800, 600])
FRAME_RATE = 80  # Frame rate (min: 1, max: 1000, default: 80)
TEXT_COLOR = (255, 255, 255)  # White (min: (0, 0, 0), max: (255, 255, 255), default: (255, 255, 255))
FONT_SIZE = 30  # Font size (min: 1, max: inf, default: 40)


class Cube:
    def __init__(self, space, color, pos, velocity, size, mass, elasticity, friction, shape_type=0):
        self.size = size
        self.color = color
        self.shape_type = shape_type
        inertia = pymunk.moment_for_box(mass, (size, size))
        self.body = pymunk.Body(mass, inertia)
        self.body.position = pos
        self.body.velocity = velocity

        if shape_type == 0:  # Cube
            self.shape = pymunk.Poly.create_box(self.body, (size, size))
        elif shape_type == 1:  # Triangle
            vertices = [(-size // 2, -size // 2), (size // 2, -size // 2), (0, size // 2)]
            self.shape = pymunk.Poly(self.body, vertices)
        elif shape_type == 2:  # Ball
            self.shape = pymunk.Circle(self.body, size // 2)

        self.shape.elasticity = elasticity
        self.shape.friction = friction
        self.shape.cube = self
        space.add(self.body, self.shape)


    def draw(self, screen):
        if any(v != v for v in self.body.position):
            return

        if self.shape_type == 0:  # Cube
            points = [(*self.body.local_to_world(v),) for v in self.shape.get_vertices()]
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape_type == 1:  # Triangle
            points = [(*self.body.local_to_world(v),) for v in self.shape.get_vertices()]
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape_type == 2:  # Ball
            pygame.draw.circle(screen, self.color, [int(x) for x in self.body.position], self.size // 2)

def handle_collision(arbiter, space, data):
    for shape in arbiter.shapes:
        cube = shape.cube
        if cube.color == STRUCK_COLOR:  # If the cube is white, change it back to green
            cube.color = STRIKE_COLOR  # Green
        else:  # If the cube is green, change it to white
            cube.color = STRUCK_COLOR  # White

            # Cycle through the shapes (cube -> triangle -> ball -> cube)
            cube.shape_type = (cube.shape_type + 1) % 3
            old_shape = cube.shape
            space.remove(old_shape)
            cube.__init__(space, cube.color, cube.body.position, cube.body.velocity,
                      cube.size, CUBE_MASS, ELASTICITY, FRICTION, cube.shape_type)
    return True  # Continue processing this collision

def main():
    global SCREEN_SIZE
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Press 'Q' to quit")

    # Initialize font
    pygame.font.init()
    font = pygame.font.Font(None, FONT_SIZE)

    # Initialize Pymunk space
    space = pymunk.Space()
    space.gravity = GRAVITY
    handler = space.add_default_collision_handler()  # Add a collision handler
    handler.begin = handle_collision  # Set the function to call on collision

    # Add cubes to the space
    cubes = []
    slowest_cube_speed = float('inf')
    slowest_cube = Cube(space, STRIKE_COLOR, (0, 0), (0, 0), CUBE_SIZE, CUBE_MASS, ELASTICITY, FRICTION)

    for _ in range(NUM_CUBES):
        pos = (random.randint(0, SCREEN_SIZE[0]), random.randint(0, SCREEN_SIZE[1]))
        velocity = Vec2d(random.uniform(-CUBE_SPEED, CUBE_SPEED), random.uniform(-CUBE_SPEED, CUBE_SPEED))
        cube = Cube(space, STRIKE_COLOR, pos, velocity, CUBE_SIZE, CUBE_MASS, ELASTICITY, FRICTION)
        cubes.append(cube)

        # Check if the current cube is the slowest and update its color
        cube_speed = velocity.length
        if cube_speed < slowest_cube_speed:
            if slowest_cube:
                slowest_cube.color = STRIKE_COLOR
                slowest_cube_speed = cube_speed
                slowest_cube = cube
                slowest_cube.color = SLOWEST_CUBE_COLOR

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_q)):
                running = False
            if event.type == VIDEORESIZE:
                SCREEN_SIZE[0], SCREEN_SIZE[1] = event.size
                screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)

        # Step the physics simulation
        space.step(1/FRAME_RATE)

        # Update cube positions and handle collisions with the screen boundaries
        for cube in cubes:
            x, y = cube.body.position
            vx, vy = cube.body.velocity

            if x - cube.size // 2 < 0 and vx < 0:
                vx = abs(vx)
            elif x + cube.size // 2 > SCREEN_SIZE[0] and vx > 0:
                vx = -abs(vx)

            if y - cube.size // 2 < 0 and vy < 0:
                vy = abs(vy)
            elif y + cube.size // 2 > SCREEN_SIZE[1] and vy > 0:
                vy = -abs(vy)
            if cube.shape_type == 1:  # If the shape is a triangle
                if x - cube.size // 2 < 0 and vx < 0 or x + cube.size // 2 > SCREEN_SIZE[0] and vx > 0:
                    cube.body.angular_velocity = -cube.body.angular_velocity
                if y - cube.size // 2 < 0 and vy < 0 or y + cube.size // 2 > SCREEN_SIZE[1] and vy > 0:
                    cube.body.angular_velocity = -cube.body.angular_velocity
    

            cube.body.velocity = Vec2d(vx, vy)

            # Reset position if NaN occurs
            if any(v != v for v in cube.body.position):
                cube.body.position = Vec2d(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
                cube.body.velocity = Vec2d(0, 0)

                        # Update slowest cube
        slowest_cube_speed = float('inf')
        slowest_cube_new = None
        for cube in cubes:
            cube_speed = cube.body.velocity.length
            if cube_speed < slowest_cube_speed:
                slowest_cube_speed = cube_speed
                slowest_cube_new = cube

        slowest_cube_new = slowest_cube if slowest_cube_new is None else slowest_cube_new

        if slowest_cube_new != slowest_cube:
            slowest_cube.color = STRIKE_COLOR
            slowest_cube = slowest_cube_new
            slowest_cube.color = SLOWEST_CUBE_COLOR


        screen.fill((0, 0, 0))

        for cube in cubes:
            cube.draw(screen)

        # Display the count of struck and strike cubes
        strike_count = sum(1 for cube in cubes if cube.color == STRIKE_COLOR)
        struck_count = sum(1 for cube in cubes if cube.color == STRUCK_COLOR)
        text = font.render(f"Strike: {strike_count} | Struck: {struck_count}", True, TEXT_COLOR)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FRAME_RATE)

    pygame.quit()

if __name__ == "__main__":
    main()

