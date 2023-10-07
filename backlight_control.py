'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

import RPi.GPIO as GPIO
import time

ledpin = 13				# PWM pin connected to LED
rotary_dt = 4
rotary_clk = 5
rotary_sw = 22
GPIO.setwarnings(True)				# disable warnings
GPIO.setmode(GPIO.BCM)				# set pin numbering system
GPIO.setup(ledpin, GPIO.OUT)
GPIO.setup(rotary_sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def setbrightness(dutycycle, *args):
	pi_pwm = GPIO.PWM(ledpin, 500)		# create PWM instance with frequency
	pi_pwm.start(dutycycle)					# start PWM of required Duty Cycle


def donothing():
	pass


def printstuff():
	print(GPIO.input(rotary_sw))
	time.sleep(2)


if __name__ == '__main__':
	setbrightness(10)
	while True:
		donothing()
		printstuff()
