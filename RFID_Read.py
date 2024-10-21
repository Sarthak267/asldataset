import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
reader=SimpleMFRC522()

try:
    uid, text=reader.read()
    print(uid,text)
finally:
    GPIO.cleanup()
