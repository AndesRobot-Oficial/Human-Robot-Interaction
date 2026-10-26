"""Lanza los 8 nodos de HRI para la prueba 5.1 (modo "reto").

Uso: ros2 launch hri_bringup hri_reto.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def cfg(package: str, file: str) -> str:
    return os.path.join(get_package_share_directory(package), 'config', file)


def node(package: str, executable: str, params: str = '') -> Node:
    return Node(
        package=package, executable=executable, name=executable,
        parameters=[cfg(package, params)] if params else [],
        output='screen', emulate_tty=True)


def generate_launch_description():
    return LaunchDescription([
        node('hri_audio', 'audio_capture_node', 'audio_params.yaml'),
        node('hri_audio', 'speaker_node', 'audio_params.yaml'),
        node('hri_speech', 'asr_node', 'asr_params.yaml'),
        node('hri_speech', 'tts_node', 'tts_params.yaml'),
        node('hri_doorbell', 'doorbell_detector_node', 'doorbell_params.yaml'),
        node('hri_dialogue', 'dialogue_manager_node', 'dialogue_params.yaml'),
        node('hri_llm', 'llm_agent_node', 'llm_params.yaml'),
        node('hri_orchestrator', 'task_orchestrator_node'),
    ])
