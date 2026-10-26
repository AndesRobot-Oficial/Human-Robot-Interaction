cmake_minimum_required(VERSION 3.8)
project(hri_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/DialogueState.msg"
  "msg/WorldPerson.msg"
  "msg/WorldContext.msg"
  "srv/PlaySound.srv"
  "srv/RememberGuest.srv"
  "srv/RequestSkill.srv"
  "action/Converse.action"
  "action/LlmChat.action"
  DEPENDENCIES std_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
