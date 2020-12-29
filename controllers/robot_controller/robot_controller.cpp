#include <webots/Robot.hpp>
#include "ground_robot.hpp"
#include <chrono>

using namespace webots;
using namespace std::chrono;

int main(int argc, char **argv)
{
  milliseconds ms = duration_cast<milliseconds>(
      system_clock::now().time_since_epoch());

  GroundRobot *robot = new GroundRobot();
  srand(std::hash<std::string>{}(robot->GetName()) + ms.count());
  robot->Run();
  delete robot;
  return 0;
}
