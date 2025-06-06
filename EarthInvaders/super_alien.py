import pygame
import random

# Super Alien specific constants
SUPER_ALIEN_DEFAULT_SPEED = 3
SUPER_ALIEN_POINTS = 300
SUPER_ALIEN_BOMB_DROP_CHANCE = 0.01

class SuperAlien(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, speed=SUPER_ALIEN_DEFAULT_SPEED):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height # May not be strictly needed for horizontal movement but good to have

        self.image = pygame.image.load("Graphics/mystery.png").convert_alpha()

        # Determine spawn side (left or right)
        self.spawn_side = random.choice(["left", "right"])
        if self.spawn_side == "left":
            self.rect = self.image.get_rect(midleft=(-self.image.get_width(), 60)) # Spawn just off-screen left, at y=60
            self.speed = speed
        else: # right
            self.rect = self.image.get_rect(midright=(screen_width + self.image.get_width(), 60)) # Spawn just off-screen right
            self.speed = -speed # Move left

        self.points = SUPER_ALIEN_POINTS # Points when hit
        self.bomb_drop_chance = SUPER_ALIEN_BOMB_DROP_CHANCE # Chance to drop a bomb per update (e.g., 1%) - can be tuned
        self.initial_bomb_burst_fired = False # Add this line

    def update(self):
        self.rect.x += self.speed

        # Check if off-screen
        if self.speed > 0 and self.rect.left > self.screen_width: # Moving right, went off right edge
            self.kill()
        elif self.speed < 0 and self.rect.right < 0: # Moving left, went off left edge
            self.kill()

        # Bomb dropping logic will be added here later or called from here
        # For now, this is a placeholder for where it would integrate
        # if random.random() < self.bomb_drop_chance:
        #     # Create and return a bomb or add to a bomb group passed in
        #     pass

    # Placeholder for bomb dropping - actual bomb creation will be handled by Game class
    # based on a signal from this update or by Game class directly checking conditions
    def should_drop_bomb(self):
        return random.random() < self.bomb_drop_chance
