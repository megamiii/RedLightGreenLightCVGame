import pygame
import sys
import cv2
import numpy as np
import time
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
red_light_start = True

# Helper function to check player visbility
def isVisible(landmarks, width, height):
    """
    Checks if key landmarks are within the frame.
    This function is used to ensure the player is visible in the camera feed.
    """
    if not landmarks:
        return False

    visible_landmarks = [
        mp_pose.PoseLandmark.NOSE,
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP,
    ]

    for landmark in visible_landmarks:
        x = landmarks.landmark[landmark].x * width
        y = landmarks.landmark[landmark].y * height
        if not (0 <= x < width and 0 <= y < height):
            return False

    return True


def win_game(screen, size, cap):
    pygame.mixer.music.load('assets/victory.mp3')
    pygame.mixer.music.play()
    image_path = 'assets/win.png'
    sequence_image = pygame.image.load(image_path).convert()
    sequence_image = pygame.transform.scale(sequence_image, size)
    screen.blit(sequence_image, (0, 0))
    pygame.display.flip()

    # Wait for 'q' key press to quit the game
    quit_game = False
    while not quit_game:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                quit_game = True
    pygame.mixer.music.stop()

    if quit_game:    

        cap.release()
        pygame.quit()
        sys.exit()
    
    else:
        current_screen = "start"


def lose_game(screen, size, cap):
    pygame.mixer.music.load('assets/game_over.mp3')
    pygame.mixer.music.play()
    for image_number in range(10, 16):
        image_path = f'assets/image_resource/Slide{image_number}.png'
        sequence_image = pygame.image.load(image_path).convert()
        sequence_image = pygame.transform.scale(sequence_image, size)
        screen.blit(sequence_image, (0, 0))
        pygame.display.flip()
        time.sleep(0.3)  # Short delay between images

    # Wait for 'q' key press to quit the game
    quit_game = False
    while not quit_game:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key is pygame.K_q:
                quit_game = True
    pygame.mixer.music.stop()

    if quit_game:    

        cap.release()
        pygame.quit()
        sys.exit()
    
    else:
        current_screen = "start"


def calculate_pose_change(baseline_landmarks, current_landmarks):
    """
    Calculate the change in pose by measuring differences in key landmarks.
    Returns True if the change is above a certain threshold.
    """
    threshold_movement = 0.1  # adjustable
    significant_movement = False

    if baseline_landmarks and current_landmarks:
        for landmark in mp_pose.PoseLandmark:
            baseline = baseline_landmarks.landmark[landmark]
            current = current_landmarks.landmark[landmark]
            distance = np.sqrt((baseline.x - current.x) ** 2 + (baseline.y - current.y) ** 2)
            # print(distance)
            
            if distance > threshold_movement:
                significant_movement = True
                break

    return significant_movement


