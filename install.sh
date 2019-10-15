#!/bin/sh

sudo apt-get update
sudo apt-get upgrade
sudp apt-get dist-upgrade


#日本語化
sudo apt-get install ttf-kochi-gothic xfonts-intl-japanese xfonts-intl-japanese-big xfonts-kaname
sudo apt-get install jfbterm

#lsusb
sudo apt-get install fswebcam


#PIGPIO
sudo apt install pigpio


#python関係
sudo pip install --upgrade pip
sudo apt-get install python3-pandas
sudo apt-get install python-pandas

#python libインストール
python3 -m pip install configparser
python3 -m pip install transitions
python3 -m pip install scratch
