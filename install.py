#!/usr/bin/python
from time import sleep
import os
from configparser import ConfigParser

#Read Config File:
config_file = ConfigParser()
config_file.read("/home/pi/soaribox/config.ini")
firstboot = config_file.getboolean('GENERAL', 'firstboot')

if firstboot is True:
    boot_file = open('/boot/config.txt', 'a')
    boot_file.write('\nhdmi_force_hotplug=1\n')
    boot_file.write('hdmi_group=2\n')
    boot_file.write('hdmi_mode=87\n')
    boot_file.write('hdmi_cvt=800 480 60 6 0 0 0\n')
    boot_file.write('hdmi_drive=1\n')

    wpa_file = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a')
    wlannetzwerkname = '1504'
    wlanpasswort = '1234567890'
    wpa_file.write('\nnetwork={\n       ssid="'+wlannetzwerkname+'"\n       psk="'+wlanpasswort+'"\n       key_mgmt=WPA-PSK\n}')

    config_file.set('GENERAL', 'firstboot', 'False')
    config_file.write(open('/home/pi/soaribox/config.ini', 'w'))
    sleep(1)
    os.system('sudo shutdown -r now')
