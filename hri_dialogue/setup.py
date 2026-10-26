import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'hri_dialogue'

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
    description='Gestor de dialogo: /hri/converse y /hri/remember (HRI)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dialogue_manager_node = hri_dialogue.dialogue_manager_node:main',
        ],
    },
)
