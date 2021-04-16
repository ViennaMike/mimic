# mimic
Raspberry Pi code for skull to copy movement of IMU sensor. Sensor and skull communicate wirelessly
## Overview
This project has two units, a sensor unit and a controller unit. The sensor unit consists of a [Raspberry Pi Zero W](https://www.raspberrypi.org/pi-zero-w/) and an [Adafruit BNO055](https://www.adafruit.com/product/2472) 9 degree of freedom IMU Board. The controller unit consists of another Pi Zero W and a [Pololu Maestro Servo Controller](https://www.pololu.com/category/102/maestro-usb-servo-controllers). 

The project has two units: the sensor unit and the controller unit. The Sensor unit consists of a Raspberry Pi Zero W and an Adafruit BNO055 9-Degrees of Freedom IMU board. The controller unit consists of another Pi Zero W and a Pololu Maestro Servo Controller. The two communicate with each other using XMLRPC running over WiFi. The Sensor unit acts as the server and the Controller unit acts as the client. 

I mounted the sensor Pi and IMU board on the brim of a baseball cap, so it will track my head movements. For more on this project, see [add link to my blog post]
## Prerequisites
The sensor software uses CircuitPython and Adafruit's Blinka library must be installed to support CircuitPython on a Pi. In addition, the adafruit_bno055 program is needed to interface with the board. Be sure to use the CircuitPython version rather than the earlier version. 

## Hardware
This project requires two Raspberry Pi's with WiFi (I used Pi Zero W's), an Adafruit BNO055 IMU board, and a Pololu Maestro Servo Controller to control the motions of a 3-axis skull. You also need some jumper wires and a USB OTG cable. The OTG cable is used to connect the controller Pi to the Maestro Servo Controller. 

## Sensor
The sensor software is just one program, imu_rpc_server.py. It is configured to use a UART interface to the BNO055 board. One can use an i2c interface instead by changing a few line at the top of the program, however all Raspberry Pi's have a hardware issue with i2c clock stretching, and the sensor board uses clock stretching. This gave extremely unreliable results when I was developing this software and I put the entire project aside for months until I came back and found out about the hardware issue. There is a workaround that you can use if you want to use i2c that consists of slowing the speed down so that clock stretching will rarely (hopefully never) be needed. You can read more about the issue here: https://www.mcgurrin.info/robots/723/. 

Normally when the Pi kernel boots up it will put a login terminal on the serial port. You'll need to turn this off if using the UART interface. To do so, you can run the raspi-config tool and go to Interface Options, then to Serial Port, and disable shell messages on the serial connection. Then reboot the Pi. If you later need to re-enable it, just follow the same procedure. To wire up the sensor board and the Pi using the UART interface:
- Connect BNO055 Vin to Raspberry Pi 3.3V power.
- Connect BNO055 GND to Raspbery Pi ground.
- Connect BNO055 SDA (now UART TX) to Raspberry Pi RXD pin.
- Connect BNO055 SCL (now UART RX) to Raspberry Pi TXD pin.
- Connect BNO055 PS1 to BNO055 Vin / Raspberry Pi 3.3V power

You can test that everthing is working by running the simpletestuart.py program. It will print out the temperature of the board, the individual sensor parameters, and the integrated Euler angle and Quaternion values, as well as the calibration status and the axis map. This will update every 5 seconds. Don't worry that the magnetometer readings will be None. This project uses relative orientation and therefore the software turns off the magnetometer. For more information on the board and the various outputs and settings, see the [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/036/832/original/BST_BNO055_DS000_14.pdf). 

The imu_rpc_server.py program is similar to the test program, but it only reads the quaternion values (the Euler angles are unreliable on this sensor). It also starts and XMLRPC server that will respond to read_sensor requests by returning the quaternion value for the current orientation. The program, once started runs continually until forced closed. 
## Controller
The controller software runs on a different Pi, and consists of two programs: main_controller.py and maestro.py. Main_controller.py initializes the servo controller and sets limits on the speed and acceleration for the servos. I found this cuts down on the noise of the servos, provides smoother motion, and keeps the head from whipping around when turning. 

The board queries the sensor Pi via XMLRPC fifty times per second to get the position as a quaternion. It converts the quaternion into Euler angles and converts the Euler angles into servo commands and sends the servo commands to the Maestro board. It also generates a sequence of eye movements and sends that to the Maestro as well.

ManServoTest can be used as you set things up to make sure your controller Pi is talking to the Maestro correctly. 
## Use
Set up the Pi's to connect to your local WiFi network and install CircuitPython on the sensor Pi (it's not needed for the controller). Then install the appropriate modules on each one. Connect the sensor Pi to the BNO055 and connect the controller Pi to the Maestro Servo Controller using a USB OTG cable. And, of course, connect the appropriate pins on the servo controller to the servos controlling your skull. Roll or tilt is channel 0, pitch or nod is channel 1, yaw or pan is channel 2, and random eye movements are sent out on channel 3.

Once everything is hooked up, you must start imu_rpc_server.py on the sensor pi first, so that it starts the XMLRPC server. Then launch main_controller.py on the controller Pi and you're off and running. 
