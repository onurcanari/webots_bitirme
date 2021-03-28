#include <stdio.h>
#include <stdlib.h> /* srand, rand */
#include <math.h>
#include <webots/DistanceSensor.hpp>
#include <webots/Motor.hpp>
#include <webots/Receiver.hpp>
#include <webots/Robot.hpp>
#include <webots/utils/AnsiCodes.hpp>
#include <webots/Field.hpp>
#include <webots/Compass.hpp>
#include <webots/Supervisor.hpp>
#include <webots/Emitter.hpp>

#include <algorithm>
#include <iostream>
#include <limits>
#include <string>

#include "models/location_limit.hpp"

using namespace webots;
using namespace std;

class GroundRobot : Supervisor
{
private:
    int robotID;
    const int TIME_STEP = 64;
    Emitter *emitter;
    Receiver *receiver;
    // Compass *compass;
    Motor *wheels[4];
    DistanceSensor *distance_sensors[2];
    int avoid_obstacle_counter = 0;
    int direction_counter = 0;
    bool device_direction = true;
    bool turn = false;
    double left_speed = 5.0;
    double right_speed = 5.0;
    LocationLimit *robot_loc_limit;
    Location location_lower;

    Field *translation_field;

    Location *robot_location;

    unordered_map<int, Location> robot_location_map;
    unordered_map<int, double> robot_distances;
    bool discovery_started = false;
    Location map_start = Location(2, 0, -2);

public:
    GroundRobot(string robotID);

    void Setup()
    {
        string name = GetName();
        robotID = 0.0 + (name[5] - '0');
        cout << "Setup ground robot : " << name << "Robot ID : " << robotID << endl;
        translation_field = getSelf()->getField("translation");

        cout << "Getting distance sensors and enable them..." << endl;
        char dsNames[2][10] = {"ds_right", "ds_left"};
        for (int i = 0; i < 2; i++)
        {
            distance_sensors[i] = getDistanceSensor(dsNames[i]);
            distance_sensors[i]->enable(TIME_STEP);
        }

        cout << "Get and reposition motors.." << endl;
        char wheels_names[4][8] = {"wheel1", "wheel2", "wheel3", "wheel4"};
        for (int i = 0; i < 4; i++)
        {
            wheels[i] = getMotor(wheels_names[i]);
            wheels[i]->setPosition(INFINITY);
            wheels[i]->setVelocity(0.0);
        }

        cout << "Get and Set Emitter" << endl;
        emitter = getEmitter("emitter");
        emitter->setChannel(-1);
        cout << "Get and set Receiver" << endl;
        receiver = getReceiver("receiver");
        receiver->setChannel(-1);
        receiver->enable(TIME_STEP);
        cout << "Setup Passed" << endl;
    }

    // Robotun lokasyonunu günceller
    void UpdateLocation()
    {
        robot_location = new Location(translation_field->getSFVec3f());
    }

    // lokasyonun değerini döndür. pointer olarak dönmez.
    Location *GetLocation()
    {
        return robot_location;
    }

    void CalculateAreaToDiscover(int turn)
    {

        Location *offset = new Location(0, 0, 1.0 * turn);
        location_lower = location_lower.Add(offset);

        temp_upper = location_lower.Add(new Location(0, 0, 1.0));
        robot_loc_limit = new LocationLimit(&temp_upper, &location_lower);
        // https://github.com/onurcanari/webots_bitirme/issues/4#issue-832042964
        // int area_number = robot_loc_limit.CalculateAreaNumber();
        // found_area_to_search = askForArea(areaNumber, robotID);
    }

    void SaveRobotsLocation(double *message)
    {
        if (robot_location_map[*message] != NULL)
        {
            robot_location_map[*message] = Location(message++)
        }
    }

    void SelectArea()
    {
        if (discovery_started == true)
        {
            return;
        }

        discovery_started = true;
        for (auto const &x : robot_location_map)
        {
            robot_distances[x.second->Compare(map_start)] = x.first;
        }
        int i = 1;
        for (auto const &x : robot_distances)
        {
            if (x.second == robotID)
            {
                CalculateAreaToDiscover(i);
                break;
            }
            i++;
        }
        GoCoverage();
    }

    void GoRandom()
    {

        double leftSpeed = 5.0;
        double rightSpeed = 5.0;
        if (avoid_obstacle_counter > 0)
        {
            avoid_obstacle_counter--;
            if (device_direction)
            {
                leftSpeed = -1.0;
                rightSpeed = 1.0;
            }
            else
            {
                leftSpeed = 1.0;
                rightSpeed = -1.0;
            }
        }
        else
        {
            for (int i = 0; i < 2; i++)
            {
                if (distance_sensors[i]->getValue() < 950.0)
                {
                    avoid_obstacle_counter = rand() % 100 + 1;
                    direction_counter = rand() % 200 + 10;
                    turn = true;
                    return;
                }
            }

            if (direction_counter > 0) 
            {
                direction_counter--;
            }
            else
            {
                device_direction = (rand() % 10 + 1) > 5;
                avoid_obstacle_counter = rand() % 100 + 1;
                direction_counter = rand() % 200 + 10;
                cout << "\n";
            }
        }
        wheels[0]->setVelocity(leftSpeed);
        wheels[1]->setVelocity(rightSpeed);
        wheels[2]->setVelocity(leftSpeed);
        wheels[3]->setVelocity(rightSpeed);
    }

