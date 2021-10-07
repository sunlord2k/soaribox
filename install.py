#!/usr/bin/python
from time import sleep
import os
from os.path import exists
from configparser import ConfigParser
import requests

# Read Config files:
config_file = ConfigParser()
config_file.read("/home/pi/soaribox/config_default.ini")
firstboot = not exists('/home/pi/soaribox/config_local.ini')
if not firstboot:
    config_file_local = ConfigParser()
    config_file_local.read("home/pi/soaribox/config_local.ini")


def updateos(self):
    os.system('sudo apt-get update')
    os.system('sudo apt-get upgrade')


def insertdisptoboot(*args):
    print('SOARIBOX: Inserting Modes for Screen')
    boot_file = open('/boot/config.txt', 'a')
    boot_file.write('\nhdmi_force_hotplug=1\n')
    boot_file.write('hdmi_group=2\n')
    boot_file.write('hdmi_mode=87\n')
    boot_file.write('hdmi_cvt=800 480 60 6 0 0 0\n')
    boot_file.write('hdmi_drive=1\n')
    print('SOARIBOX: Finished inserting Screen modes')


def insertwifi(*args):
        # Insert WIFI Details into wpa config
        print('SOARIBOX: Inserting WLAN Config')
        wifiname = str(config_file_local.get('GENERAL', 'wifiname'))
        wifipass = str(config_file_local.get('GENERAL', 'wifipass'))
        with open('/etc/wpa_supplicant/wpa_supplicant.conf') as f:
            if 'network' not in f.read():
                print("SOARIBOX: Inserting wpa supplican data")
                wpa_file = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a')
                wpa_file.write('\nnetwork={\n       ssid="'+wifiname+'"\n       psk="'+wifipass+'"\n       key_mgmt=WPA-PSK\n}')
        print('SOARIBOX: Finished Inserting WLAN Config')


def setupconfigfiles(*args):
    os.system('cp /home/pi/soaribox/config_default.ini /home/pi/soaribox/config_local.ini')


def checkinternet(*ags):
    url = "https://xcsoar.org/"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        inetconnection = True
        print('SOARIBOX: Internetconnection check succesful!')
    except (requests.ConnectionError, requests.Timeout) as exception:
        inetconnection = False
        print('SOARIBOX: Internetconnection check failed!')
    return inetconnection


if firstboot is True:
    print('Here starts the first boot!')
    setupconfigfiles()
    config_file_local = ConfigParser()
    config_file_local.read("home/pi/soaribox/config_local.ini")
    insertdisptoboot()
    # Create empty ssh file to get remote access
    ssh_file = open('/boot/ssh', 'x')
    config_file_local.set('GENERAL', 'firstboot', 'False')
    config_file_local.set('GENERAL', 'secondboot', 'True')
    config_file_local.write(open('/home/pi/soaribox/config_local.ini', 'w'))
    print('SOARIBOX: Written config Files')
    insertwifi()
    print('SOARIBOX: System is going to reboot in 10 seconds')
    sleep(10)
    os.system('sudo shutdown -r now')

secondboot = config_file_local.getboolean('GENERAL', 'secondboot')
if secondboot is True:
    print('Here starts the second boot!')
    if checkinternet() is True:
        updateos()
        url = config_file_local.get('PATHS', 'xcsoarpath')
        r = requests.get(url)
        with open('/home/pi/soaibox/xcsoar.deb', 'wb') as f:
            f.write(r.content)
    config_file_local.set('GENERAL', 'secondboot', 'False')
    config_file_local.write(open('/home/pi/soaribox/config_local.ini', 'w'))
    print('SOARIBOX: System is going to reboot in 10 seconds')
    sleep(10)
    os.system('sudo shutdown -r now')
