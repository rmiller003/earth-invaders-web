import pygame
import os
from game import Game # Assuming game.py is in parent directory or PYTHONPATH is set
from spaceship import Spaceship
from bomb import Bomb
from explosion import Explosion
from alien import Alien
from game import FRENZY_ALIEN_COUNT, FRENZY_SHOOT_PROBABILITY, ALIEN_SHOOT_PROBABILITY
import random

# Constants expected by Game class (if not already imported/available, define them here for the test)
# For example, if Game relies on constants like ALIEN_SCORE_VALUE, etc., ensure they are accessible.
# However, Game should use its own internal constants or receive them.
# The provided Game class seems to define these internally or expects them to be globally available.
# For robust tests, it's better if Game is self-contained or takes config.
# For now, we assume game.py's constants are accessible if defined globally there.

class TestGame:
    def setup_method(self):
        pygame.init()
        # Game class attempts to load sounds, so mixer should be initialized.
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Warning: Pygame mixer could not be initialized: {e}. Sound-dependent tests might behave differently.")

        # Game class loads images and creates display elements, so display mode is needed.
        try:
            pygame.display.set_mode((800, 600))
        except pygame.error as e:
            print(f"Warning: Pygame display could not be initialized: {e}. Graphics-dependent tests might fail.")

        self.screen_width = 800
        self.screen_height = 600

        # Game __init__ may try to load assets from relative paths.
        # Ensure the CWD is the project root when running tests.
        # Example: If "Graphics/alien_1.png" is loaded, it must be findable.
        self.game = Game(self.screen_width, self.screen_height)

    def test_game_creation_initial_state(self):
        assert self.game is not None
        assert not self.game.game_over
        # Assuming default lives is 3, this might come from a constant later
        assert self.game.lives == 3
        assert self.game.score == 0

    def test_game_initializes_player_spaceship(self):
        assert self.game.spaceship_group.sprite is not None
        # Check initial position of the spaceship
        # Spaceship is placed at midbottom of the screen
        expected_centerx = self.screen_width // 2
        assert self.game.spaceship_group.sprite.rect.midbottom == (expected_centerx, self.screen_height)

    def test_game_creates_aliens(self):
        # Game's create_aliens method should populate the aliens_group
        assert len(self.game.aliens_group) > 0
        # Optionally, check type of first alien or specific properties
        first_alien = self.game.aliens_group.sprites()[0]
        assert first_alien is not None

    def test_game_creates_obstacles(self):
        # Game's create_obstacles method should populate self.obstacles
        assert len(self.game.obstacles) == 4 # Game creates 4 obstacles by default
        # Check that obstacles have blocks
        # Each obstacle should have a group of blocks
        assert len(self.game.obstacles[0].blocks_group) > 0
        first_block = self.game.obstacles[0].blocks_group.sprites()[0]
        assert first_block is not None

    def teardown_method(self):
        pygame.quit()

    def test_player_explosion_on_bomb_hit(self):
        # Ensure game is in a state where player can be hit
        self.game.game_over = False
        self.game.lives = 3 # Start with full lives

        # Create and add player spaceship
        # Need to ensure the spaceship is not part of the group from setup_method if it's the same instance
        # For this test, let's clear the game's spaceship_group first or ensure it's empty.
        self.game.spaceship_group.empty() # Clear existing spaceship from game setup

        player_ship = Spaceship(self.game.screen_width, self.game.screen_height)
        player_ship.rect.center = (self.game.screen_width / 2, self.game.screen_height - 50)
        player_ship.invincible = False # Ensure player is not invincible
        self.game.spaceship_group.add(player_ship)

        # Create and add a bomb at the same position as the spaceship
        bomb_position = player_ship.rect.center
        # BOMB_SPEED is a constant in bomb.py, but for Game class, it's passed.
        # SUPER_ALIEN_BOMB_SPEED = 5 (constant in game.py used by Game logic)
        bomb = Bomb(position=bomb_position, speed=5, screen_height=self.game.screen_height)
        self.game.bombs_group.add(bomb)

        initial_explosions_count = len(self.game.explosions_group)
        initial_lives = self.game.lives

        # Call the collision detection method
        self.game.check_hostile_projectile_collisions()

        # Assertions
        assert len(self.game.explosions_group) > initial_explosions_count, "Explosion should be added."
        # Check that the new explosion is an Explosion object (optional, but good)
        # new_explosion = self.game.explosions_group.sprites()[-1] # Requires at least one explosion
        # assert isinstance(new_explosion, Explosion), "New explosion is not an Explosion instance."

        assert self.game.lives == initial_lives - 1, "Player lives should decrease by 1."
        # Player spaceship should be killed
        assert len(self.game.spaceship_group) == 0, "Player spaceship should be removed from group."

    def test_game_over_when_alien_reaches_bottom(self):
        # Ensure game is not initially over
        self.game.game_over = False

        # Clear any aliens created by game setup
        self.game.aliens_group.empty()

        # Create a new alien
        # Alien(type, x, y)
        test_alien = Alien(type=1, x=self.game.screen_width / 2, y=self.game.screen_height - 20) # y doesn't matter as much as rect.bottom

        # Manually set its position to be at the bottom of the screen
        test_alien.rect.bottom = self.game.screen_height

        self.game.aliens_group.add(test_alien)

        # Call move_aliens, which contains the check
        # Note: move_aliens might have side effects (like changing alien_direction or speed_modifier)
        # but for this test, we are primarily concerned with it triggering game_over.
        self.game.move_aliens()

        assert self.game.game_over == True, "Game should be over when an alien reaches the bottom."

    def test_extra_life_awarded_at_1000_points(self):
        self.game.score = 990
        self.game.lives = 3
        self.game.next_life_score = 1000 # Explicitly set for test clarity
        self.game.points_for_extra_life = 1000

        # Simulate scoring 10 more points
        self.game.score += 10 # Score becomes 1000

        # Call the (potentially refactored) extra life check.
        # If not refactored, this test needs to simulate a collision that awards points.
        # Assuming helper method _check_and_award_extra_life exists:
        self.game._check_and_award_extra_life()

        assert self.game.lives == 4, "Should gain an extra life at 1000 points."
        assert self.game.next_life_score == 2000, "Next life threshold should be 2000."

    def test_multiple_extra_lives_awarded_if_large_score_jump(self):
        self.game.score = 990
        self.game.lives = 3
        self.game.next_life_score = 1000
        self.game.points_for_extra_life = 1000

        # Simulate scoring 1050 more points (e.g. super alien + regular alien)
        # Total score will be 990 + 1050 = 2040
        self.game.score += 1050

        self.game._check_and_award_extra_life()

        assert self.game.lives == 5, "Should gain two extra lives (1 at 1000, 1 at 2000)."
        assert self.game.next_life_score == 3000, "Next life threshold should be 3000."

    def test_no_extra_life_below_threshold(self):
        self.game.score = 500
        self.game.lives = 3
        self.game.next_life_score = 1000
        self.game.points_for_extra_life = 1000

        self.game._check_and_award_extra_life()

        assert self.game.lives == 3, "Should not gain an extra life if score is below threshold."
        assert self.game.next_life_score == 1000, "Next life threshold should remain 1000."

    def test_next_life_score_updates_correctly_after_multiple_lives(self):
        # Test scenario: score starts at 0, gain 3000 points.
        self.game.score = 0
        self.game.lives = 3
        self.game.next_life_score = 1000
        self.game.points_for_extra_life = 1000

        self.game.score += 3000 # Score becomes 3000
        self.game._check_and_award_extra_life()

        assert self.game.lives == 6, "Should have 3 + 3 = 6 lives." # 1k, 2k, 3k
        assert self.game.next_life_score == 4000, "Next life threshold should be 4000."

    def test_bomb_destroys_entire_obstacle_with_big_explosion(self):
        # Ensure there are obstacles; game.__init__ creates them.
        # Pick the first obstacle for testing.
        if not self.game.obstacles:
            assert False, "No obstacles found for testing."
        test_obstacle = self.game.obstacles[0]

        # Ensure the obstacle has blocks initially
        if not test_obstacle.blocks_group.sprites():
            # If for some reason the test setup results in an empty obstacle,
            # we might need to manually add blocks or re-initialize obstacles.
            # For now, assume game.create_obstacles() in setup_method populates them.
            # If this fails, the test setup for obstacles needs review.
            print("Warning: Test obstacle has no blocks initially. Re-creating.")
            self.game.obstacles = self.game.create_obstacles() # Re-create obstacles
            test_obstacle = self.game.obstacles[0]
            if not test_obstacle.blocks_group.sprites():
                 assert False, "Failed to ensure obstacle has blocks for test."


        initial_block_count = len(test_obstacle.blocks_group.sprites())
        assert initial_block_count > 0, "Test obstacle should have blocks."

        # Create a bomb and position it to hit the first block of this obstacle
        first_block = test_obstacle.blocks_group.sprites()[0]
        bomb_position = first_block.rect.center

        # SUPER_ALIEN_BOMB_SPEED is a constant in game.py (value 5)
        bomb = Bomb(position=bomb_position, speed=5, screen_height=self.game.screen_height)
        self.game.bombs_group.add(bomb)

        initial_explosions_count = len(self.game.explosions_group)

        # Call the collision detection method
        self.game.check_hostile_projectile_collisions()

        # Assertions
        assert len(test_obstacle.blocks_group.sprites()) == 0, "Entire obstacle should be destroyed (all blocks removed)."
        assert len(self.game.explosions_group) > initial_explosions_count, "A big explosion should be added."

        # Optional: Verify properties of the explosion if desired (e.g., duration, image if mockable)
        # new_explosion = self.game.explosions_group.sprites()[-1]
        # assert new_explosion.duration == 1200

        # Assert bomb is consumed
        assert bomb not in self.game.bombs_group, "Bomb should be consumed after destroying obstacle."

    def test_frenzy_mode_activates_correctly(self):
        self.game.aliens_group.empty() # Clear default aliens
        self.game.frenzy_mode_activated_this_round = False # Reset flag

        # Add FRENZY_ALIEN_COUNT aliens
        for i in range(FRENZY_ALIEN_COUNT):
            self.game.aliens_group.add(Alien(type=1, x=50 + i*30, y=50))

        assert len(self.game.aliens_group) == FRENZY_ALIEN_COUNT

        # Call the method that checks and activates frenzy mode
        self.game._check_and_activate_frenzy_mode()

        assert self.game.frenzy_mode_activated_this_round == True, "Frenzy mode should be activated."
        for alien in self.game.aliens_group.sprites():
            assert alien.is_frenzied == True, "All remaining aliens should be frenzied."

    def test_frenzy_mode_does_not_activate_if_more_than_threshold_aliens(self):
        self.game.aliens_group.empty()
        self.game.frenzy_mode_activated_this_round = False

        # Add FRENZY_ALIEN_COUNT + 1 aliens
        for i in range(FRENZY_ALIEN_COUNT + 1):
            self.game.aliens_group.add(Alien(type=1, x=50 + i*30, y=50))

        self.game._check_and_activate_frenzy_mode()

        assert self.game.frenzy_mode_activated_this_round == False
        for alien in self.game.aliens_group.sprites():
            assert getattr(alien, 'is_frenzied', False) == False # Check safely

    def test_frenzied_aliens_higher_shoot_probability(self):
        # This test is probabilistic, so it's harder to assert definitively.
        # We can test the selection of probability.
        # Or mock random.random() to control outcomes.

        # Mocking random.random is more robust for testing selection logic
        original_random_random = random.random

        # Test case 1: Frenzied alien, random value just below FRENZY_SHOOT_PROBABILITY
        try:
            test_alien = Alien(type=1, x=50, y=50)
            test_alien.is_frenzied = True
            self.game.aliens_group.empty()
            self.game.aliens_group.add(test_alien)

            # Control random outcome to ensure it's less than FRENZY_SHOOT_PROBABILITY
            # but potentially greater than ALIEN_SHOOT_PROBABILITY
            random.random = lambda: FRENZY_SHOOT_PROBABILITY - 0.01

            self.game.alien_lasers_group.empty()
            self.game.alien_shoot() # Call method that uses the probability
            assert len(self.game.alien_lasers_group) == 1, "Frenzied alien should shoot."

        finally:
            random.random = original_random_random # Restore

        # Test case 2: Non-frenzied alien, same random value (should not shoot if value > ALIEN_SHOOT_PROBABILITY)
        try:
            test_alien_normal = Alien(type=1, x=50, y=50)
            test_alien_normal.is_frenzied = False # Explicitly not frenzied
            self.game.aliens_group.empty()
            self.game.aliens_group.add(test_alien_normal)

            # This value is < FRENZY_SHOOT_PROBABILITY (0.1) but > ALIEN_SHOOT_PROBABILITY (0.005)
            random.random = lambda: FRENZY_SHOOT_PROBABILITY - 0.01

            self.game.alien_lasers_group.empty()
            self.game.alien_shoot()
            # Assuming FRENZY_SHOOT_PROBABILITY - 0.01 is still > ALIEN_SHOOT_PROBABILITY
            if (FRENZY_SHOOT_PROBABILITY - 0.01) > ALIEN_SHOOT_PROBABILITY:
                 assert len(self.game.alien_lasers_group) == 0, "Normal alien should not shoot with this random value."
            else:
                # This case would mean our test random value is too low and also falls under normal probability
                pass

        finally:
            random.random = original_random_random # Restore
