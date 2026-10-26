import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'hri_audio'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'sounds'), glob('sounds/*.wav')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='V01D',
    maintainer_email='tu_correo@ejemplo.com',
    description='Captura de microfono y parlante (HRI)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'audio_capture_node = hri_audio.audio_capture_node:main',
            'speaker_node = hri_audio.speaker_node:main',
        ],
    },
)
