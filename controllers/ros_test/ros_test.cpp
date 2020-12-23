#include <sensor_msgs/Image.h>

#include <sensor_msgs/Imu.h>

#include <sensor_msgs/LaserScan.h>

#include <sensor_msgs/NavSatFix.h>

#include <signal.h>

#include <std_msgs/String.h>

#include<tf/transform_broadcaster.h>

#include "ros/ros.h"

 

#include <webots_ros/set_float.h>

#include <webots_ros/set_int.h>

 

#define TIME_STEP 32

#define NMOTORS 4

#define MAX_SPEED 10
 

ros::NodeHandle *n;

static int controllerCount;

static std::vector<std::string> controllerList; 

ros::ServiceClient timeStepClient;

webots_ros::set_int timeStepSrv;
 

static const char *motorNames[NMOTORS] ={"wheel1", "wheel2", "wheel3","wheel4"};//匹配之前定义好的电机name

void updateSpeed() {   
double speeds[NMOTORS];
  
speeds[0] = MAX_SPEED;
speeds[1] = MAX_SPEED;
speeds[2] = MAX_SPEED;
speeds[3] = MAX_SPEED;


 //set speeds
 
for (int i = 0; i < NMOTORS; ++i) {

   
ros::ServiceClient set_velocity_client;
   
webots_ros::set_float set_velocity_srv;
  
set_velocity_client = n->serviceClient<webots_ros::set_float>(std::string("ros_test/")
+ std::string(motorNames[i]) + std::string("/set_velocity"));   
set_velocity_srv.request.value = speeds[i];
set_velocity_client.call(set_velocity_srv);


 }

}//将速度请求以set_float的形式发送给set_velocity_srv




// catch names of the controllers availables on ROS network
void controllerNameCallback(const std_msgs::String::ConstPtr &name) { 
controllerCount++; 
controllerList.push_back(name->data);
ROS_INFO("Controller #%d: %s.", controllerCount, controllerList.back().c_str());

}


void quit(int sig) {

ROS_INFO("User stopped the 'ros_test' node.");

timeStepSrv.request.value = 0; 
timeStepClient.call(timeStepSrv); 
ros::shutdown();
exit(0);
}
 

int main(int argc, char **argv) {
 
std::string controllerName;
 
// create a node named 'ros_test' on ROS network

 
ros::init(argc, argv, "ros_test",
ros::init_options::AnonymousName);

n = new ros::NodeHandle;  
signal(SIGINT, quit);
 
// subscribe to the topic model_name to get the list of availables controllers

ros::Subscriber nameSub = n->subscribe("model_name", 100, controllerNameCallback);

while (controllerCount == 0 || controllerCount <nameSub.getNumPublishers()) {
ros::spinOnce();
ros::spinOnce();
ros::spinOnce();
 } 
ros::spinOnce();
 
timeStepClient = n->serviceClient<webots_ros::set_int>("ros_test/robot/time_step");
timeStepSrv.request.value = TIME_STEP;


// if there is more than one controller available, it let the user choose 
if (controllerCount == 1)   
controllerName = controllerList[0];

else {
  
int wantedController = 0;
  
std::cout << "Choose the # of the controller you want touse:\n";   
std::cin >> wantedController;   
if (1 <= wantedController && wantedController <= controllerCount)
controllerName = controllerList[wantedController - 1];   
else {
     
ROS_ERROR("Invalid number for controller choice.");
    
return 1;
  
}
} 
ROS_INFO("Using controller: '%s'", controllerName.c_str());
 
// leave topic once it is not necessary anymore
 
nameSub.shutdown();
 
// init motors 
for (int i = 0; i < NMOTORS; ++i) {

   
// position，发送电机位置给wheel1-6，速度控制时设置为缺省值INFINITY   
ros::ServiceClient set_position_client;   
webots_ros::set_float set_position_srv;   
set_position_client = n->serviceClient<webots_ros::set_float>(std::string("ros_test/")
+ std::string(motorNames[i]) + std::string("/set_position"));   
set_position_srv.request.value = INFINITY;
if (set_position_client.call(set_position_srv) &&
set_position_srv.response.success)     
ROS_INFO("Position set to INFINITY for motor %s.",
motorNames[i]);   
else     
ROS_ERROR("Failed to call service set_position on motor %s.",
motorNames[i]);

    
// speed，发送电机速度给wheel1-6   
ros::ServiceClient set_velocity_client;
webots_ros::set_float set_velocity_srv;   
set_velocity_client =
n->serviceClient<webots_ros::set_float>(std::string("ros_test/")
+ std::string(motorNames[i]) + std::string("/set_velocity"));   
set_velocity_srv.request.value = 0.0;   
if (set_velocity_client.call(set_velocity_srv) &&
set_velocity_srv.response.success == 1)     
ROS_INFO("Velocity set to 0.0 for motor %s.", motorNames[i]);   
else     
ROS_ERROR("Failed to call service set_velocity on motor %s.",
motorNames[i]);
}   
updateSpeed();
 
// main loop 
while (ros::ok()) {   
if (!timeStepClient.call(timeStepSrv) || !timeStepSrv.response.success)
{  
ROS_ERROR("Failed to call service time_step for next step.");     
break;   
}   
ros::spinOnce();
} 
timeStepSrv.request.value = 0;
timeStepClient.call(timeStepSrv);
ros::shutdown(); 
return 0;

}