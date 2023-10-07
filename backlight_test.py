'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

import RPi.GPIO as GPIO

ledpin = 13				# PWM pin connected to LED

GPIO.setwarnings(True)				# disable warnings
GPIO.setmode(GPIO.BCM)				# set pin numbering system
GPIO.setup(ledpin, GPIO.OUT)


def setbrightness(dutycycle, *args):
	pi_pwm = GPIO.PWM(ledpin, 1000)		# create PWM instance with frequency
	pi_pwm.start(dutycycle)					# start PWM of required Duty Cycle


def donothing():
	pass


if __name__ == '__main__':
	while True:
        pi_pwm = GPIO.PWM(ledpin, 1000)		# create PWM instance with frequency
        pi_pwm.start(100)					# start PWM of required Duty Cycle
