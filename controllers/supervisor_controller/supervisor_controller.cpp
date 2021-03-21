#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include "simulation_center.cpp"

#define MINE_COUNT 6
#define ROBOT_COUNT 4

using namespace webots;

int main()
{
  SimulationCenter simulation_center = SimulationCenter(ROBOT_COUNT, MINE_COUNT);
  simulation_center.Run();
  return 0;
}