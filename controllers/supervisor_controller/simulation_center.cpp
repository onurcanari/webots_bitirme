#include <vector>
#include <webots/Supervisor.hpp>
#include <webots/Emitter.hpp>

#include "models/location_limit.hpp"
#include "models/mine.hpp"
#include "models/robot.hpp"

using namespace std;

class SimulationCenter : Supervisor
{
private:
    Supervisor *supervisor;
    const int TIME_STEP = 64;
    int mine_count = 0;
    Emitter *emitter;
    Node *robot;

public:
    int foundMineCount = 0;
    vector<GroundRobot *> ground_robots;
    vector<GroundMine *> ground_mines;
    string message;

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
                        cout << robot->robot_name;
                        cout << " found " << mine->mine_name << " at " << *(mine->location) << endl;
                    }
                }
            }
            i++;
        }
    }
        void locationControl(){
        for(auto robot : ground_robots){
            if(robot->robot_name == "robot0"){
                if(robot->GetLocation().z > 1.8){
                    sendMessage("turnRight",(robot->message).c_str(),(int)(robot->channel));
                    robot->message = "turnRight";
                }
                else if(robot->GetLocation().z <1){
                    sendMessage("turnLeft",(robot->message).c_str(),(int)(robot->channel));
                    robot->message = "turnLeft";
                }
            }
            else if(robot->robot_name == "robot1"){
                if(robot->GetLocation().z > 0.8){
                    sendMessage("turnRight",(robot->message).c_str(),(int)(robot->channel));
                    robot->message = "turnRight";
                }
                else if(robot->GetLocation().z < 0){
                    sendMessage("turnLeft",(robot->message).c_str(),(int)(robot->channel));
                    robot->message = "turnLeft";
                }
            }
            else if(robot->robot_name == "robot2"){
                if(robot->GetLocation().z > -0.1){
                    sendMessage("turnRight",(robot->message).c_str(),(int)(robot->channel));
                    robot->message = "turnRight";
                }
                else if(robot->GetLocation().z < -1){
                    sendMessage("turnLeft",(robot->message).c_str(),(int)(robot->channel));
                    robot->message = "turnLeft";
                }
            }
            else if(robot->robot_name == "robot3"){
                if(robot->GetLocation().z > -1.1){
                    sendMessage("turnRight",(robot->message).c_str(),(int)(robot->channel));
                    robot->message = "turnRight";
                }
                else if(robot->GetLocation().z < -1.8){
                    sendMessage("turnLeft",(robot->message).c_str(),(int)(robot->channel));
                    robot->message = "turnLeft";
                }
            }

        }
    }
    void sendMessage(string _message, string pre_message, int _channel){
        message.assign(_message);
        if(!message.empty()){
            if(message != pre_message){
                cout << _message << " geldi... " << endl; 
                emitter->setChannel(_channel);
                emitter->send(message.c_str(), (int)strlen(message.c_str()) + 1);
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
            locationControl();
        }
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
    emitter->setChannel(0);
    char buffer[20];

    Location map_start = Location(2, 0, -2);

    Location *offset = new Location(0, 0, 1);
    Location temp_lower = map_start.Clone();
    Location temp_upper = temp_lower;

    LocationLimit *robot_loc_limit;

    for (int i = 0; i < robot_count; i++)
    {
        temp_upper = temp_lower.Add(offset);
        robot_loc_limit = new LocationLimit(&temp_upper, &temp_lower);
        sprintf(buffer, "robot%d", i);
        auto robot = new GroundRobot(this, string(buffer), robot_loc_limit);
        robot->channel = i;
        AddRobot(robot);
        temp_lower = temp_upper;
    }

    for (int i = 0; i < mine_count; i++)
    {
        sprintf(buffer, "mine%d", i);
        auto mine = new GroundMine(this, string(buffer));
        AddMine(mine);
    }
}

SimulationCenter::~SimulationCenter()
{
}
