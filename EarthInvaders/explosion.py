import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center_position, image_surface, duration=200): # duration in milliseconds
        super().__init__()

        self.image = image_surface
        self.rect = self.image.get_rect(center=center_position)

        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.spawn_time > self.duration:
            self.kill() # Remove sprite after duration
