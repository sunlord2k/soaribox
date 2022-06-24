#!/bin/bash
/usr/bin/X11/X -nolisten tcp -dpi 96 :0 > /dev/null 2>&1
DISPLAY=:0 /usr/bin/python3 /home/pi/soaribox/Menu.py
killall Xorg
