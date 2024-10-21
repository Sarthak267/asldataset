import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
solonoid=27

GPIO.setup(solonoid,GPIO.OUT)
GPIO.output(solonoid,GPIO.HIGH)
time.sleep(5)
GPIO.output(solonoid,GPIO.LOW)
