from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'IBVS_ROV'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),        
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch')),        
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'lib'), glob('*.py')),                                      
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='mat.guilleray@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
        'exec': [
            'scipy'
        ]
        
    },
    entry_points={
        'console_scripts': [
            'class_BlueRov = IBVS_ROV.Utils.BlueRov.class_BlueRov:main',
            'Image_videoGrabber = IBVS_ROV.Utils.BlueRov.Image_videoGrabber:main',

            'Tester_Command = IBVS_ROV.Testers.Command:main',
            'Tester_Channel_RCIN = IBVS_ROV.Testers.Channel_RCIN:main',
            
            'Image_Tracker = IBVS_ROV.Tracking.ROS.Image_Tracker:main',
            'Image_SelectPoints = IBVS_ROV.Tracking.ROS.Image_SelectPoints:main',
            
            'Controller_Camera = IBVS_ROV.Controller.ROS.Controller_Camera:main',
            'Controller_Frame = IBVS_ROV.Controller.ROS.Controller_Frame:main'
        ],
    },
)
