#!/usr/bin/python
# -*- coding:utf-8 -*-
import smbus
import time

address = 0x61

bus = smbus.SMBus(1)
while True:
    bus.write_byte(address, 0x33)
    time.sleep(1)
    read = bus.read_byte(address)
    print(read)
