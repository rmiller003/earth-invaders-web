import pygame
from alien import Alien, FRENZY_SPEED_MULTIPLIER, ALIEN_BASE_SPEED # Assuming constants are accessible

class TestAlienFrenzy:
    def setup_method(self):
        pygame.init() # Minimal init
        # Alien class loads images, which might need a display initialized,
        # though for these tests, we are not checking rendering.
        # To be safe and avoid potential pygame.error: No video mode has been set
        try:
            pygame.display.set_mode((100, 100))
        except pygame.error:
            print("Warning: Pygame display could not be initialized in TestAlienFrenzy (headless environment?).")
        self.alien = Alien(type=1, x=50, y=50)

    def test_alien_normal_speed(self):
        initial_x = self.alien.rect.x
        # Simulate update: direction=1, game_speed_modifier=1.0
        self.alien.update(direction=1, speed_modifier=1.0)
        # Expected speed is ALIEN_BASE_SPEED * 1.0
        assert self.alien.rect.x == initial_x + int(ALIEN_BASE_SPEED * 1.0)

    def test_alien_frenzied_speed(self):
        self.alien.is_frenzied = True
        initial_x = self.alien.rect.x
        # Simulate update: direction=1, game_speed_modifier=1.0
        self.alien.update(direction=1, speed_modifier=1.0)
        expected_frenzied_speed = int(ALIEN_BASE_SPEED * 1.0 * FRENZY_SPEED_MULTIPLIER)
        assert self.alien.rect.x == initial_x + expected_frenzied_speed, \
            f"Expected speed {expected_frenzied_speed}, got {self.alien.rect.x - initial_x}"

    def test_alien_frenzied_speed_with_game_modifier(self):
        self.alien.is_frenzied = True
        game_mod = 1.5
        initial_x = self.alien.rect.x
        self.alien.update(direction=1, speed_modifier=game_mod)
        expected_frenzied_speed = int(ALIEN_BASE_SPEED * game_mod * FRENZY_SPEED_MULTIPLIER)
        assert self.alien.rect.x == initial_x + expected_frenzied_speed, \
            f"Expected speed {expected_frenzied_speed}, got {self.alien.rect.x - initial_x}"

    def teardown_method(self):
        pygame.quit()
