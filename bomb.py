import pygame

# Bomb specific constants
BOMB_SURFACE_WIDTH = 12
BOMB_SURFACE_HEIGHT = 18
BOMB_COLOR_R = 255
BOMB_COLOR_G = 165
BOMB_COLOR_B = 0

class Bomb(pygame.sprite.Sprite):
    def __init__(self, position, speed, screen_height):
        super().__init__()
        self.image = pygame.Surface((BOMB_SURFACE_WIDTH, BOMB_SURFACE_HEIGHT))  # A bit larger and different aspect ratio than lasers
        self.image.fill((BOMB_COLOR_R, BOMB_COLOR_G, BOMB_COLOR_B))  # Dark red color for bombs
        self.rect = self.image.get_rect(center=position)
        self.speed = speed
        self.screen_height = screen_height

    def update(self):
        self.rect.y += self.speed  # Move downwards
        if self.rect.top > self.screen_height:
            self.kill()
