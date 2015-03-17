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

surfarray.use_arraytype('numpy')
size = (240,180)
if display:
    pygame.init()
    screen = pygame.display.set_mode(size)
camera = picamera.PiCamera()
target_found = False
frame_count = 0
hardware.ready()

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

                    # color
                    mask = color.find_color(image)
                    # morphology
                    mask = morphology.closing(mask)
                    mask,points = find_object(mask,5)
                    # print points
                    result[mask] = [255,255,255]
                    center = aim.find_center(size,points,5)
                    # print center
                    degrees = aim.get_degrees(size,center)
                    # print degrees
                    hardware.move_by_degrees(degrees)
                    if np.sum(points) > 0:
                        target_found = True
                        frame_count += 1
                        if frame_count > 20:
                            hardware.fire()
                            if not display:
                                print 'Fired'
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

# running part
try:
    if camera != None:
        pool = [ImageProcessor() for i in range(4)]
        camera.resolution = size
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
    
