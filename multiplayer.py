import pygame
import sys
import time
import cv2
import os
import numpy as np
from pygame.locals import *

import logging as log
import datetime as dt
from time import sleep

def multiplayer_game(pygame, screen, size, sys):

    #cascPath = "haarcascade_frontalface_default.xml"
    #faceCascade = cv2.CascadeClassifier(cascPath)

    # Load pre-trained human detection model (e.g., HOGDescriptor)
    #hog = cv2.HOGDescriptor()
    #hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    #net = cv2.dnn.readNetFromTensorflow('opencv_face_detector.prototxt', 'opencv_face_detector.pbtxt')
    #anterior = 0
    
    
    # Display game rule
    game_rule_image = pygame.image.load('assets/game_rules.png').convert()
    game_rule_image = pygame.transform.scale(game_rule_image, size)
    screen.blit(game_rule_image, (0, 0))
    pygame.display.update()
    
    pygame.mixer.music.load('assets/background_sound.mp3')
    pygame.mixer.music.play()
        
    # Wait for 's' key press to start the game
    start_game = False
    while not start_game:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                start_game = True
                
    
    loading_image = pygame.image.load('assets/loading_image.png').convert()
    loading_image = pygame.transform.scale(loading_image, size)
    screen.blit(loading_image, (0, 0))
    pygame.display.flip()

    green_light_image = pygame.image.load('assets/green_light.png').convert()
    green_light_image = pygame.transform.scale(green_light_image, size)
    red_light_image = pygame.image.load('assets/red_light.png').convert()
    red_light_image = pygame.transform.scale(red_light_image, size)
    
    TIMER_MAX = 4
    TIMER = TIMER_MAX
    maxMove = 6500000
        
    # Webcam capture size, adjust to your preferred size for the top right corner
    cam_width = 760
    cam_height = 200
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

    # Calculate the position for the top left corner
    screen_width, screen_height = size
    cam_pos = (0, 0)  # Top left corner
    frameHeight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frameWidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    win = False

    prev = time.time()
    prevDoll = prev
    isgreen = True

    time.sleep(5)
    pygame.mixer.music.stop()

    while cap.isOpened() and TIMER >=0:
        '''
        for event in pygame.event.get():
            if not isgreen and event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                win = True
                print("win in location 3")
        if win:
            break        
        '''
        
        ret, frame = cap.read()
        frame_hog = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        '''
        faces = faceCascade.detectMultiScale(
            frame_hog,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
         # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        '''

        '''
        #hog
        # Detect humans in the frame
        boxes, weights = hog.detectMultiScale(frame_hog, winStride=(8, 8))


        # Draw bounding boxes around detected humans
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        '''
        '''
        # Prepare input image for DNN face detection
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
        net.setInput(blob)

        # Perform face detection using DNN
        faces = net.forward()

        # Loop over the detected faces
        for i in range(faces.shape[2]):
            confidence = faces[0, 0, i, 2]
            if confidence > 0.5:  # Adjust the confidence threshold as needed
                # Get the coordinates of the bounding box
                box = faces[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                (x, y, x1, y1) = box.astype("int")

                # Draw a rectangle around the face
                cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)

        if anterior != faces.shape[2]:
            anterior = faces.shape[2]
            log.info("faces: " + str(faces.shape[2]) + " at " + str(dt.datetime.now()))
        '''
        frame_py = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_py = np.rot90(frame_py)
        frame_py = pygame.surfarray.make_surface(frame_py)
        screen.blit(frame_py, (120,50))
        
        pygame.display.update()

        cur = time.time()

        if cur-prev >= 5:
            
            #screen.blit(frame, (0,0))

            prev = cur
            TIMER = TIMER-1
            print(TIMER)
            '''
            for event in pygame.event.get():
                if not isgreen and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    win = True
                    print("win in location 4")
                    break
            if win:
                break
            '''
            if isgreen:
                
                screen.blit(green_light_image, (0, 0))
                print("green")
                
                # Play Squid-Game-Robot-Sound.mp3
                pygame.mixer.music.load('assets/Squid-Game-Robot-Sound.mp3')
                pygame.mixer.music.play()

                isgreen = False

            else:
                
                screen.blit(red_light_image, (0, 0))
                ref = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Stop playing Squid-Game-Robot-Sound.mp3
                pygame.mixer.music.stop()

                isgreen = True

            pygame.display.update()
            

        if isgreen: # when red light, check if player move
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #gray = cv2.GaussianBlur(gray, (21, 21), 0)
            frameDelta = cv2.absdiff(ref, gray)
            thresh = cv2.threshold(frameDelta, 20, 255, cv2.THRESH_BINARY)[1]
            change = np.sum(thresh)
            #print(change)
            if change>maxMove:
                break

        else:
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

        #if win:
            #break

        
    if win: # in winning case
        pygame.mixer.music.load('assets/victory.mp3')
        pygame.mixer.music.play()
        image_path = f'assets/win.png'
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

    else:
        pygame.mixer.music.load('assets/game_over.mp3')
        pygame.mixer.music.play()
        for image_number in range(10, 16):
            image_path = f'assets/image_resource/Slide{image_number}.png'
            sequence_image = pygame.image.load(image_path).convert()
            sequence_image = pygame.transform.scale(sequence_image, size)
            screen.blit(sequence_image, (0, 0))
            pygame.display.flip()
            
            # Wait for a short duration between images (e.g., 2 seconds)
            time.sleep(0.3)
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

        




