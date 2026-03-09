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
            'class_BlueRov = IBVS_ROV.class_BlueRov:main',
            'Tester_IBVS = IBVS_ROV.Tester_IBVS:main',
            'Tester_Command = IBVS_ROV.Tester_Command:main',
            'Tester_Channel_RCIN = IBVS_ROV.Tester_Channel_RCIN:main',
            'Tester_Channel = IBVS_ROV.Tester_Channel:main',
            
            'Image_Tracker = IBVS_ROV.Image_Tracker:main',
            'Image_SelectPoints = IBVS_ROV.Image_SelectPoints:main',
            'Image_videoGrabber = IBVS_ROV.Image_videoGrabber:main',
            

            'Controller_Camera = IBVS_ROV.Controller_Camera:main',
            'Controller_Frame = IBVS_ROV.Controller_Frame:main'
        ],
    },
)
