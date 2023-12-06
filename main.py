import pygame
import sys
import single_player
import multiplayer
import time

# Initialize Pygame and mixer
pygame.mixer.pre_init(44100, -16, 2, 32)
pygame.init()
pygame.mixer.quit()
pygame.mixer.init(22050, -16, 2, 32)

# Load background music
pygame.mixer.music.load('assets/background_sound.mp3')  # Replace with your music file path
click_sound = pygame.mixer.Sound('assets/button_click_sound.wav')  # Load click sound effect

# Play background music
pygame.mixer.music.play(-1)  # -1 for looping indefinitely

# Set the size of the window to the current display size
infoObject = pygame.display.Info()
size = (infoObject.current_w, infoObject.current_h)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

# Set the title of the window
pygame.display.set_caption("Game Modes")

# Load the start screen image and scale it to fit the screen
original_image_size = (1792, 1024)  # The original size of the background image
start_background_image = pygame.image.load('assets/start_screen.png').convert()
start_background_image = pygame.transform.scale(start_background_image, size)

# Load the options screen image and scale it to fit the screen
options_background_image = pygame.image.load('assets/options_window.png').convert()
options_background_image = pygame.transform.scale(options_background_image, size)

# Calculate scale factors
scale_x = size[0] / original_image_size[0]
scale_y = size[1] / original_image_size[1]

# Scale button positions and dimensions
def scale_button(button_x, button_y, button_width, button_height):
    return (button_x * scale_x, button_y * scale_y, button_width * scale_x, button_height * scale_y)

# Define button positions and dimensions for the options screen (scaled)
sp_button_x, sp_button_y, sp_button_width, sp_button_height = scale_button(412, 754, 262, 102)
mp_button_x, mp_button_y, mp_button_width, mp_button_height = scale_button(1111, 754, 270, 114)

# Define button positions and dimensions for the start screen (scaled)
options_button_x, options_button_y, options_button_width, options_button_height = scale_button(482, 47, 132, 128)
exit_button_x, exit_button_y, exit_button_width, exit_button_height = scale_button(664, 49, 136, 139)
start_button_x, start_button_y, start_button_width, start_button_height = scale_button(1166, 48, 135, 138)

# Current screen state and game mode
current_screen = "start"
game_mode = None  # Default game mode

# Define a function to check button clicks
def button_clicked(button_x, button_y, button_width, button_height, mouse_pos):
    mouse_x, mouse_y = mouse_pos
    return (button_x <= mouse_x <= button_x + button_width) and (button_y <= mouse_y <= button_y + button_height)

# Placeholder functions for game modes
def start_game():
    # Stop the music when the game starts
    pygame.mixer.music.stop()
    
    if game_mode == "single":
        print("Starting game in single player mode...")
        # Initialize single player game
        single_player.single_player_game(screen, size)
        
    elif game_mode == "multi":
        print("Starting game in multiplayer mode...")
        # Initialize multiplayer game
        multiplayer.multiplayer_game(pygame, screen, size, sys)
        
    else:
        print("No game mode selected")
        # Restart the background music if no game mode is selected
        pygame.mixer.music.play(-1)
        no_game_mode = pygame.image.load('assets/no_game_mode.png').convert()
        no_game_mode = pygame.transform.scale(no_game_mode, size)
        screen.blit(no_game_mode, (0, 0))  # Display the no game mode image
        pygame.display.flip()  # Update the display to show the image
        time.sleep(2)
        current_screen = "start"

        
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Play the click sound effect whenever a click event is detected
            click_sound.play()
            if current_screen == "start":
                # Start screen button actions
                if button_clicked(options_button_x, options_button_y, options_button_width, options_button_height, event.pos):
                    current_screen = "options"
                elif button_clicked(exit_button_x, exit_button_y, exit_button_width, exit_button_height, event.pos):
                    running = False  # Exit the game
                elif button_clicked(start_button_x, start_button_y, start_button_width, start_button_height, event.pos):
                    start_game()
            elif current_screen == "options":
                # Options screen button actions
                if button_clicked(sp_button_x, sp_button_y, sp_button_width, sp_button_height, event.pos):
                    game_mode = "single"
                    current_screen = "start"  # Go back to start screen
                elif button_clicked(mp_button_x, mp_button_y, mp_button_width, mp_button_height, event.pos):
                    game_mode = "multi"
                    current_screen = "start"  # Go back to start screen
                else:
                    game_mode = None
                    current_screen = "start"  # Go back to start screen

    # Draw the appropriate background
    if current_screen == "start":
        screen.blit(start_background_image, (0, 0))
    elif current_screen == "options":
        screen.blit(options_background_image, (0, 0))

    # Update the display
    pygame.display.flip()

# Stop the music when exiting the game loop
pygame.mixer.music.stop()

# Quit Pygame
pygame.quit()
sys.exit()