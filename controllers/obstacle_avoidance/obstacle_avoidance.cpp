#include <webots/Supervisor.hpp>
#include <stdlib.h>
#include <stdio.h>
#include <webots/DistanceSensor.hpp>
#include <webots/Motor.hpp>
#include <webots/Robot.hpp>
#include "models/objects.cpp"
#include "simulation_center.cpp"

#define MINE_COUNT 2
#define ROBOT_COUNT 1

using namespace webots;

int main()
{
  SimulationCenter *simulation_center = new SimulationCenter(ROBOT_COUNT, MINE_COUNT);

  while (simulation_center->MakeStep())
  {
    simulation_center->UpdateRobots();
    simulation_center->CalculateDistances();
  }

  delete simulation_center;

  return 0;
}