#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  imu_rpc_server.py
# 
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import time
import board
import busio
import adafruit_bno055
import serial

# Use these lines for I2C
# i2c = busio.I2C(board.SCL, board.SDA)
# sensor = adafruit_bno055.BNO055_I2C(i2c)

# Use these lines for UART except Linux devices
# uart = busio.UART(board.TX, board.RX)
# sensor = adafruit_bno055.BNO055_UART(uart)

# Use these lines for UART on Linux (e.g., for Raspberry Pi)
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1000)
sensor = adafruit_bno055.BNO055_UART(uart)
# Set mode to IMU (use accel, gyro, but not magnetometer)
sensor.mode = 0x08
AXIS_REMAP_X = 0x00
AXIS_REMAP_Y = 0x01
AXIS_REMAP_Z = 0x02
AXIS_REMAP_POSITIVE = 0x00
AXIS_REMAP_NEGATIVE = 0x01
# Set orientation based on board orientatin in specific project
remap = (0x01, 0x00, 0x02, 0x00, 0x01, 0x00)
sensor.axis_remap = remap
    
def read_sensor():
    """Returns the orientation in quaternion form"""
    quat = sensor.quaternion
    return quat

server = SimpleXMLRPCServer(('192.168.88.184', 8000)) 
server.register_introspection_functions()
server.register_function(read_sensor)

try:
    print('Use CTRL-C to exit')
    print('Listening on port 8000...')
    server.serve_forever()

except KeyboardInterrupt:
    print('Keyboard interrup received. Exiting')

