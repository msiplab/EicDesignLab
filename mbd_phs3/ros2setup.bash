#!/bin/bash -e
#
# ROS 2 Jazzy Jalisco のインストール（Ubuntu 24.04，Windows の WSL2 を想定）
#
#   $ bash ros2setup.bash
#
# 「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

if [ $EUID -eq 0 ]; then
    echo "このスクリプトは root で実行しないでください" 1>&2
    exit 1
fi

. /etc/os-release
if [ "${VERSION_CODENAME}" != "noble" ]; then
    echo "Ubuntu 24.04 (noble) 用のスクリプトです（現在: ${PRETTY_NAME}）" 1>&2
    exit 1
fi

if ! locale | grep -qi "utf-8"; then
    echo "警告: UTF-8 のロケールが設定されていません" 1>&2
fi

# universe リポジトリと必要なツール
sudo apt update
sudo apt install -y software-properties-common curl
sudo add-apt-repository -y universe

# ROS 2 の apt リポジトリの設定（ros2-apt-source パッケージ）
if dpkg -s ros2-apt-source > /dev/null 2>&1; then
    echo "ros2-apt-source found."
else
    ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
    curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.${VERSION_CODENAME}_all.deb"
    sudo dpkg -i /tmp/ros2-apt-source.deb
fi

# ROS 2 Jazzy（デスクトップ版）と開発ツール，シミュレータが使うモジュール
sudo apt update
sudo apt -y upgrade
sudo apt install -y ros-jazzy-desktop ros-dev-tools python3-numpy python3-scipy python3-pil python3-pytest

# 端末を開いたときに ROS 2 の環境を読み込む
SETUPLINE="source /opt/ros/jazzy/setup.bash"
if grep -qxF "${SETUPLINE}" ~/.bashrc; then
    echo "${SETUPLINE} found."
else
    echo "${SETUPLINE}" >> ~/.bashrc
fi

echo ""
echo "インストールが完了しました．新しい端末を開くか，source ~/.bashrc を実行してください．"
