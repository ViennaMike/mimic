# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 17:15:23 2018

@author: Mike
"""
import time
import maestro

# Initialize servo controller
servos = maestro.Controller()

angle_range = [-90., 90.]
timing_range = [4000., 8000.]  # units are quarter-microseconds
servo_min = 5200  # minimum safe value for servo command
servo_max = 6800  # maximimum safe value for servo command

def scale(val, src, dst):
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

def angle_conversion(angle):
    """Takes an angle, in radians, and converts it to the input to the controller. 
    The units are quarter micro-seconds. Typical servo center is at 
    1500 microseconds, or 6000 quarter-microseconds.
    Typcially valid servo range is 4000 to 8000 quarter-microseconds, although
    some have a greater range.
    """
    (-30.,1886), (-20.,1825), (-10.,1755), (0.,1666), (10.,1599), (20.,1497), (30.,1396)
    servo_target = scale(angle, angle_range, timing_range)
    # Limit motion to safe range
    if servo_target < servo_min: servo_target = servo_min
    if servo_target > servo_max: servo_target = servo_max
    
    return servo_target

while True:
    tilt = float(input('tilt in degrees'))
    nod = float(input('nod in degrees'))
    turn = float(input('turn in degrees'))
    roll_cmd = int(angle_conversion(tilt))
    pitch_cmd = int(angle_conversion(nod))
    yaw_cmd = int(angle_conversion(turn))
    
    # send commands to servo controller
    servos.setTarget(0, roll_cmd)
    servos.setTarget(1, pitch_cmd)
    servos.setTarget(2, yaw_cmd)
    time.sleep(0.5)   # sleep for 1/2 of a second. 
    

    

