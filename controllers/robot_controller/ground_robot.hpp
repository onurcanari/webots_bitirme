#include <stdio.h>
#include <stdlib.h> /* srand, rand */
#include <math.h>
#include <webots/DistanceSensor.hpp>
#include <webots/Motor.hpp>
#include <webots/Receiver.hpp>
#include <webots/Robot.hpp>
#include <webots/utils/AnsiCodes.hpp>
#include <webots/Compass.hpp>

#include <algorithm>
#include <iostream>
#include <limits>
#include <string>

#include "models/location_limit.hpp"

using namespace webots;

class GroundRobot : Robot
{
private:
    const int TIME_STEP = 64;
    Receiver *command_receiver;
    Compass *compass;
    Motor *wheels[4];
    DistanceSensor *distance_sensors[2];
    int avoid_obstacle_counter = 0;
    int direction_counter = 0;
    bool device_direction = true;
    bool turn = false;
    double left_speed = 5.0;
    double right_speed = 5.0;
    LocationLimit *robot_loc_limit;
    Location location_lower;

public:
    GroundRobot(std::string robotID);
    
    void CalculateAreas(){
        Location map_start = Location(2, 0, -2);
        Location *offset = new Location(0, 0, 1);
        location_lower = map_start.Clone();
        Location temp_upper = location_lower;
        
        bool found_area_to_search = false;
        while(!found_area_to_search)
        {
            temp_upper = location_lower.Add(offset);
            robot_loc_limit = new LocationLimit(&temp_upper, &temp_lower);
            // https://github.com/onurcanari/webots_bitirme/issues/4#issue-832042964
            // int area_number = robot_loc_limit.CalculateAreaNumber();
            // found_area_to_search = askForArea(areaNumber, robotID);
            location_lower = temp_upper;
        }

    }

    void GoRandom()
    {
        std::cout << "angle : "
                  << "angle";
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

    void GoWhere()
    {
        double x = -2.0, z = -2.0;

        double leftSpeed = 5.0;
        double rightSpeed = 5.0;

        std::string rotation = "right";

        const double *north = compass->getValues();

        double robotAngle = GetAngle(atan2(north[0], north[2]));

        double pointAngle = GetAngle(atan2(x, z));

        double angle = abs(robotAngle - pointAngle);

        std::cout << "angle : " << angle << std::endl;

        /*  if (angle > 180)
        {
            angle = 360 - angle;
            rotation = "right";
        } */

        if (angle > -1 && angle < 1)
        {
            leftSpeed = 5.0;
            rightSpeed = 5.0;
        }
        else
        {
            if (rotation == "right")
            {
                leftSpeed = 1.0;
                rightSpeed = -1.0;
            }
            else
            {
                leftSpeed = -1.0;
                rightSpeed = 1.0;
            }
        }

        wheels[0]->setVelocity(leftSpeed);
        wheels[1]->setVelocity(rightSpeed);
        wheels[2]->setVelocity(leftSpeed);
        wheels[3]->setVelocity(rightSpeed);
    }
    double GetAngle(double rad)
    {
        double bearing = (rad - 1.5708) / M_PI * 180.0;
        if (bearing < 0.0)
            bearing = bearing + 360.0;
        return bearing;
    }

    ~GroundRobot();

    void Run()
    {
        while (step(TIME_STEP) != -1)
        {
            GoWhere();
        }
    }

    std::string GetName()
    {
        return getName();
    }
};

GroundRobot::GroundRobot(std::string robotID)
{
    // uzaklık sensörlerini kaydet ve başlat
    char dsNames[2][10] = {"ds_right", "ds_left"};
    for (int i = 0; i < 2; i++)
    {
        distance_sensors[i] = getDistanceSensor(dsNames[i]);
        distance_sensors[i]->enable(TIME_STEP);
    }

    // motorları ekle, pozsiyonlarını ayarlar ve başlat
    char wheels_names[4][8] = {"wheel1", "wheel2", "wheel3", "wheel4"};
    for (int i = 0; i < 4; i++)
    {
        wheels[i] = getMotor(wheels_names[i]);
        wheels[i]->setPosition(INFINITY);
        wheels[i]->setVelocity(0.0);
    }

    command_receiver = getReceiver("receiver");
    command_receiver->setChannel(stoi(robotID));
    compass = getCompass("compass");
    compass->enable(TIME_STEP);
}
GroundRobot::~GroundRobot()
{
}