#include <iostream>
#include <string.h>

class Location
{
public:
    double x, y, z;
    Location(const double *locations);

    bool IsClose(Location *other, double delta = 0.2)
    {
        if ((x <= other->x + delta && x >= other->x - delta) &&
            (z <= other->z + delta && z >= other->z - delta))
        {
            return true;
        }
        return false;
    }

    std::ostream &operator<<(std::ostream &strm)
    {
        return strm << "(x: " << x << " y: " << y << " z: " << z << ")";
    }

    ~Location();
};

Location::Location(const double *locations)
{
    x = locations[0];
    y = locations[1];
    z = locations[2];
}
Location::~Location()
{
}