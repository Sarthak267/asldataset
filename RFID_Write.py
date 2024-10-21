import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
reader=SimpleMFRC522()
try:
	print('enter user credential')
	text=input('put text')
	reader.write(text)
    
finally:
	GPIO.cleanup()
