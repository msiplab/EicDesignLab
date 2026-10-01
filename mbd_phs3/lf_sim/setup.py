from glob import glob
from setuptools import setup

package_name = 'lf_sim'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
        # コース画像はリポジトリの images フォルダから取り込む
        ('share/' + package_name + '/images', ['../../images/course2025.png']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shogo MURAMATSU',
    maintainer_email='shogo@eng.niigata-u.ac.jp',
    description='ライントレーサの ROS 2 シミュレータ（電子情報通信設計製図）',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'body = lf_sim.body_node:main',
            'controller = lf_sim.controller_node:main',
        ],
    },
)
