#include <iostream>
#include <string.h>

class Location
{
public:
    double x, y, z;
    Location();
    Location(const double *locations);
    Location(double x, double y, double z);

    bool IsClose(Location *other, double delta = 0.2)
    {
        if ((x <= other->x + delta && x >= other->x - delta) &&
            (z <= other->z + delta && z >= other->z - delta))
        {
            return true;
        }
        return false;
    }

    friend std::ostream &operator<<(std::ostream &os, const Location &dt);

    Location Add(Location *location)
    {
        return Location(x + location->x,
                        y + location->y,
                        z + location->z);
    }

    Location Subtract(Location *location)
    {
        return Location(x - location->x,
                        y - location->y,
                        z - location->z);
    }

    Location Clone()
    {
        return Location(x, y, z);
    }

    ~Location();
};

std::ostream &operator<<(std::ostream &os, const Location &loc)
{
    os << "(x: " << loc.x << " y: " << loc.y << " z: " << loc.z << ")";
    return os;
}

Location::Location(const double *locations)
{
    x = locations[0];
    y = locations[1];
    z = locations[2];
}
Location::Location(double x, double y, double z)
{
    this->x = x;
    this->y = y;
    this->z = z;
}
Location::Location()
{
    x = 0.0;
    y = 0.0;
    z = 0.0;
}
Location::~Location()
{
}
