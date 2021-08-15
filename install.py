#!/usr/bin/python
from time import sleep
import os
from configparser import ConfigParser

#Read Config File:
config_file = ConfigParser()
config_file.read("/home/pi/soaribox/config.ini")
firstboot = config_file.getboolean('GENERAL', 'firstboot')
wifiname = str(config_file.get('GENERAL', 'wifiname'))
wifipass = str(config_file.get('GENERAL', 'wifipass'))

if firstboot is True:
    print('SOARIBOX: Inserting HDMI Modes for Screen')
    boot_file = open('/boot/config.txt', 'a')
    boot_file.write('\nhdmi_force_hotplug=1\n')
    boot_file.write('hdmi_group=2\n')
    boot_file.write('hdmi_mode=87\n')
    boot_file.write('hdmi_cvt=800 480 60 6 0 0 0\n')
    boot_file.write('hdmi_drive=1\n')
    print('SOARIBOX: Inserting WLAN Config')
    wpa_file = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a')
    wpa_file.write('\nnetwork={\n       ssid="'+wifiname+'"\n       psk="'+wifipass+'"\n       key_mgmt=WPA-PSK\n}')
    ssh_file = open('/boot/ssh', 'w')

    config_file.set('GENERAL', 'firstboot', 'False')
    config_file.write(open('/home/pi/soaribox/config.ini', 'w'))
    print('SOARIBOX: Written config Files')
    sleep(1)
    print('SOARIBOX: System is going to reboot in 10 seconds')
    sleep(10)
#    os.system('sudo shutdown -r now')
