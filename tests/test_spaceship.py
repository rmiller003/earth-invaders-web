import pygame
from spaceship import Spaceship # Assuming spaceship.py is in parent directory or PYTHONPATH is set

class TestSpaceship:
    def setup_method(self):
        pygame.init() # Initialize Pygame modules
        # It's often good to set up a screen, even if not drawn to, for some Pygame functionalities
        # For tests that don't involve rendering, a dummy screen is fine.
        # However, Spaceship loads images, which might need a display initialized.
        try:
            pygame.display.set_mode((800, 600))
        except pygame.error as e:
            # This can happen in environments without a display server (e.g., CI)
            # We can try to work around it by setting a dummy video driver if needed
            # For now, let's print a warning and proceed, as some tests might pass.
            print(f"Warning: Pygame display could not be initialized: {e}. Some graphics-dependent tests might fail.")


        self.screen_width = 800
        self.screen_height = 600
        # It's important that the test can find the assets (images, sounds)
        # Assuming the test is run from the root directory of the project,
        # and Graphics/spaceship.png is available.
        self.spaceship = Spaceship(self.screen_width, self.screen_height)

    def test_spaceship_creation(self):
        assert self.spaceship is not None
        # Spaceship image is 64x64 by default if file loads, rect.centerx might not be exactly screen_width // 2
        # due to integer division and image width. midbottom is used for initial placement.
        assert self.spaceship.rect.midbottom == (self.screen_width // 2, self.screen_height)

    def test_spaceship_fire_laser_creates_laser(self):
        # Ensure laser can be fired
        self.spaceship.laser_ready = True

        initial_laser_count = len(self.spaceship.lasers_group)

        # Simulate spacebar press for firing logic
        # Mock pygame.key.get_pressed to simulate spacebar being pressed
        original_get_pressed = pygame.key.get_pressed

        # Create a mock dictionary for keys
        # K_RIGHT and K_LEFT are included because get_user_input checks them.
        keys_pressed_state = {key: False for key in range(512)} # Initialize all keys to False
        keys_pressed_state[pygame.K_SPACE] = True

        pygame.key.get_pressed = lambda: keys_pressed_state

        # Call update() which should call get_user_input()
        # get_user_input() will then attempt to fire a laser
        self.spaceship.update()

        pygame.key.get_pressed = original_get_pressed # Restore original function

        assert len(self.spaceship.lasers_group) > initial_laser_count

        # Check properties of the new laser
        # The new laser should be the last one added to the group
        new_laser = self.spaceship.lasers_group.sprites()[-1]
        assert new_laser.rect.centerx == self.spaceship.rect.centerx
        # Laser starts slightly above the spaceship's center
        assert new_laser.rect.centery < self.spaceship.rect.centery


    def teardown_method(self):
        pygame.quit()
