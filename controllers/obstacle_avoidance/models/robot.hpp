#include <stdio.h>
#include <webots/Supervisor.hpp>
using namespace webots;

class GroundRobot
{
private:
    Node *node;
    Field *translation_field;
    Motor *wheels[4];
    DistanceSensor *distance_sensors[2];

    int avoid_obstacle_counter = 0;
    int direction_counter = 0;
    bool device_direction = true;
    bool turn = false;
    double left_speed = 5.0;
    double right_speed = 5.0;

public:
    Location *location;

    std::string robot_name;
    GroundRobot(Supervisor *supervisor, std::string name);

    void Update()
    {
        location = new Location(translation_field->getSFVec3f());
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
};
