#include <stdio.h>
#include <webots/Supervisor.hpp>
#include "location.hpp"
#include "mine.hpp"
#include "robot.hpp"

GroundRobot::GroundRobot(Supervisor *supervisor, std::string name)
{
    // GroundRobot constructerı
    // isiminden node ve translation definii alıp tutar. buralardan konumuna ulaşırız.
    robot_name = name;
    node = supervisor->getFromDef(robot_name);
    if (node == NULL)
    {
        std::cout << name << "'s node is NULL";
    }
    translation_field = node->getField("translation");
}
GroundRobot::~GroundRobot()
{
}

GroundMine::GroundMine(Supervisor *supervisor, std::string name)
{
    // GroundMine constructerı
    // isiminden node ve translation definii alıp tutar. buralardan konumuna ulaşırız.
    mine_name = name;
    node = supervisor->getFromDef(mine_name);
    translation_field = node->getField("translation");
    Update();
}

GroundMine::~GroundMine()
{
}

Location::Location(const double *locations)
{
    x = locations[0];
    y = locations[1];
    z = locations[2];
}
Location::~Location()
{
}