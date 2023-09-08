'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

import RPi.GPIO as GPIO
from time import sleep

def setbrightness(tmp,*args):
	ledpin = 13				# PWM pin connected to LED
	GPIO.setwarnings(True)			#disable warnings
	GPIO.setmode(GPIO.BCM)			#set pin numbering system
	GPIO.setup(ledpin,GPIO.OUT)
	pi_pwm = GPIO.PWM(ledpin, 500)		#create PWM instance with frequency
	pi_pwm.start(tmp)				#start PWM of required Duty Cycle
#    pi_pwm.ChangeDutyCycle(0)
#    while True:
#        for duty in range(0,101,1):
#            pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
#            sleep(0.01)
#            print(duty)
#        sleep(0.5)
#
#        for duty in range(100,-1,-1):
#            pi_pwm.ChangeDutyCycle(duty)
#            sleep(0.01)
#            print(duty)
#        sleep(0.5)
if __name__ == '__main__':
	setbrightness(10)
	while True:
		i=0
