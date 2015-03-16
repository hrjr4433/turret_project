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

def find_object(bin_img, sides=4):
    int_img = labeling.labeling(bin_img)
    num_obj = np.max(int_img)
    points = np.array([[0]])
    found = np.zeros(bin_img.shape, dtype=np.bool)
    biggest_pix = 0
    for i in range(1,num_obj+1):
        mask = (int_img == i)
        points = shape.find_points(mask)
        if shape.count_sides(points) == sides:
            mask_sum = mask.sum()
            if  mask_sum > biggest_pix:
                biggest_pix = mask_sum
                found = mask
    return (found,points)

# this is where one sets how long the script
# sleeps for, between frames.sleeptime__in_seconds = 0.05
# initialise the display window
screen_size = (640,480)
rows, cols = screen_size
screen = pygame.display.set_mode(screen_size)
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
    
    #color
    mask = color.find_color(data)
    #morphology
    mask = morphology.closing(mask)
    mask,points = find_object(mask,4)
    # print points
    result[mask] = [255,255,255]
    center = aim.find_center(screen_size,points,4)
    print center
    y,x = aim.get_degrees(rows, cols, center)
    print y,x
    pulse_per_degree = (530-270)/float(90)
    print (int(y*pulse_per_degree), int(x*pulse_per_degree))
    # print center
    # result[center[0],center[1]] = [17, 15, 100]
    
    # copy the camera image to the screen
    surfarray.blit_array(screen, result)
    
    # update the screen to show the latest screen image
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
