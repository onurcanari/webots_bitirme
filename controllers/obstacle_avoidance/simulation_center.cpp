#include <vector>
#include <webots/Supervisor.hpp>
#include <webots/Emitter.hpp>

#include "models/location_limit.hpp"
#include "models/mine.hpp"
#include "models/robot.hpp"

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
    Emitter *emitter;
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

    // her robotoun konumunu günceller
    void UpdateRobots()
    {
        for (auto robot : ground_robots)
        {
            robot->Update();
        }
    }

    // her robotun konumu ile diğer mayınların konumunu karşılaştırır.
    void CalculateDistances()
    {
        int i = 0;
        for (auto robot : ground_robots)
        {
            for (auto mine : ground_mines)
            {
                if (!mine->is_found)
                {
                    bool isClose = robot->GetLocation().IsClose(mine->location);
                    // eğer mayın bulduysa mayını bulundu olarak işaretle ve log yazdır.
                    if (isClose)
                    {
                        foundMineCount++;
                        mine->is_found = true;
                        std::cout << robot->robot_name;
                        std::cout << " found " << mine->mine_name << " at " << *(mine->location) << std::endl;
                    }
                }
            }
            i++;
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

    void SendCommandToRobot(int robot_num)
    {
        this->emitter->setChannel(robot_num);
        // this->emitter->send()
    }
};

SimulationCenter::SimulationCenter(int robot_count, int mine_count)
{
    // verilen mayın ve robot sayısı kadar groundrobot objesi oluşturur. ve hepsini dinamik listeye ekler.
    this->mine_count = mine_count;
    this->emitter = getEmitter("emitter");
    char buffer[20];

    Location map_start = Location(2, 0, -2);
    Location map_end = Location(-2, 0, 2);

    Location *offset = new Location(0, 0, 1);
    Location temp_lower = map_start.Clone();
    Location temp_upper = temp_lower;

    LocationLimit *robot_loc_limit;

    for (int i = 0; i < robot_count; i++)
    {
        temp_upper = temp_lower.Add(offset);
        robot_loc_limit = new LocationLimit(&temp_upper, &temp_lower);
        sprintf(buffer, "robot%d", i);
        auto robot = new GroundRobot(this, std::string(buffer), robot_loc_limit);
        AddRobot(robot);
        temp_lower = temp_upper;
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
