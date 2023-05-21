import pygame
import random
import pymunk
from pygame.locals import *
from pymunk import Vec2d

class Ball:
    def __init__(self, space, color, pos, velocity, size):
        self.size = size
        self.color = color
        mass = 1
        inertia = pymunk.moment_for_circle(mass, 0, size // 2)
        self.body = pymunk.Body(mass, inertia)
        self.body.position = pos
        self.body.velocity = velocity
        self.shape = pymunk.Circle(self.body, size // 2)
        self.shape.elasticity = 1.0
        self.shape.friction = 0.0
        space.add(self.body, self.shape)

    def draw(self, screen):
        if any(v != v for v in self.body.position):
            return
        x, y = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(screen, self.color, (x, y), self.size // 2)

def main():
    # Parameters
    num_balls = 100
    ball_speed = 250
    ball_size = 20

    pygame.init()
    screen_size = (800, 600)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    pygame.display.set_caption("Press 'Q' to quit")

    # Initialize Pymunk space
    space = pymunk.Space()
    space.gravity = (0.0, 0.0)

    # Add balls to the space
    balls = []
    for _ in range(num_balls):
        color = (random.randint(10, 255), random.randint(25, 255), random.randint(25, 255))
        pos = (random.randint(0, screen_size[0]), random.randint(0, screen_size[1]))
        velocity = Vec2d(random.uniform(-ball_speed, ball_speed), random.uniform(-ball_speed, ball_speed))
        ball = Ball(space, color, pos, velocity, ball_size)
        balls.append(ball)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_q)):
                running = False
            if event.type == VIDEORESIZE:
                screen_size = event.size
                screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

        # Step the physics simulation
        space.step(1/60)

        # Update ball positions and handle collisions with the screen boundaries
        for ball in balls:
            x, y = ball.body.position
            vx, vy = ball.body.velocity

            if x - ball.size // 2 < 0 and vx < 0:
                vx = abs(vx)
            elif x + ball.size // 2 > screen_size[0] and vx > 0:
                vx = -abs(vx)

            if y - ball.size // 2 < 0 and vy < 0:
                vy = abs(vy)
            elif y + ball.size // 2 > screen_size[1] and vy > 0:
                vy = -abs(vy)

            ball.body.velocity = Vec2d(vx, vy)

                        # Reset position if NaN occurs
            if any(v != v for v in ball.body.position):
                ball.body.position = Vec2d(screen_size[0] / 2, screen_size[1] / 2)
                ball.body.velocity = Vec2d(0, 0)

        screen.fill((0, 0, 0))

        for ball in balls:
            ball.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

