import pygame
import random
import traceback # Added import
from spaceship import Spaceship
from obstacle import Obstacle
from obstacle import grid
from alien import Alien
from super_alien import SuperAlien
from bomb import Bomb
from explosion import Explosion

# Game specific constants
ALIEN_SHOOT_PROBABILITY = 0.005
ALIEN_SCORE_VALUE = 10
SUPER_ALIEN_INITIAL_BOMB_BURST_COUNT = 20
SUPER_ALIEN_BOMB_SPEED = 5
OBSTACLE_DAMAGE_PLAYER_LASER = 2
OBSTACLE_DAMAGE_ALIEN_LASER = 2
OBSTACLE_DAMAGE_BOMB = 5

FRENZY_ALIEN_COUNT = 5
FRENZY_SHOOT_PROBABILITY = 0.1

class Game:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # self.victory = False # Removed
        self.game_over = False
        self.game_speed_modifier = 1.0
        self.alien_descents = 0 # Re-adding for tracking alien descents

        self.lives = 3
        self.spaceship_respawn_time = 0  # Timestamp for when respawn should occur
        self.invincibility_duration_ms = 2000 # Duration of invincibility in ms
        self.respawn_delay_ms = 2000 # Delay before respawn in ms

        # Super Alien spawn timer attributes
        self.super_alien_spawn_time_min = 20000  # milliseconds (20 seconds)
        self.super_alien_spawn_time_max = 40000  # milliseconds (40 seconds)
        self.super_alien_next_spawn_time = pygame.time.get_ticks() + random.randint(self.super_alien_spawn_time_min, self.super_alien_spawn_time_max)

        # Essential group initializations, even if other parts fail
        self.spaceship_group = pygame.sprite.GroupSingle()
        self.aliens_group = pygame.sprite.Group()
        self.alien_lasers_group = pygame.sprite.Group()
        self.super_alien_group = pygame.sprite.GroupSingle()
        self.bombs_group = pygame.sprite.Group()
        self.explosions_group = pygame.sprite.Group()

        try:
            # Removed speed_modifier from Spaceship constructor
            initial_spaceship = Spaceship(self.screen_width, self.screen_height)
            self.spaceship_group.add(initial_spaceship)

            self.obstacles = self.create_obstacles()
            self.create_aliens() # Will pass game_speed_modifier
            self.aliens_direction = 1
            self.score = 0

            self.points_for_extra_life = 1000
            self.next_life_score = self.points_for_extra_life
            self.frenzy_mode_activated_this_round = False
            self.current_level_number = 1 # Add this

            # Explosion sound
            try:
                self.explosion_sound = pygame.mixer.Sound("assets/Sounds/explosion.ogg")
                self.explosion_sound.set_volume(0.3)
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load 'assets/Sounds/explosion.ogg'. Error: {e}. Explosions will be silent.")
                self.explosion_sound = None # Set to None if loading fails

            # Alien laser sound
            try:
                self.alien_laser_sound = pygame.mixer.Sound("assets/Sounds/alien_laser.ogg")
                self.alien_laser_sound.set_volume(0.3)  # Adjust volume as needed
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load 'assets/Sounds/alien_laser.ogg'. Error: {e}. Alien lasers will be silent.")
                self.alien_laser_sound = None

            self.alien_down_step = 10 # How much aliens move down when hitting an edge

            # Super Explosion sound
            try:
                self.super_explosion_sound = pygame.mixer.Sound("assets/Sounds/epic_explosion.ogg")
                self.super_explosion_sound.set_volume(0.5) # Adjust volume as needed
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load 'assets/Sounds/epic_explosion.ogg'. Error: {e}. Super explosions will use default sound or be silent.")
                self.super_explosion_sound = None # Fallback to None

            # Pre-load explosion images
            self.super_explosion_img = None
            self.regular_explosion_img = None
            self.explosion_placeholder_img = pygame.Surface((30,30)) # Default placeholder size
            self.explosion_placeholder_img.fill((255,255,0)) # Yellow

            try:
                self.super_explosion_img = pygame.image.load("assets/Graphics/explosion.png").convert_alpha()
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load 'assets/Graphics/explosion.png'. Error: {e}. Super explosions will use placeholder.")
                # self.super_explosion_img remains None or use placeholder

            try:
                self.regular_explosion_img = pygame.image.load("assets/Graphics/explosion2.png").convert_alpha()
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load 'assets/Graphics/explosion2.png'. Error: {e}. Regular explosions will use placeholder.")
                # self.regular_explosion_img remains None or use placeholder

        except Exception as e:
            print(traceback.format_exc())
        finally:
            pass

    def create_obstacles(self):
        obstacle_width = len(grid[0]) * 3
        gap = (self.screen_width - (4 * obstacle_width))/5
        obstacles = []
        for i in range(4):
            offset_x = (i + 1) * gap + i * obstacle_width
            obstacle = Obstacle(offset_x, self.screen_height - 100)
            obstacles.append(obstacle)
        return obstacles

    def create_aliens(self):
        for row in range(5):
            for column in range(11):
                x = 75 + column * 55
                y = 110 + row * 55

                if row == 0:
                    alien_type = 3
                elif row in (1,2):
                    alien_type = 2
                else:
                    alien_type = 1

                # Removed speed_modifier from Alien constructor
                alien = Alien(alien_type, x, y)
                self.aliens_group.add(alien)

    def move_aliens(self):
        # Still move all aliens first
        # Pass speed_modifier to aliens_group.update
        self.aliens_group.update(self.aliens_direction, self.game_speed_modifier)

        # Store current direction before checking for reversal
        previous_direction = self.aliens_direction

        alien_sprites = self.aliens_group.sprites()
        for alien in alien_sprites:
            if alien.rect.right >= self.screen_width and self.aliens_direction == 1: # Check direction before flipping
                self.aliens_direction = -1
                break # Direction flipped, no need to check other aliens for this
            elif alien.rect.left <= 0 and self.aliens_direction == -1: # Check direction before flipping
                self.aliens_direction = 1
                break # Direction flipped

        # If direction changed, move all aliens down
        if self.aliens_direction != previous_direction:
            # Move all aliens down (ensure this loop appears only ONCE)
            for alien_sprite in self.aliens_group.sprites():
                alien_sprite.rect.y += self.alien_down_step

            self.alien_descents += 1

            if self.alien_descents % 2 == 0:
                self.game_speed_modifier *= 1.01

        # Check if any alien reached the bottom
        if not self.game_over: # Only check if game isn't already over for other reasons
            for alien in self.aliens_group.sprites():
                # Check against screen_height. Consider a small buffer if needed, e.g. spaceship height.
                # For now, direct comparison with screen_height.
                if alien.rect.bottom >= self.screen_height:
                    self.game_over = True
                    # This debug print should be removed before final commit of this feature.
                    break # Game is over, no need to check other aliens

    def check_collisions(self):
        if self.spaceship_group.sprite:
            # Player laser vs Aliens
            alien_collisions = pygame.sprite.groupcollide(self.spaceship_group.sprite.lasers_group, self.aliens_group, True, True)
            if alien_collisions:
                if self.explosion_sound:
                    self.explosion_sound.play()

                for aliens_hit_by_laser in alien_collisions.values(): # aliens_hit_by_laser is a list of aliens
                    for alien in aliens_hit_by_laser:
                        self.score += ALIEN_SCORE_VALUE
                        self._check_and_award_extra_life()

                        explosion_surface_to_use = None
                        if self.regular_explosion_img and self.super_explosion_img:
                            target_w = int(self.super_explosion_img.get_width() * 0.105) # Changed from 0.175
                            target_h = int(self.super_explosion_img.get_height() * 0.105) # Changed from 0.175
                            # Ensure minimum dimensions
                            target_w = max(1, target_w)
                            target_h = max(1, target_h)
                            explosion_surface_to_use = pygame.transform.smoothscale(self.regular_explosion_img, (target_w, target_h))
                        elif self.regular_explosion_img: # Super image failed, but regular loaded
                             explosion_surface_to_use = self.regular_explosion_img # Use as is
                        else: # Regular image failed (or both)
                            # Fallback: create a new placeholder surface with desired smaller size for regular aliens
                            placeholder_size = 20
                            explosion_surface_to_use = pygame.Surface((placeholder_size, placeholder_size))
                            explosion_surface_to_use.fill((255, 255, 0)) # Yellow

                        explosion = Explosion(center_position=alien.rect.center, image_surface=explosion_surface_to_use)
                        self.explosions_group.add(explosion)

            # Player laser vs Obstacles
            for obstacle in self.obstacles:
                obstacle_collisions = pygame.sprite.groupcollide(self.spaceship_group.sprite.lasers_group, obstacle.blocks_group, True, False)
                if obstacle_collisions:
                    for collided_blocks in obstacle_collisions.values():
                        for block in collided_blocks:
                            block.take_damage(OBSTACLE_DAMAGE_PLAYER_LASER) # CHANGED FROM 1 to 2

            # Player laser vs Super Alien
            if self.super_alien_group.sprite: # Check if super alien exists
                super_alien = self.super_alien_group.sprite
                if self.spaceship_group.sprite: # Ensure spaceship and its lasers exist
                    lasers_hit_super_alien = pygame.sprite.spritecollide(super_alien, self.spaceship_group.sprite.lasers_group, True)
                    if lasers_hit_super_alien:
                        super_alien.kill() # Kill the super alien
                        self.score += super_alien.points
                        self._check_and_award_extra_life()

                        if self.super_explosion_sound:
                            self.super_explosion_sound.play()
                        elif self.explosion_sound: # Fallback to default explosion sound
                            print("Info: 'epic_explosion.ogg' not loaded. Using default explosion sound for Super Alien.")
                            self.explosion_sound.play()
                        # If both are None, no sound plays, which is fine.

                        super_explosion_surface = self.super_explosion_img if self.super_explosion_img else self.explosion_placeholder_img
                        # If super_explosion_img failed to load, use the generic placeholder (30x30).
                        # Or, create a larger one if desired for super alien fallback:
                        if not self.super_explosion_img:
                             placeholder_size = 50
                             super_explosion_surface = pygame.Surface((placeholder_size, placeholder_size))
                             super_explosion_surface.fill((255,255,0))

                        explosion = Explosion(center_position=super_alien.rect.center, image_surface=super_explosion_surface)
                        self.explosions_group.add(explosion)

    def alien_shoot(self):
        if self.aliens_group.sprites():
            for alien in self.aliens_group.sprites():
                # Determine shoot probability based on frenzy state
                current_shoot_probability = FRENZY_SHOOT_PROBABILITY if getattr(alien, 'is_frenzied', False) else ALIEN_SHOOT_PROBABILITY

                if random.random() < current_shoot_probability:
                    new_laser = alien.fire_laser(self.screen_height)
                    self.alien_lasers_group.add(new_laser)
                    if self.alien_laser_sound:
                        self.alien_laser_sound.play()

    def check_hostile_projectile_collisions(self):
        # Alien laser vs Player Spaceship
        if self.spaceship_group.sprite: # Check if spaceship exists
            player_spaceship = self.spaceship_group.sprite # Convenience variable

            collided_lasers = pygame.sprite.spritecollide(player_spaceship, self.alien_lasers_group, True)
            if collided_lasers:
                player_shield_active = getattr(player_spaceship, 'shield_active', False)
                if player_shield_active:
                    for laser in collided_lasers:
                        laser.kill() # Destroy the laser
                    # Play shield hit sound here if available
                elif not getattr(player_spaceship, 'invincible', False): # Shield not active, check normal invincibility

                    # --- Add explosion effect ---
                    explosion_pos = player_spaceship.rect.center
                    explosion_img_to_use = self.super_explosion_img if self.super_explosion_img else self.explosion_placeholder_img
                    # If super_explosion_img failed to load, use the generic placeholder.
                    # Create a larger one for player if desired for super alien fallback:
                    if not self.super_explosion_img: # and self.explosion_placeholder_img is the small one
                         placeholder_size = 50 # Or match spaceship size approx
                         explosion_img_to_use = pygame.Surface((placeholder_size, placeholder_size))
                         explosion_img_to_use.fill((255,165,0)) # Orange placeholder for player

                    player_explosion = Explosion(center_position=explosion_pos, image_surface=explosion_img_to_use, duration=1000)
                    self.explosions_group.add(player_explosion)

                    # Play sound
                    if self.super_explosion_sound:
                        self.super_explosion_sound.play()
                    elif self.explosion_sound: # Fallback to default explosion sound
                        self.explosion_sound.play()
                    # --- End explosion effect ---

                    self.lives -= 1
                    player_spaceship.kill()

                    if self.lives > 0:
                        self.spaceship_respawn_time = pygame.time.get_ticks() + self.respawn_delay_ms
                    else:
                        self.game_over = True

        # Alien laser vs Obstacles
        for obstacle in self.obstacles:
            obstacle_collisions = pygame.sprite.groupcollide(self.alien_lasers_group, obstacle.blocks_group, True, False)
            if obstacle_collisions:
                for collided_blocks in obstacle_collisions.values(): # Corrected: iterate through values()
                    for block in collided_blocks:
                        block.take_damage(OBSTACLE_DAMAGE_ALIEN_LASER) # CHANGED FROM 1 to 2

        # Bomb vs Player Spaceship
        if self.spaceship_group.sprite: # Check if spaceship exists
            # Store a reference to the spaceship sprite for convenience
            player_spaceship = self.spaceship_group.sprite

            bombs_hitting_player = pygame.sprite.spritecollide(player_spaceship, self.bombs_group, True)
            if bombs_hitting_player:
                player_shield_active = getattr(player_spaceship, 'shield_active', False)
                if player_shield_active:
                    for bomb in bombs_hitting_player: # Iterate through all bombs that hit
                        bomb.kill() # Destroy the bomb
                    # Play shield hit sound here if available
                elif not getattr(player_spaceship, 'invincible', False): # Shield not active, check normal invincibility

                    # --- Add explosion effect ---
                    explosion_pos = player_spaceship.rect.center
                    explosion_img_to_use = self.super_explosion_img if self.super_explosion_img else self.explosion_placeholder_img
                    # If super_explosion_img failed to load, use the generic placeholder.
                    # Create a larger one for player if desired for super alien fallback:
                    if not self.super_explosion_img: # and self.explosion_placeholder_img is the small one
                         placeholder_size = 50 # Or match spaceship size approx
                         explosion_img_to_use = pygame.Surface((placeholder_size, placeholder_size))
                         explosion_img_to_use.fill((255,165,0)) # Orange placeholder for player

                    player_explosion = Explosion(center_position=explosion_pos, image_surface=explosion_img_to_use, duration=1000) # Duration updated
                    self.explosions_group.add(player_explosion)

                    # Play sound
                    if self.super_explosion_sound:
                        self.super_explosion_sound.play()
                    elif self.explosion_sound: # Fallback to default explosion sound
                        self.explosion_sound.play()
                    # --- End explosion effect ---

                    self.lives -= 1
                    # print(f"Player hit by bomb! Lives remaining: {self.lives}") # Debug print
                    player_spaceship.kill() # Kill the spaceship sprite

                    if self.lives > 0:
                        self.spaceship_respawn_time = pygame.time.get_ticks() + self.respawn_delay_ms
                    else:
                        # print("Game Over!") # Debug print
                        self.game_over = True

        # Bomb vs Obstacles
        # Iterate over a copy of self.obstacles if obstacles themselves might be removed from the list,
        # but here we are modifying blocks within them, not the list self.obstacles.
        for obstacle_index, obstacle in enumerate(self.obstacles):
            if not obstacle.blocks_group: # Skip if obstacle already destroyed
                continue

            # Check for collisions between any bomb and any block in THIS specific obstacle
            # We want to kill the bomb (first True) but not the blocks individually yet (False),
            # as we will destroy all of them if any are hit.
            # However, to get which bombs hit, we might need a different approach or check bomb properties.

            # Let's try this:
            # 1. Find bombs that hit blocks of this obstacle.
            # 2. If any, process destruction for this obstacle and those bombs.

            bombs_that_hit_this_obstacle = pygame.sprite.groupcollide(
                self.bombs_group,
                obstacle.blocks_group,
                False, # Don't kill bombs yet, we need to know which ones to kill after processing
                False  # Don't kill blocks yet, we kill all of them for the obstacle
            )

            if bombs_that_hit_this_obstacle: # If any bomb hit any block of this obstacle
                # Calculate obstacle center for the explosion (as per plan step 2)
                all_blocks = obstacle.blocks_group.sprites()
                if not all_blocks: # Should not happen if bombs_that_hit_this_obstacle is true, but good check
                    continue

                min_x = min(block.rect.left for block in all_blocks)
                max_x = max(block.rect.right for block in all_blocks)
                min_y = min(block.rect.top for block in all_blocks)
                max_y = max(block.rect.bottom for block in all_blocks)
                obstacle_center_x = min_x + (max_x - min_x) / 2
                obstacle_center_y = min_y + (max_y - min_y) / 2
                explosion_pos = (obstacle_center_x, obstacle_center_y)

                # Create big explosion (as per plan step 3)
                explosion_img = self.super_explosion_img if self.super_explosion_img else self.explosion_placeholder_img
                if not self.super_explosion_img: # Use a distinct placeholder if super_explosion_img is missing
                     placeholder_size = 70 # Larger placeholder for obstacle
                     explosion_img = pygame.Surface((placeholder_size, placeholder_size))
                     explosion_img.fill((200,200,0)) # Different color, e.g., olive

                big_explosion = Explosion(center_position=explosion_pos, image_surface=explosion_img, duration=1200) # Longer duration
                self.explosions_group.add(big_explosion)

                # Play sound (as per plan step 3)
                if self.super_explosion_sound:
                    self.super_explosion_sound.play()
                elif self.explosion_sound:
                    self.explosion_sound.play()

                # Destroy all blocks in this obstacle
                obstacle.blocks_group.empty() # Removes all sprites from the group, effectively destroying them

                # Kill the bombs that caused this destruction
                for bomb in bombs_that_hit_this_obstacle.keys():
                    bomb.kill()

                # Important: If an obstacle is destroyed, we might not want its space to be checked again by other bombs in this same frame.
                # However, obstacle.blocks_group.empty() handles this for subsequent checks against this obstacle.
                # No need to remove obstacle from self.obstacles, just make it empty.

    def _check_and_award_extra_life(self): # Helper method
        while self.score >= self.next_life_score:
            self.lives += 1
            self.next_life_score += self.points_for_extra_life

    def _check_and_activate_frenzy_mode(self):
        if not self.frenzy_mode_activated_this_round and \
           0 < len(self.aliens_group) <= FRENZY_ALIEN_COUNT:

            for alien in self.aliens_group.sprites():
                alien.is_frenzied = True
            self.frenzy_mode_activated_this_round = True

    def reset_game(self, new_round_started=False): # Signature changed
        if new_round_started:
            self.game_speed_modifier *= 1.0
            self.current_level_number += 1 # Add this
        else: # This means a reset from Game Over
            self.game_speed_modifier = 1.0
            self.current_level_number = 1 # Add this

        self.alien_descents = 0 # Re-adding reset for alien_descents
        self.game_over = False # Always reset game_over flag
        self.lives = 3 # Reset lives
        self.spaceship_respawn_time = 0 # Reset respawn timer

        # Spaceship
        if self.spaceship_group.sprite:
            self.spaceship_group.sprite.kill() # Kill the old sprite

        # Removed speed_modifier from Spaceship constructor
        spaceship = Spaceship(self.screen_width, self.screen_height)
        self.spaceship_group.add(spaceship)

        # Conditional score reset:
        # Conditional score reset:
        if not new_round_started: # Only reset score if it's NOT a new round (i.e., it's from Game Over)
            self.score = 0
            # Reset Super Alien spawn timer on full game reset
            self.super_alien_next_spawn_time = pygame.time.get_ticks() + random.randint(self.super_alien_spawn_time_min, self.super_alien_spawn_time_max)

        # Always reset frenzy mode for new round or new game
        self.frenzy_mode_activated_this_round = False

        # Obstacles
        self.obstacles = self.create_obstacles()

        # Aliens
        self.aliens_group.empty()
        self.create_aliens()
        self.aliens_direction = 1

        # Alien Lasers
        self.alien_lasers_group.empty()
        self.bombs_group.empty() # Also clear bombs on reset
        self.explosions_group.empty() # Also clear explosions on reset
        if self.super_alien_group.sprite: # Clear super alien on reset
             self.super_alien_group.sprite.kill()


        # Game State
        self.game_over = False

    def spawn_super_alien(self):
        current_time = pygame.time.get_ticks()
        if not self.super_alien_group.sprite and current_time >= self.super_alien_next_spawn_time:
            super_alien = SuperAlien(self.screen_width, self.screen_height)
            self.super_alien_group.add(super_alien)

            # Fire initial bomb burst
            if not super_alien.initial_bomb_burst_fired:
                num_bombs_in_burst = SUPER_ALIEN_INITIAL_BOMB_BURST_COUNT # Changed from 10 to 20
                bomb_speed = SUPER_ALIEN_BOMB_SPEED # Or int(5 * self.game_speed_modifier) if bombs should speed up
                spread_width = 40

                for i in range(num_bombs_in_burst):
                    offset_x = 0
                    if num_bombs_in_burst > 1:
                       offset_x = (i * (spread_width / (num_bombs_in_burst -1 ))) - (spread_width / 2)

                    bomb_x = super_alien.rect.centerx + int(offset_x)
                    bomb_y = super_alien.rect.bottom

                    new_bomb = Bomb((bomb_x, bomb_y), SUPER_ALIEN_BOMB_SPEED, self.screen_height)
                    self.bombs_group.add(new_bomb)

                super_alien.initial_bomb_burst_fired = True

            # Reset the timer for the next spawn
            self.super_alien_next_spawn_time = current_time + random.randint(self.super_alien_spawn_time_min, self.super_alien_spawn_time_max)

    def handle_bomb_dropping(self):
        if self.super_alien_group.sprite:
            super_alien = self.super_alien_group.sprite
            if super_alien.should_drop_bomb(): # Using the method from SuperAlien class
                bomb_x = super_alien.rect.centerx
                bomb_y = super_alien.rect.bottom
                # Bomb speed can be a fixed value or configurable
                new_bomb = Bomb((bomb_x, bomb_y), SUPER_ALIEN_BOMB_SPEED, self.screen_height)
                self.bombs_group.add(new_bomb)

    # Methods below this point are correctly placed and should not be part of handle_bomb_dropping
    # def check_victory(self): ... (already removed)
    # def load_high_score(self): ... (already removed)

    def check_round_clear(self):
        if not self.game_over: # Only check if game is ongoing
            if not self.aliens_group: # No more aliens
                # Optional: Add a small delay here before returning True,
                # or handle delay in main.py after this returns True.
                # For now, immediate signal.
                return True
        return False

    def handle_spaceship_respawn(self):
        if self.lives > 0 and not self.spaceship_group.sprite and self.spaceship_respawn_time > 0:
            current_time = pygame.time.get_ticks()
            if current_time >= self.spaceship_respawn_time:
                # Removed speed_modifier from Spaceship constructor
                spaceship = Spaceship(self.screen_width, self.screen_height, start_invincible=True)

                # Set invincibility on the new spaceship instance
                # This requires Spaceship class to handle these attributes.
                # For now, we're just setting the time on Game, Spaceship will need to use it.
                # The actual attribute setting on spaceship will be part of Spaceship.py modification.
                # spaceship.invincible = True # This will be done in Spaceship.__init__ or by a method
                # spaceship.invincible_until = current_time + self.invincibility_duration_ms

                self.spaceship_group.add(spaceship)
                self.spaceship_respawn_time = 0 # Reset respawn timer

                # Store time for when invincibility should end for the NEWLY created spaceship
                # This is a bit tricky. The spaceship itself should manage its invincibility state.
                # For now, let's assume Spaceship will have an activate_invincibility method or similar.
                # For this subtask, we'll just add the spaceship.
                # The plan step for Spaceship.py will handle making it invincible.
