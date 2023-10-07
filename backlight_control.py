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


def getrotary(counter):
	global clkLastState
	clkState = GPIO.input(rotary_clk)
	dtState = GPIO.input(rotary_dt)
	if clkState != clkLastState:
		if dtState != clkState:
			counter += 1
		else:
			counter -= 1
		os.system('clear')
		return counter
	clkLastState = clkState
	time.sleep(0.01)


if __name__ == '__main__':
	setbrightness(10)
	clkLastState = GPIO.input(rotary_clk)
	counter = 0.0
	while True:
		pwm = getrotary(counter)
		print(counter)
		# setbrightness(pwm)

