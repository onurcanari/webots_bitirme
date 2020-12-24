#include <vector>

class SimulationCenter
{
private:
    Supervisor *supervisor;
    const int TIME_STEP = 64;

public:
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

    bool MakeStep()
    {
        return supervisor->step(TIME_STEP) != -1;
    }

    void CalculateDistances()
    {
        for (auto robot : ground_robots)
        {
            for (auto mine : ground_mines)
            {
                if (!mine->is_found)
                {
                    bool isClose = robot->location->IsClose(mine->location);
                    if (isClose)
                    {
                        mine->is_found = true;
                        std::cout << "Buldum\n";
                        std::cout << "x:" << robot->location->x;
                        std::cout << " x:" << mine->location->x << std::endl;
                    }
                }
            }
        }
    }
};

SimulationCenter::SimulationCenter(int robot_count, int mine_count)
{
    supervisor = new Supervisor();
    char buffer[20];
    for (int i = 0; i < robot_count; i++)
    {
        sprintf(buffer, "robot%d", i);
        auto robot = new GroundRobot(supervisor, std::string(buffer));
        AddRobot(robot);
    }

    for (int i = 0; i < mine_count; i++)
    {
        sprintf(buffer, "mine%d", i);
        auto mine = new GroundMine(supervisor, std::string(buffer));
        AddMine(mine);
    }
}

SimulationCenter::~SimulationCenter()
{
    delete supervisor;
}
