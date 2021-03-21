#!/usr/bin/env python
import Menu as menu
import datahandler as datahandler
import os
import threading


def startxcsoar(*args):
    os.system('/usr/bin/xcsoar')


xcsoar = threading.Thread(target=startxcsoar, args=(0,))
xcsoar.start()
datahandler.starthandler()
