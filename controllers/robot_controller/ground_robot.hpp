#include <stdio.h>
#include <stdlib.h> /* srand, rand */
#include <webots/DistanceSensor.hpp>
#include <webots/Motor.hpp>
#include <webots/Receiver.hpp>
#include <webots/Robot.hpp>
#include <webots/utils/AnsiCodes.hpp>

#include <algorithm>
#include <iostream>
#include <limits>
#include <string>

using namespace webots;

class GroundRobot : Robot
{
private:
    const int TIME_STEP = 64;
    Motor *wheels[4];
    DistanceSensor *distance_sensors[2];
    int avoid_obstacle_counter = 0;
    int direction_counter = 0;
    bool device_direction = true;
    bool turn = false;
    double left_speed = 5.0;
    double right_speed = 5.0;

public:
    GroundRobot();

    void GoRandom()
    {
        double leftSpeed = 5.0;
        double rightSpeed = 5.0;
        if (avoid_obstacle_counter > 0)
        {
            avoid_obstacle_counter--;
            if (device_direction)
            {
                leftSpeed = -1.0;
                rightSpeed = 1.0;
            }
            else
            {
                leftSpeed = 1.0;
                rightSpeed = -1.0;
            }
        }
        else
        {
            for (int i = 0; i < 2; i++)
            {
                if (distance_sensors[i]->getValue() < 950.0)
                {
                    avoid_obstacle_counter = rand() % 100 + 1;
                    direction_counter = rand() % 200 + 10;
                    turn = true;
                    return;
                }
            }

            if (direction_counter > 0)
            {
                direction_counter--;
            }
            else
            {
                device_direction = (rand() % 10 + 1) > 5;
                avoid_obstacle_counter = rand() % 100 + 1;
                direction_counter = rand() % 200 + 10;
                std::cout << "\n";
            }
        }
        wheels[0]->setVelocity(leftSpeed);
        wheels[1]->setVelocity(rightSpeed);
        wheels[2]->setVelocity(leftSpeed);
        wheels[3]->setVelocity(rightSpeed);
    }
    void ObstacleAvoidence()
    {
        double leftSpeed = 5.0;
        double rightSpeed = 5.0;

        if (avoid_obstacle_counter > 0)
        {
            avoid_obstacle_counter--;
            if (device_direction)
            {
                leftSpeed = -1.0;
                rightSpeed = 1.0;
            }
            else
            {
                leftSpeed = 1.0;
                rightSpeed = -1.0;
            }
        }
        else
        {
            if (direction_counter > 0)
            {
                direction_counter--;
            }
            else
            {
                if (turn)
                {
                    avoid_obstacle_counter = 57;
                    turn = false;
                }
                else
                {
                    for (int i = 0; i < 2; i++)
                    {
                        if (distance_sensors[i]->getValue() < 950.0)
                        {

                            avoid_obstacle_counter = 57;
                            direction_counter = 10;
                            turn = true;
                        }
                    }
                    if (avoid_obstacle_counter > 0)
                    {
                        device_direction = !device_direction;
                    }
                }
            }
        }
        wheels[0]->setVelocity(leftSpeed);
        wheels[1]->setVelocity(rightSpeed);
        wheels[2]->setVelocity(leftSpeed);
        wheels[3]->setVelocity(rightSpeed);
    }
    ~GroundRobot();

    void Run()
    {
        while (step(TIME_STEP) != -1)
        {
            GoRandom();
        }
    }

    std::string GetName(){
        return getName();
    }
};

GroundRobot::GroundRobot()
{

    char dsNames[2][10] = {"ds_right", "ds_left"};
    for (int i = 0; i < 2; i++)
    {
        distance_sensors[i] = getDistanceSensor(dsNames[i]);
        distance_sensors[i]->enable(TIME_STEP);
    }
    char wheels_names[4][8] = {"wheel1", "wheel2", "wheel3", "wheel4"};
    for (int i = 0; i < 4; i++)
    {
        wheels[i] = getMotor(wheels_names[i]);
        wheels[i]->setPosition(INFINITY);
        wheels[i]->setVelocity(0.0);
    }
}
GroundRobot::~GroundRobot()
{}