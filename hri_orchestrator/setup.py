import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'hri_orchestrator'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='V01D',
    maintainer_email='tu_correo@ejemplo.com',
    description='Orquestador con arbol de comportamiento py_trees (HRI)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'task_orchestrator_node = hri_orchestrator.task_orchestrator_node:main',
        ],
    },
)
