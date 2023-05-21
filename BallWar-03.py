import pygame
import random
import pymunk
from pygame.locals import *
from pymunk import Vec2d

# Configuration variables
STRIKE_COLOR = (255, 255, 255)  # Ball Color
STRUCK_COLOR = (0, 255, 0)  # Ball Color
BALL_SPEED = 100
BALL_SIZE = 20
SCREEN_SIZE = [800, 600]  # Changed from tuple to list to make it mutable
FRAME_RATE = 70
NUM_BALLS = 100
GRAVITY = (0.0, 0.0)  # Set to (0.0, -100.0) for gravity like on Earth
BALL_MASS = 1.0  # Mass of each ball
ELASTICITY = 1.0  # Elasticity of the balls (0.0 to 1.0)
FRICTION = 0.0  # Friction of the balls (0.0 to 1.0)
TEXT_COLOR = (255, 255, 255)  # White
FONT_SIZE = 40

class Ball:
    def __init__(self, space, color, pos, velocity, size, mass, elasticity, friction):
        self.size = size
        self.color = color
        inertia = pymunk.moment_for_circle(mass, 0, size // 2)
        self.body = pymunk.Body(mass, inertia)
        self.body.position = pos
        self.body.velocity = velocity
        self.shape = pymunk.Circle(self.body, size // 2)
        self.shape.elasticity = elasticity
        self.shape.friction = friction
        self.shape.ball = self  # Add a reference to the ball object in the shape
        space.add(self.body, self.shape)

    def draw(self, screen):
        if any(v != v for v in self.body.position):
            return
        x, y = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(screen, self.color, (x, y), self.size // 2)

def handle_collision(arbiter, space, data):
    for shape in arbiter.shapes:
        if shape.ball.color == STRUCK_COLOR:  # If the ball is red, change it back to green
            shape.ball.color = STRIKE_COLOR  # Neon green
        else:  # If the ball is green, change it to red
            shape.ball.color = STRUCK_COLOR  # Red
    return True  # Continue processing this collision

def main():
    global SCREEN_SIZE  # Add this line to fix the error
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

        # Add balls to the space
    balls = []
    for _ in range(NUM_BALLS):
        pos = (random.randint(0, SCREEN_SIZE[0]), random.randint(0, SCREEN_SIZE[1]))
        velocity = Vec2d(random.uniform(-BALL_SPEED, BALL_SPEED), random.uniform(-BALL_SPEED, BALL_SPEED))
        ball = Ball(space, STRIKE_COLOR, pos, velocity, BALL_SIZE, BALL_MASS, ELASTICITY, FRICTION)
        balls.append(ball)

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

        # Update ball positions and handle collisions with the screen boundaries
        for ball in balls:
            x, y = ball.body.position
            vx, vy = ball.body.velocity

            if x - ball.size // 2 < 0 and vx < 0:
                vx = abs(vx)
            elif x + ball.size // 2 > SCREEN_SIZE[0] and vx > 0:
                vx = -abs(vx)

            if y - ball.size // 2 < 0 and vy < 0:
                vy = abs(vy)
            elif y + ball.size // 2 > SCREEN_SIZE[1] and vy > 0:
                vy = -abs(vy)

            ball.body.velocity = Vec2d(vx, vy)

            # Reset position if NaN occurs
            if any(v != v for v in ball.body.position):
                ball.body.position = Vec2d(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
                ball.body.velocity = Vec2d(0, 0)

        screen.fill((0, 0, 0))

        for ball in balls:
            ball.draw(screen)

        # Display the count of struck and strike balls
        strike_count = sum(1 for ball in balls if ball.color == STRIKE_COLOR)
        struck_count = sum(1 for ball in balls if ball.color == STRUCK_COLOR)
        text = font.render(f"Strike: {strike_count} | Struck: {struck_count}", True, TEXT_COLOR)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FRAME_RATE)

    pygame.quit()

if __name__ == "__main__":
    main()

