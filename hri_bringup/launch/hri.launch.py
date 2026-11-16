import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    voz = os.path.join(get_package_share_directory('hri_speech'), 'config', 'voz.yaml')
    simular = LaunchConfiguration('simular')
    iniciar = LaunchConfiguration('iniciar')
    esperar_timbre = LaunchConfiguration('esperar_timbre')
    return LaunchDescription([
        DeclareLaunchArgument('simular', default_value='false'),
        DeclareLaunchArgument('iniciar', default_value='false'),
        DeclareLaunchArgument('esperar_timbre', default_value='true'),
        Node(package='hri_speech', executable='tts_node', name='tts_node',
             parameters=[voz], output='screen'),
        Node(package='hri_speech', executable='stt_node', name='stt_node',
             parameters=[voz], output='screen'),
        Node(package='hri_speech', executable='timbre_node', name='timbre_node',
             parameters=[voz], output='screen'),
        Node(package='hri_llm', executable='llm_node', name='llm_node', output='screen'),
        Node(package='hri_bert', executable='bert_node', name='bert_node', output='screen'),
        Node(package='hri_orchestrator', executable='task_orchestrator_node',
             name='task_orchestrator_node', output='screen',
             parameters=[{'auto_iniciar': iniciar, 'esperar_timbre': esperar_timbre}]),
        Node(package='hri_orchestrator', executable='simulador_equipos', name='simulador_equipos',
             output='screen', condition=IfCondition(simular)),
    ])
