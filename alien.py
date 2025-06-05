import pygame
import laser  # Import the laser module
# Re-confirming imports and structure

# Alien specific constants
ALIEN_BASE_SPEED = 2
ALIEN_LASER_SPEED = 4
FRENZY_SPEED_MULTIPLIER = 2.0 # Example: Aliens move twice as fast in frenzy mode

class Alien(pygame.sprite.Sprite):
    def __init__(self, type, x, y): # Removed speed_modifier parameter
        super().__init__()
        self.type = type
        path = f"assets/Graphics/alien_{type}.png"
        try:
            self.image = pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load alien graphic '{path}'. Error: {e}. Using placeholder for alien.")
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect(topleft=(x, y))
        # self.speed_modifier = speed_modifier # Removed
        self.base_speed = ALIEN_BASE_SPEED # Set base_speed to 2
        self.is_frenzied = False # Add this line

    def update(self, direction, speed_modifier=1.0): # Renamed parameter
        effective_speed = int(self.base_speed * speed_modifier)
        if self.is_frenzied:
            effective_speed = int(effective_speed * FRENZY_SPEED_MULTIPLIER)
        self.rect.x += direction * effective_speed

    def shoot_laser(self, game_lasers_group, screen_height):
        # Create a new Laser instance (classic player-style laser)
        # Assuming speed 5 for this player-style laser fired by an alien
        laser_instance = laser.Laser(self.rect.midbottom, 5, screen_height)
        game_lasers_group.add(laser_instance)

    def fire_laser(self, screen_height):
        # Create a new AlienLaser instance (e.g., red beam or custom alien laser)
        laser_speed = ALIEN_LASER_SPEED # Set to constant as self.speed_modifier is removed
        laser_instance = laser.AlienLaser(self.rect.center, laser_speed, screen_height)
        return laser_instance
