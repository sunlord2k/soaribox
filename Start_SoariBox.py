#!/usr/bin/env python
from time import sleep
import Menu as menu
import datahandler as datahandler
import os
import threading
import backlight_control as backlight_control


def startxcsoar(*args):
    os.system('/usr/bin/xcsoar -fly')


def startmenux(*args):
    if os.uname()[4][:3] == 'aar':
        os.system('sudo xinit /usr/bin/python3 /home/pi/soaribox/Menu.py ')
        os.system('/usr/bin/vlc /home/pi/soaribox/graphics/output.mp4 --no-osd vlc://quit')
    else:
        os.system('sudo /usr/bin/python3 /home/steffen/gits/soaribox/Menu.py ')


startmenux()
startdatahandler = threading.Thread(target=datahandler.starthandler)
startdatahandler.start()
startbacklight = threading.Thread(target=backlight_control.main)
startbacklight.start()
startxcsoar()
# os.system('/usr/bin/X11/X -nolisten tcp -dpi 96 :0 > /dev/null 2>&1')
# sleep(10)
# menu.loadconfig()
# menu.startmenu()
# xcsoar = threading.Thread(target=startxcsoar, args=(0,))
# xcsoar.start()

print('This is just a test!')
