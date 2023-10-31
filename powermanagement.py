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


bus = smbus.SMBus(1)
while True:
    time.sleep(1)
    read = hex(bus.read_byte(address))
    match read:
        case "0x33":
            donothing()
            pressed = 0
            safepressed(pressed)

        case "0x34":
            os.system('sudo halt -p')

        case "p":
            pressed = pressed + 1
            safepressed(pressed)
            send_udp("SoariBox is going to shutdown in..", UDP_IP, UDP_PORT)
