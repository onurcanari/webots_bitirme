import time

from ground_robot import GroundRobot
from sys import argv

time.sleep(0)
ground_robot = GroundRobot(argv[1])
ground_robot.run()