def single_player_game(screen, size):
    """
    Main function for the single-player game mode.
    This function manages the game state, including the initial visibility check,
    and toggling between green and red lights based on the timer.
    """
    # Initial setup: setting up the game clock, loading images and sounds
    clock = pygame.time.Clock()
    toggle_interval = 3  # seconds for light toggle
    last_toggle = time.time() # timer to manage light toggle
    
    # Load game images (rules, loading, green light, red  light)
    game_rule_image = pygame.image.load('assets/game_rules_single.png').convert()
    loading_image = pygame.image.load('assets/loading_image.png').convert()
    green_light_image = pygame.image.load('assets/green_light.png').convert()
    red_light_image = pygame.image.load('assets/red_light.png').convert()

    # Load game sounds (background, green light, red light)
    background_sound = pygame.mixer.Sound('assets/background_sound.mp3')
    green_light_sound = pygame.mixer.Sound('assets/green_light_sound.mp3')
    red_light_sound = pygame.mixer.Sound('assets/red_light_sound.mp3')
    
    # Display game rules (slightly different from the multiplayer mode 
    # as you don't need to press the space bar when you reach the finish line)
    game_rule_image = pygame.transform.scale(game_rule_image, size)
    screen.blit(game_rule_image, (0, 0))
    pygame.display.update()
    
    pygame.mixer.music.load('assets/background_sound.mp3')
    pygame.mixer.music.play()
        
    # Game start logic: waiting for 's' key to start the game
    start_game = False
    game_started = False  # flag to track if game logic has started
    visibility_check_started = False
    visibility_timeout = 25  # seconds allowed for player to be visible
    visibility_check_start_time = None # timer start for visibility check
    
    while not start_game:
        # Event loop to wait for 's' key press to start the game
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                start_game = True
                if not visibility_check_started:
                    visibility_check_started = True
                    visibility_check_start_time = time.time()
                
    loading_image = pygame.transform.scale(loading_image, size)
    screen.blit(loading_image, (0, 0))
    pygame.display.flip()
    
    green_light_image = pygame.transform.scale(green_light_image, size)
    red_light_image = pygame.transform.scale(red_light_image, size)
    
    # Font for displaying text
    font = pygame.font.Font(None, 36)  # Use a system font, or replace with a path to a custom font
    text_color = (255, 0, 0)  # Red color for the text

    # Define the camera view position on the screen
    cam_view_x, cam_view_y = 120, 50  # Top-left corner of the camera view
    cam_width = 760
    cam_height = 200
    
    # Setup for the webcam to capture player's movement
    cap = cv2.VideoCapture(0) 
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

    win = False
    is_green = True
    
    time.sleep(5)
    pygame.mixer.music.stop()

    # Game loop
    i = 1
    j = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Process each frame for pose detection using MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        frame_in_frame = isVisible(results.pose_landmarks, cam_width, cam_height)
        current_time = time.time()

        # baseline_landmarks = None
        player_moved = False

        # Check for player visibility within a timeout period
        if visibility_check_started and not game_started:
            if frame_in_frame:
                game_started = True  # Player is visible, start game logic
                last_toggle = current_time  # Initialize toggle timer
            elif current_time - visibility_check_start_time > visibility_timeout:
                break  # End game if player is not visible within timeout

        # If the game has started, manage the toggling of traffic lights
        if game_started:
            # Toggle lights logic
            if current_time - last_toggle > toggle_interval:
                is_green = not is_green
                last_toggle = current_time
                play_sound(is_green, green_light_sound, red_light_sound)

                if not is_green:
                    print(str(i) + "th red light")
                    i+=1
                    red_light_start = True
                    baseline_landmarks = results.pose_landmarks
                    # print("REAL BASELINE_LANDMARKS\n")
                    # print(baseline_landmarks)

            if not is_green and red_light_start:
                red_light_start = False  # Reset the flag after setting baseline

            # Check for movement during red light
            if not is_green and not red_light_start:
                curr_landmarks = results.pose_landmarks
                # print("TEST BASELINE_LANDMARKS\n")
                # print(baseline_landmarks)
                # print("COMPARE CURR_LANDMARKS\n")
                # print(curr_landmarks)
                player_moved = calculate_pose_change(baseline_landmarks, curr_landmarks)

            if player_moved:
                lose_game(screen, size, cap)

            if is_green:
                baseline_landmarks = None
                player_moved = False
                red_light_start = True

            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    win = True
                    print("win in location 1")
                    
            if win:
                break

            for event in pygame.event.get():
                '''
                if not isgreen and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    win = True
                    print("win in location 2")
                '''    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    cap.release()
                    pygame.quit()
                    sys.exit()

        # Draw pose landmarks on the frame for player's visualization
        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec = mp.solutions.drawing_styles.get_default_pose_landmarks_style())
        
        # Process the camera frame and display it
        frame_py = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_py = np.rot90(frame_py)
        frame_py = pygame.surfarray.make_surface(frame_py)
        
        if not frame_in_frame:
            # Render the text and center it in the camera view
            text_surface = font.render("You are not in the frame", True, text_color)
            # Calculate relative position inside the camera feed
            text_x = 440 - cam_view_x
            text_y = 220 - cam_view_y
            text_rect = text_surface.get_rect(center=(text_x, text_y))
            
            frame_py.blit(text_surface, text_rect)  # Draw the text on the camera frame

        # Clear the screen
        screen.fill((0, 0, 0))

        # Blit images depending on game state
        if is_green:
            screen.blit(green_light_image, (0, 0))  # Maybe resize or reposition
        else:
            screen.blit(red_light_image, (0, 0))  # Maybe resize or reposition
        
        # Blit the camera feed above the images
        screen.blit(frame_py, (120, 50))

        pygame.display.flip()

        # Event loop to check for game exit condition
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                cap.release()
                pygame.quit()
                sys.exit()

    if win:
        win_game(screen, size, cap)
    else:
        lose_game(screen, size, cap)

                
# Helper function to play sounds based on the current light state
def play_sound(is_green, green_light_sound, red_light_sound):
    """
    Plays sound based on the current state of the traffic light in the game.
    Green light and red light have different sounds associated with them.
    """
    if is_green:
        green_light_sound.play()
    else:
        red_light_sound.play()