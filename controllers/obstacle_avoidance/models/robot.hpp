#include <stdio.h>
#include <stdlib.h> /* srand, rand */
#include <webots/Supervisor.hpp>

using namespace webots;

class GroundRobot
{
private:
    Node *node;
    Field *translation_field;
    Location *location;
    LocationLimit *location_limit;

public:
    std::string robot_name;
    GroundRobot(Supervisor *supervisor, std::string name, LocationLimit *location_limit);

    // konumunu günceller
    void Update()
    {
        location = new Location(translation_field->getSFVec3f());
    }

    // lokasyonun değerini döndür. pointer olarak dönmez.
    Location GetLocation()
    {
        return *location;
    }

    ~GroundRobot();
};

GroundRobot::GroundRobot(Supervisor *supervisor, std::string name, LocationLimit *location_limit)
{
    // GroundRobot constructerı
    // isiminden node ve translation definii alıp tutar. buralardan konumuna ulaşırız.
    robot_name = name;
    node = supervisor->getFromDef(robot_name);
    this->location_limit = location_limit;
    if (node == NULL)
    {
        std::cout << name << "'s node is NULL";
    }
    translation_field = node->getField("translation");
}
GroundRobot::~GroundRobot()
{
}