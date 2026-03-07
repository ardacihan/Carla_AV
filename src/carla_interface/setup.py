from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'carla_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/carla_interface']),
    ('share/carla_interface', ['package.xml']),
    (os.path.join('share', 'carla_interface', 'launch'),
        glob('launch/*.py')),   
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='arda',
    maintainer_email='arda@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'interface_node = carla_interface.interface_node:main',
        ],
    },
)
