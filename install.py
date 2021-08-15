from time import sleep
import os
from configparser import ConfigParser

#Read Config File:
config_file = ConfigParser()
config_file.read("config.ini")
firstboot = config_file.getboolean('INSTALL', 'firstboot')

if firstboot:
    config_file = open('/boot/config.txt', 'a')
    config_file.write('\nhdmi_force_hotplug=1\n')
    config_file.write('hdmi_group=2\n')
    config_file.write('hdmi_mode=87\n')
    config_file.write('hdmi_cvt=800 480 60 6 0 0 0\n')
    config_file.write('hdmi_drive=1\n')
    config_file['INSTALL']['firstboot']
    with open('config.ini', 'w') as config_file:    # save
        config.write(config_file)
    sleep(1)
    os.system('sudo shutdown -r now')
