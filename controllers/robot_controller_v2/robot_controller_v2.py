import time

from ground_robot import GroundRobot
from sys import argv

ground_robot = GroundRobot(argv[1])
time.sleep(20)
ground_robot.run()
