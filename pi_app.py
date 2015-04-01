import io
import os
import sys
import time
import numpy as np
import pygame
from pygame import surfarray
from pygame.locals import *
import picamera
import picamera.array
import threading
from parakeet import jit

import aim
import labeling
import color
import hardware
import morphology
import shape
import threshold

done = False
lock = threading.Lock()
pool = []
display = True
display_option = 1
center_display = False
degree_display = False
o_thr = False
o_color = 'r'
o_sides = 5
prev_threshold = None
surfarray.use_arraytype('numpy')
size = (180,180)
camera = picamera.PiCamera()
target_found = False
frame_count = 0
hardware.ready()

print "                                         ###"
print "                                     ## ##### ##"
print "                                    ## ### ### ##"
print "                                   ###  ## ##  ###"
print "                                    ##   ###   ##"
print "                                #    ##   #   ##"
print "                               #        ## ##"
print "                             #     #   ##   ##"
print "                           #     #"
print "            ##           #     #"
print "        ###  ##       #      #"
print "       #####  ##   #      #"
print "        ###  ## #       #"
print "            ##        #"
print "       ######      #"
print "      ## ####   #"
print "     ##  #### # "
print "      ##  ####"
print "          ## ##"
print "         ##   ##"
print "        ##   ##"
print "       ##   ##"

print "Hello! This is your friendly automated sentry gun, 'Destroyer'!"
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
print ""
print "Now the turret will get ready for the task. It might take a bit."

if display:
    pygame.init()
    screen = pygame.display.set_mode(size)
    
class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = picamera.array.PiRGBArray(camera)
        self.event = threading.Event()
        self.terminated = False
        self.setDaemon(True)
        self.start()

    def run(self):
        global done, o_sides, o_color, o_thr, frame_count
        while not self.terminated:
            if self.event.wait(1) and not done:
                try:
                    self.stream.seek(0)
                    if display:
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                pygame.quit()
                                done = True
                    
                    image = self.stream.array
                    result = np.zeros((size[1],size[0],3),np.uint8)

                    if o_thr:
                        # thresholding
                        thr_m = threshold.thresholding(image)
                        # morphology
                        mask = morphology.opening(thr_m)
                        # find object
                        mask,points,o_sides = find_any_moving_object(mask)
                    else:
                        # color
                        color_m = color.find_color(image,o_color)
                        # morphology
                        mask = morphology.closing(color_m)
                        # find object
                        mask,points = find_object(mask,o_sides)
                    #print points
                    center = aim.find_center(size,points,o_sides)
                    if center_display:
                        print center
                    degrees = aim.get_degrees(size,center)
                    if degree_display:
                        print degrees
                    hardware.move_by_degrees(degrees)
                    if np.sum(points) > 0:
                        target_found = True
                        frame_count += 1
                        if frame_count > 8:
                            hardware.fire()
                            #print "Weapon fired!"
                            #print "The 'Destroyer' will now be deactivated"
                            #done = True
                    else:
                        target_found = False
                        frame_count = 0
                    #result[center[0],center[1]] = [17, 15, 100]

                    # update the screen to show the latest screen image
                    if display:
                        if display_option == 1:
                            result = image
                        elif display_option == 2:
                            if o_thr:
                                mask = thr_m
                            else:
                                mask = color_m
                        if display_option > 1:
                            result[mask] = [255,255,255]
                        mapped = surfarray.map_array(screen,result).transpose()
                        surfarray.blit_array(screen, mapped)
                        pygame.display.update()
                except:
                    #do nothing
                    print "A thread encountered an error"
                finally:
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    with lock:
                        pool.append(self)

def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            time.sleep(0.1)

def find_object(bin_img, sides=4):
    int_img = labeling.labeling(bin_img)
    num_obj = np.max(int_img)
    found_points = np.array([[0]])
    selected_label = 0
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

def find_any_moving_object(bin_img):
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
    t_sides = 0
    found_points = np.array([[0]])
    for i in range(1,num_obj+1):
        mask = (int_img == i)
        mask_sum = mask.sum()
        if mask_sum > 100:
            points = shape.find_points(mask)
            t_sides = shape.count_sides(points)
            if t_sides > 3 and mask_sum > biggest_pix:
                biggest_pix = mask_sum
                found = mask
                found_points = points
                found_sides = t_sides
    return (found,found_points,found_sides)

# running part
try:
    if camera != None:
        pool = [ImageProcessor() for i in range(1)]
        camera.resolution = size
        #camera.vflip = True
        #camera.hflip = True
        camera.framerate = 15
        time.sleep(2)
        camera.capture_sequence(streams(),'rgb', use_video_port=True)

    while pool:
        with lock:
            processor = pool.pop()
        processor.terminated = True
        processor.join()
finally:
    camera.close()
    time.sleep(1)
    hardware.ready()
    filelist = [ f for f in os.listdir(".") if f.endswith(".pyc") ]
    for f in filelist:
        os.remove(f)
    os.system("sudo rm -rf build")
