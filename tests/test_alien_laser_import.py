import pygame

# Attempt to import the classes directly
try:
    from laser import AlienLaser
    from alien import Alien
except ImportError as e:
    # This will help diagnose if the basic import itself fails
    print(f"Critical import error in test setup: {e}")
    AlienLaser = None
    Alien = None

class TestAlienLaserUsage:
    def setup_method(self):
        pygame.init()
        # Minimal display setup if any Pygame component used by Alien/AlienLaser needs it
        # For Alien and AlienLaser instantiation as defined, it might not be strictly necessary
        # but good practice if sprite system is touched.
        try:
            pygame.display.set_mode((100, 100))
        except pygame.error:
            print("Warning: Pygame display could not be initialized in test (headless environment?).")


    def test_alien_can_create_alien_laser(self):
        """Tests if an Alien instance can successfully create an AlienLaser."""
        if Alien is None or AlienLaser is None:
            assert False, "Alien or AlienLaser class failed to import."

        # Parameters for Alien instantiation
        alien_type = 1
        x_pos = 50
        y_pos = 50
        screen_height = 600 # Mock screen_height needed for fire_laser

        test_alien = Alien(type=alien_type, x=x_pos, y=y_pos)

        # Call the method that was causing the NameError
        try:
            created_laser = test_alien.fire_laser(screen_height=screen_height)
            assert isinstance(created_laser, AlienLaser),                 f"Expected AlienLaser instance, got {type(created_laser)}"
        except NameError as e:
            assert False, f"NameError encountered during fire_laser: {e}"
        except Exception as e:
            assert False, f"An unexpected error occurred during fire_laser: {e}"

    def teardown_method(self):
        pygame.quit()
