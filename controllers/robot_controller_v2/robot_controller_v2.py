import argparse
import GroundRobot

parser = argparse.ArgumentParser()
parser.add_argument('robot_name', type=str)
args = parser.parse_args()

ground_robot = GroundRobot(args.robot_name)
ground_robot.run();