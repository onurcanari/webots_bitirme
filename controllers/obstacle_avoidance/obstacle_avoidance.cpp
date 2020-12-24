#include <webots/DistanceSensor.hpp>
#include <webots/Motor.hpp>
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <stdlib.h>
#include <stdio.h>
#include <time.h> /* time */
#include "models/objects.cpp"

#define TIME_STEP 64
#define MINE_COUNT 2
#define ROBOT_COUNT 1

using namespace webots;

int main()
{
  GroundRobot *robots[ROBOT_COUNT];
  GroundMine *mines[MINE_COUNT];

  Supervisor *supervisor = new Supervisor();
  srand(time(NULL));

  char buffer[20];

  for (int i = 0; i < ROBOT_COUNT; i++)
  {
    sprintf(buffer, "robot%d", i);
    robots[i] = new GroundRobot(supervisor, std::string(buffer));
  }

  for (int i = 0; i < MINE_COUNT; i++)
  {
    sprintf(buffer, "mine%d", i);
    mines[i] = new GroundMine(supervisor, std::string(buffer));
    mines[i]->Update();
  }

  //  #######    While Loop    #######
  while (supervisor->step(TIME_STEP) != -1)
  {
    for (int i = 0; i < ROBOT_COUNT; i++)
    {
      robots[i]->Update();
      for (int i = 0; i < MINE_COUNT; i++)
      {
        bool isClose = robots[i]->location->IsClose(mines[i]->location);
        if (isClose)
        {
          std::cout << "Buldum\n";
          std::cout << "x:" << robots[i]->location->x;
          std::cout << " x:" << mines[i]->location->x << std::endl;
        }
      }
    }
  }

  //delete robot;
  delete supervisor;

  return 0; // EXIT_SUCCESS
}