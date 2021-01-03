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

