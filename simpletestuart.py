# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

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

last_val = 0xFFFF

sensor.mode = 0x08
AXIS_REMAP_X = 0x00
AXIS_REMAP_Y = 0x01
AXIS_REMAP_Z = 0x02
AXIS_REMAP_POSITIVE = 0x00
AXIS_REMAP_NEGATIVE = 0x01
remap = (0x01, 0x00, 0x02, 0x00, 0x01, 0x00)
sensor.axis_remap = remap

def temperature():
    global last_val  # pylint: disable=global-statement
    result = sensor.temperature
    if abs(result - last_val) == 128:
        result = sensor.temperature
        if abs(result - last_val) == 128:
            return 0b00111111 & result
    last_val = result
    return result

for i in range(20):
    print("Temperature: {} degrees C".format(sensor.temperature))
    """
    print(
        "Temperature: {} degrees C".format(temperature())
    )  # Uncomment if using a Raspberry Pi
    """
    print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
    print("Magnetometer (microteslas): {}".format(sensor.magnetic))
    print("Gyroscope (rad/sec): {}".format(sensor.gyro))
    print("Euler angle: {}".format(sensor.euler))
    print("Quaternion: {}".format(sensor.quaternion))
    print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
    print("Gravity (m/s^2): {}".format(sensor.gravity))
    print("calibration: {}".format(sensor.calibration_status))
    print("axis map: {}".format(sensor.axis_remap))
    print()
    # if i == 10:
        # sensor.axis_remap = remap
    i += 1
    time.sleep(5)
