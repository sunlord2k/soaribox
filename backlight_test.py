#!/usr/bin/python
# -*- coding:utf-8 -*-
import smbus
import time
import psutil
# import os

address = 0x61


def is_process_running(name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == name:
            return True
    return False


def donothing():
    pass


bus = smbus.SMBus(1)
while True:
    time.sleep(1)
    read = hex(bus.read_byte(address))
    print(read)