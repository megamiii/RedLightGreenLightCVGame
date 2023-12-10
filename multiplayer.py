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

from centroidtracker import CentroidTracker
import datetime
import imutils

protopath = "MobileNetSSD_deploy.prototxt"
modelpath = "MobileNetSSD_deploy.caffemodel"
detector = cv2.dnn.readNetFromCaffe(prototxt=protopath, caffeModel=modelpath)


CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

tracker = CentroidTracker(maxDisappeared=80, maxDistance=90)


def non_max_suppression_fast(boxes, overlapThresh):
    try:
        if len(boxes) == 0:
            return []

        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")

        pick = []

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)

        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            overlap = (w * h) / area[idxs[:last]]

            idxs = np.delete(idxs, np.concatenate(([last],
                                                   np.where(overlap > overlapThresh)[0])))

        return boxes[pick].astype("int")
    except Exception as e:
        print("Exception occurred in non_max_suppression : {}".format(e))

def multiplayer_game(pygame, screen, size, sys, current_screen):

    # Test2: HOG detection
    #hog = cv2.HOGDescriptor()
    #hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
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


    # Initialize value for gameplay
    TIMER_MAX = 6  #Rounds of game (each light counted as 1 round)
    TIMER = TIMER_MAX
    maxMove = 5000000  #maxMove is the threshold for motion detection (boundary for movement allowed)
    win = False
    isgreen = True
    prev = time.time()
        
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

    # Intialiaze value for motion detection
    total_frames = 0
    lpc_count = 0
    opc_count = 0
    object_id_list = []

    # Wait for 5 seconds before starting the game
    time.sleep(5)
    pygame.mixer.music.stop()

    while cap.isOpened() and TIMER >=0:
        # Start gameplay 

        # Set up webcam capture
        ret, frame = cap.read()
        frame_hog = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        '''
        #Test 2: HOG detection
        # Detect humans in the frame
        boxes, weights = hog.detectMultiScale(frame_hog, winStride=(8, 8))


        # Draw bounding boxes around detected humans
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        '''
        
        # Setup for object detection bounding box
        frame = imutils.resize(frame, width=600)
        total_frames = total_frames + 1
        (H, W) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)

        detector.setInput(blob)
        person_detections = detector.forward()
        rects = []
        for i in np.arange(0, person_detections.shape[2]):
            confidence = person_detections[0, 0, i, 2]
            if confidence > 0.5:
                idx = int(person_detections[0, 0, i, 1])

                if CLASSES[idx] != "person":
                    continue

                person_box = person_detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = person_box.astype("int")
                rects.append(person_box)

        boundingboxes = np.array(rects)
        boundingboxes = boundingboxes.astype(int)
        rects = non_max_suppression_fast(boundingboxes, 0.3)

        objects = tracker.update(rects)
        for (objectId, bbox) in objects.items():
            x1, y1, x2, y2 = bbox
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            

            if objectId not in object_id_list:
                object_id_list.append(objectId)
        
        # Draw the webcam frame onto the screen and convert webcam frame to pygame format
        frame_py = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_py = np.rot90(frame_py)
        frame_py = pygame.surfarray.make_surface(frame_py)
        screen.blit(frame_py, (120,50))
        
        pygame.display.update()

        cur = time.time()

        # Check if 5 seconds have passed, red/green light chenges every 5 seconds
        if cur-prev >= 5:
            
            prev = cur
            TIMER = TIMER-1
           
            if isgreen:
                # Change to green light
                screen.blit(green_light_image, (0, 0))
                # Play Squid-Game-Robot-Sound.mp3
                pygame.mixer.music.load('assets/Squid-Game-Robot-Sound.mp3')
                pygame.mixer.music.play()
                
                isgreen = False

            else:
                # Change to red light
                screen.blit(red_light_image, (0, 0))
                ref = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                isgreen = True

            pygame.display.update()
            

        if isgreen: # when red light, check if player move
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #gray = cv2.GaussianBlur(gray, (21, 21), 0)
            frameDelta = cv2.absdiff(ref, gray)
            thresh = cv2.threshold(frameDelta, 20, 255, cv2.THRESH_BINARY)[1]
            change = np.sum(thresh)
            
            if change>maxMove:
                # Player moved during red light, game over
                # Stop playing Squid-Game-Robot-Sound.mp3, break gameplay loop
                pygame.mixer.music.stop()
                break


        else: # when green light, reach finish line and press space
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    win = True
                    
            if win:
                # Player reached finish line by pressing space, win
                # Stop playing Squid-Game-Robot-Sound.mp3, break gameplay loop
                pygame.mixer.music.stop()
                break

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q: #press q to quit game
                cap.release()
                pygame.quit()
                sys.exit()
        
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

        current_screen = "start"


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

        current_screen = "start"



   
        




