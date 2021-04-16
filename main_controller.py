# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 17:15:23 2018

@author: Mike
This is the working wireless skull code. Acts as XMLRPC client
"""
import time
import maestro
import math
import xmlrpc.client
from random import randint, uniform
   
   
# Initialize servo controller
controller = maestro.Controller()
# Dict of motion to controller channel
motion_codes = {'tilt': 0, 'nod': 1, 'pan': 2, 'eyes': 3}
# Set servo speed. Unlimited has very jerky motion
controller.setSpeed(motion_codes['tilt'], 50)
controller.setSpeed(motion_codes['nod'], 75)
controller.setSpeed(motion_codes['pan'], 35)
# Set servo acceleration for smoother motion
controller.setAccel(motion_codes['tilt'], 50)
controller.setAccel(motion_codes['nod'], 75)
controller.setAccel(motion_codes['pan'], 35)
def quat2euler(q):
    # order from board seems to be w, y, x, z, so exchange x and y
    temp = q[1]
    q[1] = q[2]
    q[2] = temp
    # roll (x-axis rotation)
    sinr_cosp = 2.0 * (q[0] * q[1] + q[2] * q[3])
    cosr_cosp = 1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2])
    roll_r = -math.atan2(sinr_cosp, cosr_cosp)
    # pitch (y-axis rotation)
    sinp = 2.0 * (q[0] * q[2] - q[3] * q[1])
    if abs(sinp) >= 0.99:   
        pitch_r = math.copysign(math.pi / 2, sinp)
    else:
        pitch_r = math.asin(sinp)
    # yaw (z-axis rotation)
    siny_cosp = 2.0 * (q[0] * q[3] + q[1] * q[2])
    cosy_cosp = 1.0 - 2.0 * (q[2] * q[2] + q[3] * q[3])
    yaw_r = math.atan2(siny_cosp, cosy_cosp)
    
    return roll_r, pitch_r, yaw_r

def angle_conversion(angle, motion):
    """Takes an angle, in radians, and converts it to the input to the controller. 
    The units are quarter micro-seconds. Typical servo center is at 
    1500 microseconds, or 6000 quarter-microseconds.
    Typically valid servo range is 4000 to 8000 quarter-microseconds, although
    some have a greater range.
    For the skull, the servo ranges are 2400 - 9600 with 6000 quarter-micro-seconds
    as the middle, BUT they do not support the full range. here are the limits:
    Nod: 4400 (up), 6000 (center), 7600 (down)
    Pan: 4400 (left), 6000 (center), 7600 (right)
    Tilt: 5200 (right), 6000 (center), 6800 (left)
    Jaw: 6000 (closed), 4800 (normal open), 4400 (max open)
    Eyes: 4000 (left), 60000 (center), 8000 (right)
    """
    angle_range = 180
    controller_range = 9600 - 2400
    if motion == 'nod' or motion == 'tilt': angle = -angle
    controller_val = (((angle + 90) / angle_range) * controller_range) + 2400
    nod_min = 4400
    nod_max = 7552
    pan_min = 1992
    pan_max = 6912
    tilt_min = 5200
    tilt_max = 6800
    if (motion == 'nod'):
        controller_val = min(controller_val, nod_max)
        controller_val = max(controller_val, nod_min)
    if (motion == 'pan'):
        controller_val = min(controller_val, pan_max)
        controller_val = max(controller_val, pan_min)
    if (motion == 'tilt'):
        controller_val = min(controller_val, tilt_max)
        controller_val = max(controller_val, tilt_min)  
    return controller_val
    
"""
This class produces randomized eye movements.
Movements aren't totally random, the eye speed has 3 values and a 2/3rds chance
of staying the same each time it updates. The direction is divided into 3
sectors, right, center, and left, and there is a 50% chance it stays in the 
same sector. 

Eye range is 1000, 1500, 2000 BUT commanda are quarter-microseconds,so
Eyes: 4000 (left), 6000 (center), 8000 (right)
"""
class RandomEyes:
    def __init__(self):
        self.old_speed = 1
        self.old_position = 6000
        self.speeds = [10, 20, 60]
        self.start_time = time.time()
        # Call set range
        controller.setRange(motion_codes['eyes'], 4032, 8000)
    def move(self):  
        speed = self.old_speed
        position = self.old_position
        move_done = False
        if time.time() - self.start_time > 2.:
             move_done = True
             self.start_time = time.time()
        if move_done == True:
            if randint(0,2) < 1:
                speed = self.speeds[randint(0,2)] 
            if randint(0,10) < 5:
                if self.old_position < 5332:
                    position = randint(0, 5332)
                elif self.old_position < 6668:
                    position = randint(5333, 6668)
                else:
                    position = randint(6669, 8000)
            else:
                position = randint(4032, 8000)
                
            if randint(0,4) < 1:
                self.pause = uniform(0,2.) 
            else:
                self.pause = 0
            controller.setSpeed(motion_codes['eyes'], speed)
            controller.setTarget(motion_codes['eyes'], position)
        self.old_position = position
        self.old_speed = speed      
        return

# Initialize the eye movement
eyes = RandomEyes()

# Check XMLRPC Connection
with xmlrpc.client.ServerProxy("http://192.168.88.184:8000") as proxy:
    try:
        print('sensor methods: ',proxy.system.listMethods())
    except xmlrpc.client.Fault as err:
        print("A fault occurred")
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)
    except xmlrpc.client.ProtocolError as err:
        print("A protocol error occurred")
        print("URL: %s" % err.url)
        print("HTTP/HTTPS headers: %s" % err.headers)
        print("Error code: %d" % err.errcode)
        print("Error message: %s" % err.errmsg)
    except ConnectionError as err:
        print("\nConnection error. Is the server running? {}".format(err))
    # Start mimicing
    while True:
        # Update orientation
        try:
            orientation = proxy.read_sensor()
        except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)
        except xmlrpc.client.ProtocolError as err:
            print("A protocol error occurred")
            print("URL: %s" % err.url)
            print("HTTP/HTTPS headers: %s" % err.headers)
            print("Error code: %d" % err.errcode)
            print("Error message: %s" % err.errmsg)
            print('quaternion: {}'.format(orientation))
      
        ## Convert to Euler angles in radians
        roll_r, pitch_r, yaw_r = quat2euler(orientation)
        
        # Convert to degrees
        roll = math.degrees(roll_r)
        pitch = math.degrees(pitch_r)
        yaw = -math.degrees(yaw_r)
        if yaw > 90.: yaw = 90.
        if yaw < -90.: yaw = -90.
        if roll > 90.: roll = 90.
        if roll < -90.: roll = -90.
        if pitch > 90.: pitch = 90.
        if pitch < -90.: pitch = -90.
        roll = -roll
        roll_cmd = int(angle_conversion(roll, 'tilt'))
        pitch_cmd = int(angle_conversion(pitch, 'nod'))
        yaw_cmd = int(angle_conversion(yaw, 'pan'))
        
        # send commands to servo controller
        controller.setTarget(motion_codes['tilt'], roll_cmd)
        controller.setTarget(motion_codes['nod'], pitch_cmd)
        controller.setTarget(motion_codes['pan'], yaw_cmd)
        eyes.move()
        time.sleep(0.01)   # sleep for 1/10 of a second. Update to tune performance
    
        # test code, remove for final    
        #print('roll:',roll)
        #print(roll_cmd)
        #print('pitch:',pitch)
        #print(pitch_cmd)
        #print('yaw:',yaw)
        #print(yaw_cmd)
        #time.sleep(3)
    

