#!/usr/bin/python
from time import sleep
import os
from os.path import exists
from configparser import ConfigParser

# Read Config files:
config_file = ConfigParser()
config_file.read("/home/pi/soaribox/config_default.ini")
firstboot = not exists('/home/pi/soaribox/config_local.ini')
print(firstboot)
wifiname = str(config_file.get('GENERAL', 'wifiname'))
wifipass = str(config_file.get('GENERAL', 'wifipass'))


def update(self):
    os.system('sudo apt-get update')
    os.system('sudo apt-get upgrade')


def insertdisptoboot(*args):
    boot_file = open('/boot/config.txt', 'a')
    boot_file.write('\nhdmi_force_hotplug=1\n')
    boot_file.write('hdmi_group=2\n')
    boot_file.write('hdmi_mode=87\n')
    boot_file.write('hdmi_cvt=800 480 60 6 0 0 0\n')
    boot_file.write('hdmi_drive=1\n')
    print('SOARIBOX: Finished inserting Screen modes')


if firstboot is True:
    config_file_local = open('/home/pi/soaribox/config_local.ini', 'x')
    config_file_local = ConfigParser()
    config_file_local.read("home/pi/soaribox/config_local.ini")
    print('SOARIBOX: Inserting Modes for Screen')
    insertdisptoboot()
    print('SOARIBOX: Inserting WLAN Config')
    # Insert WIFI Details into wpa config
    with open('/etc/wpa_supplicant/wpa_supplicant.conf') as f:
        if 'network' not in f.read():
            print("SOARIBOX: Inserting wpa supplican data")
            wpa_file = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a')
            wpa_file.write('\nnetwork={\n       ssid="'+wifiname+'"\n       psk="'+wifipass+'"\n       key_mgmt=WPA-PSK\n}')
    # Create empty ssh file to get remote access
    ssh_file = open('/boot/ssh', 'x')
    config_file_local.add_section('GENERAL')
    config_file_local.set('GENERAL', 'firstboot', 'False')
    config_file_local.write(open('/home/pi/soaribox/config_local.ini', 'w'))
    print('SOARIBOX: Written config Files')
    print('SOARIBOX: System is going to reboot in 10 seconds')
    sleep(10)
    os.system('sudo shutdown -r now')
print('SOARIBOX: This is a test to ee if we see!')