    void GoCoverage()
    {
        double leftSpeed = 5.0;
        double rightSpeed = 5.0;

        if (avoid_obstacle_counter > 0)
        {
            avoid_obstacle_counter--;
            if (device_direction)
            {
                leftSpeed = -1.0;
                rightSpeed = 1.0;
            }
            else
            {
                leftSpeed = 1.0;
                rightSpeed = -1.0;
            }
        }
        else
        {
            if (direction_counter > 0)
            {
                direction_counter--;
            }
            else
            {
                if (turn)
                {
                    avoid_obstacle_counter = 57;
                    turn = false;
                }
                else
                {
                    for (int i = 0; i < 2; i++)
                    {
                        if (GetMessage())
                        {
                            avoid_obstacle_counter = 57;
                            direction_counter = 10;
                            turn = true;
                        }
                    }
                    if (avoid_obstacle_counter > 0)
                    {
                        device_direction = !device_direction;
                    }
                }
            }
        }
        wheels[0]->setVelocity(leftSpeed);
        wheels[1]->setVelocity(rightSpeed);
        wheels[2]->setVelocity(leftSpeed);
        wheels[3]->setVelocity(rightSpeed);
    }

    void ObstacleAvoidence()
    {
        double leftSpeed = 5.0;
        double rightSpeed = 5.0;

        if (avoid_obstacle_counter > 0)
        {
            avoid_obstacle_counter--;
            if (device_direction)
            {
                leftSpeed = -1.0;
                rightSpeed = 1.0;
            }
            else
            {
                leftSpeed = 1.0;
                rightSpeed = -1.0;
            }
        }
        else
        {
            if (direction_counter > 0)
            {
                direction_counter--;
            }
            else
            {
                if (turn)
                {
                    avoid_obstacle_counter = 57;
                    turn = false;
                }
                else
                {
                    for (int i = 0; i < 2; i++)
                    {
                        if (distance_sensors[i]->getValue() < 950.0)
                        {

                            avoid_obstacle_counter = 57;
                            direction_counter = 10;
                            turn = true;
                        }
                    }
                    if (avoid_obstacle_counter > 0)
                    {
                        device_direction = !device_direction;
                    }
                }
            }
        }
        wheels[0]->setVelocity(leftSpeed);
        wheels[1]->setVelocity(rightSpeed);
        wheels[2]->setVelocity(leftSpeed);
        wheels[3]->setVelocity(rightSpeed);
    }

    //TODO DÜZELTİLECEK
    void LocationControl()
    {
       if (GetLocation().z < robot->getUpperZ())
        {
            sendMessage("turnRight", (robot->message).c_str(), (int)(robot->channel));
            robot->message = "turnRight";
        }
        else if (robot->GetLocation().z > robot->getLowerZ())
        {
            sendMessage("turnLeft", (robot->message).c_str(), (int)(robot->channel));
            robot->message = "turnLeft";
        }
    }

    ~GroundRobot();
    
    //TODO DÜZELTİLECEK
    int GetMessage()
    {
        if (receiver->getQueueLength() > 0)
        {
            string message((const char *)receiver->getData());
            receiver->nextPacket();
            if (message.compare("turnRight") == 0)
            {
                cout << "sağa dönmem lazim" << endl;
                return 1;
            }
            else if (message.compare("turnLeft") == 0)
            {
                cout << "sola dönmem lazim" << endl;
                return 1;
            }
        }
        return 0;
    }

    void ListenLocationData()
    {
        if (receiver->getQueueLength() > 0)
        {
            double *message = (double *)receiver->getData();

            cout << "Robot ID : " << message[0] << " (x : " << message[1] << ", y : " << message[2] << ", z : " << message[3] << ")" << endl;
            //cout << format("Robot ID : {} (x : {} y : {}, z : {})", message[0], message[1], message[2], message[3]) << endl;
            receiver->nextPacket();
        }
    }

    void SendLocation()
    {
        Location *location = GetLocation();
        if (location == NULL)
            return;

        double array[4] = {robotID, location->x, location->y, location->z};
        emitter->send(array, 4 * sizeof(double));
    }

    void Run()
    {
        cout << "Start robot" << endl;
        while (step(TIME_STEP) != -1)
        {
            UpdateLocation();
            SendLocation();
            ListenLocationData();
        }
    }

    string GetName()
    {
        return getName();
    }
};

GroundRobot::GroundRobot(string robotID)
{
    Setup();
}
GroundRobot::~GroundRobot()
{
}