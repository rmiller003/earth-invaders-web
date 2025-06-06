import pygame
# Ensuring file is re-processed

# Laser specific constants
PLAYER_LASER_WIDTH = 4
PLAYER_LASER_HEIGHT = 15
PLAYER_LASER_COLOR_R = 243
PLAYER_LASER_COLOR_G = 216
PLAYER_LASER_COLOR_B = 63

ALIEN_LASER_WIDTH = 4
ALIEN_LASER_HEIGHT = 15
ALIEN_LASER_COLOR_R = 255
ALIEN_LASER_COLOR_G = 0
ALIEN_LASER_COLOR_B = 0

class Laser(pygame.sprite.Sprite):
    def __init__(self, position, speed, screen_height):
        super().__init__()
        self.image = pygame.Surface((PLAYER_LASER_WIDTH, PLAYER_LASER_HEIGHT))
        self.image.fill((PLAYER_LASER_COLOR_R, PLAYER_LASER_COLOR_G, PLAYER_LASER_COLOR_B))
        self.rect = self.image.get_rect(center = position)
        self.speed = speed
        self.screen_height = screen_height

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y > self.screen_height + 15 or self.rect.y < 0:
            self.kill()


class AlienLaser(pygame.sprite.Sprite):
    def __init__(self, position, speed, screen_height):
        super().__init__()
        self.image = pygame.Surface((ALIEN_LASER_WIDTH, ALIEN_LASER_HEIGHT))
        self.image.fill((ALIEN_LASER_COLOR_R, ALIEN_LASER_COLOR_G, ALIEN_LASER_COLOR_B))  # Red color
        self.rect = self.image.get_rect(center=position)
        self.speed = speed
        self.screen_height = screen_height

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > self.screen_height:
            self.kill()
