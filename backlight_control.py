'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

import RPi.GPIO as GPIO
import time
import os

ledpin = 13				# PWM pin connected to LED
rotary_dt = 4
rotary_clk = 5
rotary_sw = 22
GPIO.setwarnings(True)				# disable warnings
GPIO.setmode(GPIO.BCM)				# set pin numbering system
GPIO.setup(ledpin, GPIO.OUT)
GPIO.setup(rotary_sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rotary_dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rotary_clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def setbrightness(dutycycle, *args):
	pi_pwm = GPIO.PWM(ledpin, 500)		# create PWM instance with frequency
	pi_pwm.start(dutycycle)					# start PWM of required Duty Cycle


def donothing():
	pass


def printstuff():
	os.system('clear')
	print(GPIO.input(rotary_sw))
	print(GPIO.input(rotary_dt))
	print(GPIO.input(rotary_clk))
	time.sleep(0.1)


if __name__ == '__main__':
	setbrightness(10)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	counter = 0
	clkLastState = GPIO.input(clk)
	try:
		while True:
				clkState = GPIO.input(clk)
				dtState = GPIO.input(dt)
				if clkState != clkLastState:
					if dtState != clkState:
						counter += 1
					else:
						counter -= 1
					print counter
				clkLastState = clkState
				sleep(0.01)
	finally:
			GPIO.cleanup()