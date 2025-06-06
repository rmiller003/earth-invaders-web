# Based on one of the most popular video games of all time,
# This is a new Earth Invaders Pygame developed in Python v3.10 [5/12/24]
# Enjoy!

import pygame
import sys
import random # Ensure random is imported at the top of main.py
from game import Game


pygame.init()

# Attempt to initialize the mixer, but don't crash if it fails
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Warning: Could not initialize mixer. Error: {e}. Game will continue without sound.")
    # Optionally, disable sound-related functionality further if needed

# Background music
try:
    pygame.mixer.music.load("Sounds/dark_music.ogg")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Warning: Could not load background music 'Sounds/dark_music.ogg'. Error: {e}. Game will continue without music.")

font = pygame.font.Font("Font/monogram.ttf", 40)

# Title Configuration
TITLE_TEXT = "Robert Miller Presents Earth Invaders Revenge"
TITLE_COLOR = (255, 0, 0)  # Red

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 700

NUM_STARS = 150  # Increased for better density
STAR_COLORS = [
    (255, 255, 255),  # White
    (200, 200, 255),  # Light Blue
    (255, 255, 200)   # Light Yellow
]
   
GREY = (29,29,27)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPM Presents Earth Invaders X")

# Create title surface for main menu (original title)
# Repositioning will be handled in the drawing section for the menu
title_surface = font.render(TITLE_TEXT, True, TITLE_COLOR)

# Prompt for Main Menu
PROMPT_TEXT = "Press ENTER to Start"
PROMPT_COLOR = (255, 255, 255)  # White
prompt_surface = font.render(PROMPT_TEXT, True, PROMPT_COLOR)

clock = pygame.time.Clock()

def initialize_stars(width, height, num_stars):
    star_list = []
    for _ in range(num_stars):
        star_x = random.randint(0, width)
        star_y = random.randint(0, height)
        star_size = random.randint(1, 2) # Stars of 1x1 or 2x2 pixels
        star_color = random.choice(STAR_COLORS)
        # Add a scroll speed for each star, even if uniform for now for the scrolling part
        star_scroll_speed = random.uniform(0.5, 1.5) # Slower stars for parallax later, or just 1
        star_list.append({'x': star_x, 'y': star_y, 'size': star_size, 'color': star_color, 'speed': star_scroll_speed})
    return star_list

game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)

# Game States
MAIN_MENU = "main_menu"
PLAYING = "playing"
PAUSED = "paused"
current_state = MAIN_MENU

stars = initialize_stars(SCREEN_WIDTH, SCREEN_HEIGHT, NUM_STARS) # Add this line

