import pygame
from laser import Laser

# Spaceship specific constants
SPACESHIP_SPEED = 5
LASER_DELAY_MS = 300
PLAYER_LASER_SPEED = 7

SHIELD_DURATION_MS = 3000
SHIELD_COOLDOWN_MS = 7000
SHIELD_AURA_COLOR = (100, 100, 255, 120) # Light blue, semi-transparent (R, G, B, Alpha)

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, start_invincible=False): # Removed speed_modifier
        super().__init__( )
        self.screen_width = screen_width
        self.screen_height = screen_height
        # self.speed_modifier = speed_modifier # Removed speed_modifier store

        try:
            self.image = pygame.image.load("assets/Graphics/spaceship.png").convert_alpha() # Added convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load 'assets/Graphics/spaceship.png'. Error: {e}. Using placeholder for spaceship.")
            self.image = pygame.Surface((50, 50)) # Example placeholder size
            self.image.fill((0, 0, 255)) # Blue placeholder

        self.rect = self.image.get_rect(midbottom = (self.screen_width/2, self.screen_height))
        self.speed = SPACESHIP_SPEED # Set to constant integer value
        self.lasers_group = pygame.sprite.Group()
        self.laser_ready = True
        self.laser_time = 0
        self.laser_delay = LASER_DELAY_MS

        self.invincible = False
        self.invincible_duration_ms = 2000 # Match Game.invincibility_duration_ms
        self.invincible_active_time = 0 # When invincibility was turned on
        self.blink_on = True # For visual blinking

        if start_invincible:
            self.invincible = True
            self.invincible_active_time = pygame.time.get_ticks()

        # Laser sound
        try:
            self.laser_sound = pygame.mixer.Sound("assets/Sounds/laser.ogg")
            self.laser_sound.set_volume(0.9)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load 'assets/Sounds/laser.ogg' for spaceship. Error: {e}. Spaceship laser will be silent.")
            self.laser_sound = None

        # Shield attributes
        self.shield_active = False
        self.shield_activation_time = 0
        self.shield_last_activation_time = -SHIELD_COOLDOWN_MS # Allow immediate first use

        # Shield aura surface
        aura_radius = int(max(self.rect.width, self.rect.height) * 0.75)
        self.shield_aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.shield_aura_surface, SHIELD_AURA_COLOR, (aura_radius, aura_radius), aura_radius)

    def get_user_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.laser_ready:
            self.laser_ready = False
            laser_speed = PLAYER_LASER_SPEED
            laser = Laser(self.rect.center, laser_speed, self.screen_height)
            self.lasers_group.add(laser)
            self.laser_time = pygame.time.get_ticks()
            if self.laser_sound: # Play sound only if it loaded
                self.laser_sound.play()

        if keys[pygame.K_UP]:
            current_time = pygame.time.get_ticks()
            if not self.shield_active and (current_time - self.shield_last_activation_time > SHIELD_COOLDOWN_MS):
                self.shield_active = True
                self.shield_activation_time = current_time
                self.shield_last_activation_time = current_time # Record activation time for cooldown
                # Optional: Play shield activation sound here if one is chosen later

    def update(self):
        # Current invincibility logic (for post-respawn)
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_active_time > self.invincible_duration_ms:
                self.invincible = False
                self.blink_on = True # Ensure it's visible when invincibility ends
            else:
                # Simple blink: toggle visibility every 100ms (5 blinks per second if 100ms on, 100ms off)
                if (current_time // 100) % 2 == 0:
                    self.blink_on = True
                else:
                    self.blink_on = False
        else:
            self.blink_on = True # Ensure visible when not invincible

        # Shield duration check
        if self.shield_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.shield_activation_time > SHIELD_DURATION_MS:
                self.shield_active = False
                # Optional: Play shield deactivation sound

        self.get_user_input()
        self.constrain_movement()
        self.lasers_group.update()
        self.recharge_laser()

    def constrain_movement(self):
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.left < 0:
            self.rect.left = 0

    def recharge_laser(self):
        if not self.laser_ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_delay:
                self.laser_ready = True
