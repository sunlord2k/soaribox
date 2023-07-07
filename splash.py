#!/usr/bin/env python

import os
import time
for i in range(1, 54, 1):
	os.system('/usr/bin/fim /home/pi/soaribox/graphics/progress_00'+ str(i) +'.png &')
	sleep(1)
	os.system('/usr/bin/killall fim')
