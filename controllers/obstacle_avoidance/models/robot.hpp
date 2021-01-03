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

public:
    std::string robot_name;
    GroundRobot(Supervisor *supervisor, std::string name);

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