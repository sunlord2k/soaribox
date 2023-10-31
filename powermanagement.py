#!/usr/bin/python
# -*- coding:utf-8 -*-
import smbus
import time
import psutil
import os
from librarys.udpsend import send_udp

address = 0x61
pressed = 0
UDP_IP = "127.0.0.1"
UDP_PORT = 4353


def is_process_running(name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == name:
            return True
    return False


def safepressed(p):
    f = open("keypressed.txt", "w")
    f.write(p)
    f.close()


def donothing():
    pass


def readbus():
    time.sleep(1)
    busreading = hex(bus.read_byte(address))
    if busreading == "0x34":
        os.system('sudo halt -p')
    else:
        print('Received' + busreading)


bus = smbus.SMBus(1)
while True:
    try:
        readbus()
    except Exception as e:
        print("Function errored out!", e)
        print("Retrying ... ")
