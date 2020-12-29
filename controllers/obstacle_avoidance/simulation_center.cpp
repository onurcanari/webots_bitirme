#include <vector>
#include <webots/Supervisor.hpp>

class SimulationCenter : Supervisor
{
private:
    Supervisor *supervisor;
    const int TIME_STEP = 64;
    int mine_count = 0;

public:
    int foundMineCount = 0;

    std::vector<GroundRobot *> ground_robots;
    std::vector<GroundMine *> ground_mines;
    SimulationCenter(int robot_count, int mine_count);
    ~SimulationCenter();

    void AddRobot(GroundRobot *ground_robot)
    {
        ground_robots.push_back(ground_robot);
    }

    void AddMine(GroundMine *ground_mine)
    {
        ground_mines.push_back(ground_mine);
    }

    void UpdateRobots()
    {
        for (auto robot : ground_robots)
        {
            robot->Update();
        }
    }

    void CalculateDistances()
    {
        for (auto robot : ground_robots)
        {
            for (auto mine : ground_mines)
            {
                if (!mine->is_found)
                {
                    bool isClose = robot->GetLocation().IsClose(mine->location);
                    if (isClose)
                    {
                        foundMineCount++;
                        mine->is_found = true;
                        std::cout << robot->robot_name;
                        std::cout << " found " << mine->mine_name << " at " << mine->location << std::endl;
                    }
                }
            }
        }
    }

    void Run()
    {
        while (step(TIME_STEP) != -1)
        {
            if (foundMineCount == mine_count)
                break;

            UpdateRobots();
            CalculateDistances();
        }
        simulationQuit(0);
    }
};

SimulationCenter::SimulationCenter(int robot_count, int mine_count)
{
    this->mine_count = mine_count;
    char buffer[20];
    for (int i = 0; i < robot_count; i++)
    {
        sprintf(buffer, "robot%d", i);
        auto robot = new GroundRobot(this, std::string(buffer));
        AddRobot(robot);
    }

    for (int i = 0; i < mine_count; i++)
    {
        sprintf(buffer, "mine%d", i);
        auto mine = new GroundMine(this, std::string(buffer));
        AddMine(mine);
    }
}
SimulationCenter::~SimulationCenter()
{
}
