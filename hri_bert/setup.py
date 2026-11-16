from setuptools import find_packages, setup

package_name = 'hri_bert'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='V01D',
    maintainer_email='tu_correo@ejemplo.com',
    description='Interprete de ordenes con BERT: objeto y lugar (HRI)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'bert_node = hri_bert.bert_node:main',
        ],
    },
)
