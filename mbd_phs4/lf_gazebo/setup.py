from glob import glob
from setuptools import setup

package_name = 'lf_gazebo'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/worlds', glob('worlds/*.sdf')),
        ('share/' + package_name + '/models/line_follower', glob('models/line_follower/*')),
        ('share/' + package_name + '/models/lf_course', glob('models/lf_course/model.*')),
        ('share/' + package_name + '/models/lf_course/meshes', glob('models/lf_course/meshes/*')),
        # コース画像はリポジトリの images フォルダから取り込む
        ('share/' + package_name + '/models/lf_course/materials/textures', ['../../images/course2025.png']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shogo MURAMATSU',
    maintainer_email='shogo@eng.niigata-u.ac.jp',
    description='ライントレーサの Gazebo シミュレータ（電子情報通信設計製図）',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'photorefs = lf_gazebo.photoref_node:main',
            'motors = lf_gazebo.motor_node:main',
            'encoders = lf_gazebo.encoder_node:main',
        ],
    },
)