while True:
    #Checking for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle pause toggle if P is pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if current_state == PLAYING:
                    current_state = PAUSED
                elif current_state == PAUSED:
                    current_state = PLAYING

            # Other keydown events based on state
            if current_state == MAIN_MENU:
                if event.key == pygame.K_RETURN:
                    current_state = PLAYING
                    game.reset_game(new_round_started=False)
            elif current_state == PLAYING: # This condition is for when the game is active (not paused, not main menu)
                if game.game_over:
                    if event.key == pygame.K_n:
                        current_state = MAIN_MENU
                # Potentially other PLAYING key events for spaceship controls if they are handled here
                # (Spaceship controls are in spaceship.py's get_user_input, which is fine)
            # Note: No specific keydown events for PAUSED state other than K_p to unpause (handled above)

    #Updating
    # Only update game logic if in PLAYING state and not game over
    if current_state == PLAYING and not game.game_over:

        # Update star positions for scrolling effect
        for star in stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT: # Star has moved off the bottom
                star['y'] = 0 # Reset to top
                star['x'] = random.randint(0, SCREEN_WIDTH) # New random x position
                # Optional: Re-randomize size, color, and speed for variety
                star['size'] = random.randint(1, 2)
                star['color'] = random.choice(STAR_COLORS)
                star['speed'] = random.uniform(0.5, 1.5)

        game.handle_spaceship_respawn() # Add this call
        game._check_and_activate_frenzy_mode() # Add this call
        game.spaceship_group.update()
        game.move_aliens()
        game.alien_shoot()
        game.alien_lasers_group.update() # Update lasers before checking round clear

        if game.check_round_clear(): # New call
            game.reset_game(new_round_started=True)
        else:
            # Only run these other updates if a round isn't immediately cleared and reset
            game.spawn_super_alien()
            game.handle_bomb_dropping()
            game.super_alien_group.update()
            game.bombs_group.update()
            game.explosions_group.update()
            game.check_collisions()
            game.check_hostile_projectile_collisions()
    
    
    #Drawing
    screen.fill((0, 0, 0)) # Fill screen with black

    # Draw stars
    for star in stars:
        pygame.draw.rect(screen, star['color'], (star['x'], star['y'], star['size'], star['size']))

    if current_state == MAIN_MENU:
        # Draw Main Menu
        # Title position for main menu
        mm_title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
        screen.blit(title_surface, mm_title_rect)

        # Prompt position for main menu
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(prompt_surface, prompt_rect)

    elif current_state == PLAYING:
        if not game.game_over:
            # Draw active game elements
            if game.spaceship_group.sprite: # Ensure spaceship exists before drawing its lasers
                game.spaceship_group.sprite.lasers_group.draw(screen)

            # Handle spaceship blinking for invincibility
            if game.spaceship_group.sprite: # Check if spaceship exists
                if getattr(game.spaceship_group.sprite, 'blink_on', True): # Default to True if no attribute
                    game.spaceship_group.draw(screen)
                # If blink_on is False, it's simply not drawn for that frame.

            # Add shield drawing logic AFTER spaceship is drawn
            if game.spaceship_group.sprite and getattr(game.spaceship_group.sprite, 'shield_active', False):
                shield_aura_surface = getattr(game.spaceship_group.sprite, 'shield_aura_surface', None)
                if shield_aura_surface:
                    aura_rect = shield_aura_surface.get_rect(center=game.spaceship_group.sprite.rect.center)
                    screen.blit(shield_aura_surface, aura_rect)

            for obstacle in game.obstacles:
                obstacle.blocks_group.draw(screen)
            game.aliens_group.draw(screen)
            game.alien_lasers_group.draw(screen)
            game.super_alien_group.draw(screen)
            game.bombs_group.draw(screen)
            game.explosions_group.draw(screen)

            # Display current score during active gameplay
            score_surface = font.render(f"Score: {game.score}", True, (255, 255, 255))
            score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 20, 10))
            screen.blit(score_surface, score_rect)

            # New Lives display
            lives_text = f"Lives: {game.lives}"
            lives_surface = font.render(lives_text, True, (255, 255, 255)) # White color
            lives_rect = lives_surface.get_rect(topleft=(20, 10))
            screen.blit(lives_surface, lives_rect)

            # Display current level
            level_text = f"Level: {game.current_level_number}"
            # Using the global 'font' and white color (255,255,255)
            level_surface = font.render(level_text, True, (255, 255, 255))
            # Position it, e.g., top-center
            level_rect = level_surface.get_rect(midtop=(SCREEN_WIDTH / 2, 10))
            screen.blit(level_surface, level_rect)
        else: # This means current_state == PLAYING and game.game_over is True
            # Game Over Screen
            game_over_surface = font.render("GAME OVER", True, (255, 0, 0)) # Red
            game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60))
            screen.blit(game_over_surface, game_over_rect)

            final_score_surface = font.render(f"Score: {game.score}", True, (255, 255, 255))
            final_score_rect = final_score_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(final_score_surface, final_score_rect)

            # The prompt text might need updating based on previous subtask (N to go to Menu)
            # But sticking to "Press N for New Game" as per current subtask's verification items.
            restart_text_surface = font.render("Press N for New Game", True, (255, 255, 255)) # White
            restart_text_rect = restart_text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60))
            screen.blit(restart_text_surface, restart_text_rect)

    elif current_state == PAUSED:
        # 1. Draw the 'frozen' game scene (similar to PLAYING and not game.game_over)
        if game.spaceship_group.sprite: # Ensure spaceship exists before drawing its lasers
            game.spaceship_group.sprite.lasers_group.draw(screen)

        # Handle spaceship blinking for invincibility
        if game.spaceship_group.sprite: # Check if spaceship exists
            if getattr(game.spaceship_group.sprite, 'blink_on', True): # Default to True if no attribute
                game.spaceship_group.draw(screen)
            # If blink_on is False, it's simply not drawn for that frame.

            # Add shield drawing logic AFTER spaceship is drawn in PAUSED state
            if game.spaceship_group.sprite and getattr(game.spaceship_group.sprite, 'shield_active', False):
                shield_aura_surface = getattr(game.spaceship_group.sprite, 'shield_aura_surface', None)
                if shield_aura_surface:
                    aura_rect = shield_aura_surface.get_rect(center=game.spaceship_group.sprite.rect.center)
                    screen.blit(shield_aura_surface, aura_rect)

        for obstacle in game.obstacles:
            obstacle.blocks_group.draw(screen)
        game.aliens_group.draw(screen)
        game.alien_lasers_group.draw(screen)
        game.super_alien_group.draw(screen)
        game.bombs_group.draw(screen)
        game.explosions_group.draw(screen)

        # Display current score
        score_surface = font.render(f"Score: {game.score}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 20, 10))
        screen.blit(score_surface, score_rect)

        # Display current lives
        lives_text = f"Lives: {game.lives}"
        lives_surface = font.render(lives_text, True, (255, 255, 255))
        lives_rect = lives_surface.get_rect(topleft=(20, 10))
        screen.blit(lives_surface, lives_rect)

        # Display current level
        level_text = f"Level: {game.current_level_number}"
        level_surface = font.render(level_text, True, (255, 255, 255))
        level_rect = level_surface.get_rect(midtop=(SCREEN_WIDTH / 2, 10))
        screen.blit(level_surface, level_rect)

        # 2. Render and blit the "PAUSED" message
        paused_text = "PAUSED"
        paused_color = (255, 255, 255) # White
        paused_surface = font.render(paused_text, True, paused_color)
        paused_rect = paused_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(paused_surface, paused_rect)

        # Optional: Add a sub-text like "Press P to Resume"
        resume_text = "Press P to Resume"
        resume_color = (200, 200, 200) # Light grey
        resume_surface = font.render(resume_text, True, resume_color) # Use the same font or a smaller one
        resume_rect = resume_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)) # Position below "PAUSED"
        screen.blit(resume_surface, resume_rect)

    pygame.display.update()
    clock.tick(60)
