#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time

class Servos:
    # Initialise the PWM device using the default address
    pwm = PWM(0x40)
    # Note if you'd like more debug output you can instead run:
    #pwm = PWM(0x40, debug=True)

    servoMin = 270  #140  # Min pulse length out of 4096
    servoMid = 400  # mid point
    servoMax = 530  #660  # Max pulse length out of 4096
    servoTrg = 450  # triger point
    servo_x = 0 # servo x channel
    servo_y = 1 # servo y channel
    servo_t = 2 # servo trigger channel

    # def __init__(self):
    #     self.pwm = PWM(0x40)

    def get_pulses(self,degrees):
        y,x = degrees
        pulse_per_degree = float((self.servoMax-servoMin)/90)
        return (int(y*pulse_per_degree), int(x*pulse_per_degree))

    def move_by_degree(self,degrees):
        y,x = self.get_pulses(degrees)
        pwm.setPWM(servo_x, 0, x)
        pwm.setPWM(servo_y, 0, y)

    def fire():
        pwm.setPWM(servo_t, 0, servoTrg)