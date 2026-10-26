"""Lanza solo el arbol (con stubs) y el gestor de dialogo (con respuestas fijas).

Sirve para probar la parte del orquestador sin audio, LLM ni otros equipos.
Uso: ros2 launch hri_bringup orchestrator_only.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    dialogue_params = os.path.join(
        get_package_share_directory('hri_dialogue'), 'config', 'dialogue_params.yaml')
    return LaunchDescription([
        Node(package='hri_dialogue', executable='dialogue_manager_node',
             name='dialogue_manager_node', parameters=[dialogue_params],
             output='screen', emulate_tty=True),
        Node(package='hri_orchestrator', executable='task_orchestrator_node',
             name='task_orchestrator_node', output='screen', emulate_tty=True),
    ])
