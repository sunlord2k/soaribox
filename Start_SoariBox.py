#!/usr/bin/env python
import Menu as menu
import datahandler as datahandler
import os
import threading


def startxcsoar(*args):
    os.system('/usr/bin/xcsoar')


def startxserver(*args):
    os.system('sudo /usr/bin/X11/X -nolisten tcp -dpi 96 :0 > /dev/null 2>&1')


startxserver()
menu.menustart()
xcsoar = threading.Thread(target=startxcsoar, args=(0,))
xcsoar.start()
# startdatahandler = threading.Thread(target=datahandler.starthandler)
# startdatahandler.start()
print('This is just a test!')
