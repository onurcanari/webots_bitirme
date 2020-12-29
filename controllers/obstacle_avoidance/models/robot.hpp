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

    void Update()
    {
        location = new Location(translation_field->getSFVec3f());
    }
    Location GetLocation()
    {
        return *location;
    }

    ~GroundRobot();
};
