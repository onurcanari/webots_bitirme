#include <stdio.h>
#include <webots/Supervisor.hpp>
#include "location.hpp"
#include "mine.hpp"
#include "robot.hpp"

GroundRobot::GroundRobot(Supervisor *supervisor, std::string name)
{
    robot_name = name;
    node = supervisor->getFromDef(robot_name);
    translation_field = node->getField("translation");
    char dsNames[2][10] = {"ds_right", "ds_left"};
    for (int i = 0; i < 2; i++)
    {
        distance_sensors[i] = supervisor->getDistanceSensor(dsNames[i]);
        distance_sensors[i]->enable(64); //time step = 64
    }
    char wheels_names[4][8] = {"wheel1", "wheel2", "wheel3", "wheel4"};
    for (int i = 0; i < 4; i++)
    {
        wheels[i] = supervisor->getMotor(wheels_names[i]);
        wheels[i]->setPosition(INFINITY);
        wheels[i]->setVelocity(0.0);
    }
}

GroundMine::GroundMine(Supervisor *supervisor, std::string name)
{
    mine_name = name;
    node = supervisor->getFromDef(mine_name);
    translation_field = node->getField("translation");
    Update();
}

Location::Location(const double *locations){
    x = locations[0];
    y = locations[1];
    z = locations[2];
}