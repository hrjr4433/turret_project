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

done = False
lock = threading.Lock()
pool = []
display = False
o_thr = True
o_color = 'r'
o_sides = 5
prev_threshold = None
surfarray.use_arraytype('numpy')
size = (240,180)
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
option = raw_input("would you like to see what I see? ")
if option == 'y' or option == 'Y' or option == 'yes' or option == 'Yes':
    display = True
option = raw_input("choose what do you wish to find any moving object? ")
if option == 'y' or option == 'Y' or option == 'yes' or option == 'Yes':
    o_thr = True
else:
    option = raw_input("choose color of your target(r,b,y,g): ")
    if option == 'r' or option == 'b' or option == 'y' or option == 'g':
        o_color = option
    option = raw_input("choose the number of sides of your target(3-8): ")
    if option >= 3 and option <= 8:
        o_sides = option
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
        global done
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
                        # color
                        mask = color.find_color(image,o_color)
                        # morphology
                        mask = morphology.closing(mask)
                        # find object
                        mask,points = find_object(mask,o_sides)
                    else:
                        # thresholding
                        mask = threshold.thresholding(image)
                        # morphology
                        mask = morphology.opening(mask)
                        # find object
                        mask,points,o_sides = find_any_object(mask)
                    #print points
                    result[mask] = [255,255,255]
                    center = aim.find_center(size,points,o_sides)
                    #print center
                    degrees = aim.get_degrees(size,center)
                    #print degrees
                    hardware.move_by_degrees(degrees)
                    if np.sum(points) > 0:
                        target_found = True
                        frame_count += 1
                        if frame_count > 20:
                            hardware.fire()
                            print "Weapon fired!"
                            print "The 'Destroyer' will now be deactivated"
                            done = True
                    else:
                        target_found = False
                        frame_count = 0
                    #result[center[0],center[1]] = [17, 15, 100]

                    # update the screen to show the latest screen image
                    if display:
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
    return (found,points,t_sides)

# running part
try:
    if camera != None:
        pool = [ImageProcessor() for i in range(4)]
        camera.resolution = size
        #camera.vflip = True
        #camera.hflip = True
        camera.framerate = 30
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
