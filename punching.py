import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import requests   
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin.exceptions import UnavailableError
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from func_timeout import func_timeout, FunctionTimedOut





cred=credentials.Certificate('/home/kali/ACIC/ACIC.json')
firebase_admin.initialize_app(cred,{ 'databaseURL':'https://acic-7e587-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
WIDTH = 128
HEIGHT = 64
I2C_ADDR = 0x3C
i2c = busio.I2C(3,2)

# Initialize the OLED display
oled1 = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=I2C_ADDR)


uid,text='',''
valid=True
solonoid=27
buzzer=13
ledpinWhite=21
ledpinRed=6
ledpinGreen=5

reader = SimpleMFRC522()
ref=db.reference('/Members')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(solonoid,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(ledpinWhite,GPIO.OUT)
GPIO.setup(ledpinRed,GPIO.OUT)
GPIO.setup(ledpinGreen,GPIO.OUT)
image = Image.new("1", (oled1.width, oled1.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)



GPIO.output(ledpinGreen,GPIO.LOW)

def check_internet():
    try:
        response = requests.get("https://www.google.com")
        if response.status_code == 200:
            print("Internet is connected")
            update_oled("Connected", "Place your card")
            GPIO.output(ledpinWhite, GPIO.HIGH)
            return True
    except requests.ConnectionError:
        print("Internet is not accessible")
        GPIO.output(ledpinWhite, GPIO.LOW)
        update_oled("No Internet")
        return False

def update_oled(line1, line2=""):
    oled1.fill(0)
    draw.text((0, 0), line1, font=font, fill=255)
    draw.text((0, 10), line2, font=font, fill=255)
    oled1.image(image)
    oled1.show()

def in_valid_card_led():
    GPIO.output(ledpinRed, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(ledpinRed, GPIO.LOW)

def turn_on_led():
    GPIO.output(ledpinGreen, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(ledpinGreen, GPIO.LOW)

def oled():
    global text
    global uid
    print(str(text))
    draw.text((0, 40), str(text), font=font, fill=220)
    oled1.image(image)
    oled1.show()
    time.sleep(2)
    oled1.fill(0)
    oled1.show()

def uid_exists():
    global uid, text
    uid, text = reader.read()
    if not text or text.isspace() or set(text) == {'\x00'}:
        print('Card is not registered')
        in_valid_card_led()
        return False
    else:
        try:
            data = func_timeout(3, ref.child(str(uid) + str(text)).get)
            if data:
                print('Card is valid')
                return True
            else:
                print('Card is not valid')
                in_valid_card_led()
                return False
        except FunctionTimedOut:
            print('Data fetch timeout')
            return False

def read_rfid():
    global uid, text
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reference = ref.child('Members/' + str(uid) + str(text)).child('boardingTime').push(timestamp)
    if reference.key:
        turn_on_led()
        print('Buzz')
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(buzzer, GPIO.LOW)
        oled()

def run():
    GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(solonoid, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ledpinRed, GPIO.OUT)
    GPIO.setup(ledpinGreen, GPIO.OUT)
    print('Now place your RFID')
    if check_internet():
        if uid_exists():
            try:
                func_timeout(8, read_rfid)
            except FunctionTimedOut:
                print('Timeout occurred')

while True:
    run()
