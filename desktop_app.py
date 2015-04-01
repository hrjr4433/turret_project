#!/usr/bin/env python
# import the relevant libraries
import sys
import time
import numpy as np
import pygame
import pygame.camera
import pygame.surfarray as surfarray
from pygame.locals import *
from parakeet import jit

import aim
import labeling
import color
# import hardware
import morphology
import shape
import threshold


display = True
display_option = 1
center_display = False
degree_display = False
o_thr = False
o_color = 'r'
o_sides = 5
prev_threshold = None

def find_object(bin_img, sides=4):
    int_img = labeling.labeling(bin_img)
    num_obj = np.max(int_img)
    found_points = np.array([[0]])
    found = np.zeros(bin_img.shape, dtype=np.bool)
    biggest_pix = 100
    for i in range(1,num_obj+1):
        mask = (int_img == i)
        points = shape.find_points(mask)
        if shape.count_sides(points) == sides:
            mask_sum = mask.sum()
            if  mask_sum > biggest_pix:
                biggest_pix = mask_sum
                found = mask
                found_points = points
    return (found,found_points)

def find_any_object(bin_img):
    global prev_threshold
    if prev_threshold is None:
        prev_threshold = bin_img
    else:
        diff = np.subtract(bin_img,prev_threshold)  
        prev_threshold = bin_img
        bin_img = (diff != 0)
    int_img = labeling.labeling(bin_img)
    num_obj = np.max(int_img)
    found = np.zeros(bin_img.shape, dtype=np.bool)
    biggest_pix = 0
    sides = 3
    t_sides = 0
    for i in range(1,num_obj+1):
        mask = (int_img == i)
        mask_sum = mask.sum()
        points = shape.find_points(mask)
        t_sides = shape.count_sides(points)
        if mask_sum > 100 and mask_sum > biggest_pix and t_sides > sides:
            biggest_pix = mask_sum
            found = mask
            found_points = points
            found_sides = t_sides
    return (found,found_points,found_sides)

# this is where one sets how long the script
# sleeps for, between frames.sleeptime__in_seconds = 0.05
# initialise the display window
option = int(raw_input("Choose image raw(1), color/threshold(2), shape/result(3), or no display? "))
if option >= 1 and option <= 3:
    display_option = option
elif option == 4:
    display = False
option = raw_input("choose what do you wish to find any moving object? ")
if option == 'y' or option == 'Y' or option == 'yes' or option == 'Yes':
    o_thr = True
else:
    option = raw_input("choose color of your target(r,b,y,g): ")
    if option == 'r' or option == 'b' or option == 'y' or option == 'g':
        o_color = option
    option = int(raw_input("choose the number of sides of your target(3-8): "))
    if option >= 3 and option <= 8:
        o_sides = option
option = raw_input("would you like to see the center of mass? ")
if option == 'y' or option == 'Y' or option == 'yes' or option == 'Yes':
    center_display = True
option = raw_input("would you like to see the coordinance? ")
if option == 'y' or option == 'Y' or option == 'yes' or option == 'Yes':
    degree_display = True

screen_size = (320,240)
rows, cols = screen_size
screen = pygame.display.set_mode(screen_size)
prev_threshold = None
pygame.init()
pygame.camera.init()
# set up a camera object
cam = pygame.camera.Camera("/dev/video0",screen_size)
cam.set_controls(hflip=False)
# start the camera
cam.start()

while 1:

    # sleep between every frame
    time.sleep( 0.04 )
    # fetch the camera image
    image = cam.get_image()
    data = surfarray.array3d(image)
    result = np.zeros(data.shape[:3],dtype=np.uint8)
    
    global done, o_sides, o_color, o_thr, frame_count
    if o_thr:
        # thresholding
        thr_m = threshold.thresholding(data)
        # morphology
        mask = morphology.opening(thr_m)
        # find object
        mask,points,o_sides = find_any_moving_object(mask)
    else:
        # color
        color_m = color.find_color(data,o_color)
        # morphology
        color_m = morphology.closing(color_m)
        # find object
        mask,points = find_object(color_m,o_sides)
        print points
    #print points
    # center = aim.find_center(screen_size,points,o_sides)
    # if center_display:
    #     print center
    # degrees = aim.get_degrees(screen_size,center)
    # if degree_display:
    #     print degrees
    # result[center[0],center[1]] = [17, 15, 100]

    # update the screen to show the latest screen image
    if display:
        if display_option == 1:
            result = data
        elif display_option == 2:
            if o_thr:
                mask = thr_m
            else:
                mask = color_m
        if display_option > 1:
            result[mask] = [255,255,255]
    
    # copy the camera image to the screen
    surfarray.blit_array(screen, result)
    
    # update the screen to show the latest screen image
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
