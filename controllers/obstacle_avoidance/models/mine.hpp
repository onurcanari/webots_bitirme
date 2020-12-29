#include <webots/Supervisor.hpp>
using namespace webots;

class GroundMine
{
private:
    Node *node;
    Field *translation_field;

public:
    bool is_found = false;
    Location *location;
    std::string mine_name;
    GroundMine(Supervisor *supervisor, std::string name);

    // konumunu günceller
    void Update()
    {
        const double *vect = translation_field->getSFVec3f();
        location = new Location(vect);
    }

    ~GroundMine();
};
