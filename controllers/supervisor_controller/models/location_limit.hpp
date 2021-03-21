#include "location.hpp"
using namespace std;
class LocationLimit
{
private:
    Location *upper_limit, *lower_limit;

public:
    LocationLimit(Location *upper, Location *lower);
    ~LocationLimit();

    bool IsInside(Location loc)
    {
        return true;
    }

    LocationLimit Copy()
    {
        return LocationLimit(upper_limit, lower_limit);
    }

    Location getUpper()
    {
        /*         cout << "upper_limit : " << upper_limit->x << endl;
        cout << "upper_limit : " << upper_limit->y << endl;
        cout << "upper_limit : " << upper_limit->z << endl; */
        return *upper_limit;
    }

    /*     double getLower(char value)
    {

        switch (value)
        {
        case 'x':
            return lower_limit->x;
        case 'y':
            return lower_limit->y;
        case 'z':
        cout << "lower_limit : " << *lower_limit.z << endl;
            return *lower_limit.z;
        default:
            return 0.0;
        }
    } */
    friend std::ostream &operator<<(std::ostream &os, const LocationLimit &lt);
};

std::ostream &operator<<(std::ostream &os, const LocationLimit &lt)
{
    os << "Upper Limit : " << *lt.upper_limit << " / Lower Limit : " << *lt.lower_limit << endl;
    return os;
}

LocationLimit::LocationLimit(Location *upper_limit, Location *lower_limit)
{
    this->upper_limit = upper_limit;
    this->lower_limit = lower_limit;
}

LocationLimit::~LocationLimit()
{
    delete upper_limit;
    delete lower_limit;
}