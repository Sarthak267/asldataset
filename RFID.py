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
import sqlite3




cred=credentials.Certificate('/home/kali/ACIC/ACIC.json')
firebase_admin.initialize_app(cred,{ 'databaseURL':'https://acic-7e587-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
WIDTH = 128
HEIGHT = 64
I2C_ADDR = 0x3C
i2c = busio.I2C(3,2)

# Initialize the OLED display
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=I2C_ADDR)


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
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)


def inValidCardLed():
    GPIO.output(ledpinRed,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(ledpinRed,GPIO.LOW)
    time.sleep(1)
    GPIO.output(ledpinRed,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(ledpinRed,GPIO.LOW)
    print('led off')
def turnOnLed():
     GPIO.output(solonoid,GPIO.HIGH)
     GPIO.output(ledpinGreen,GPIO.HIGH)
     print('LEd on')
     time.sleep(4)
     GPIO.output(ledpinGreen,GPIO.LOW)
     GPIO.output(solonoid,GPIO.LOW)




GPIO.output(ledpinGreen,GPIO.LOW)
def checkInternet():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ledpinWhite,GPIO.OUT)
    try:
        response=requests.get("https://www.google.com")
        if response.status_code==200:
            print("internet is connected")
            draw.text((0, 0), "Connected", font=font, fill=255)
            draw.text((0,10),'plade your card',font=font, fill=255)
            oled.fill(0)
            oled.image(image)
            oled.show()

            GPIO.output(ledpinWhite,GPIO.HIGH)

            return True
            
    except requests.ConnectionError:
        GPIO.output(ledpinWhite,GPIO.LOW) 
        print ("internet is not accessible")
        oled.fill(0)
        image1 = Image.new("1", (oled.width, oled.height))
        draw1 = ImageDraw.Draw(image1)
        draw1.text((0, 10), "No Internet", font=font, fill=255)
        oled.image(image1)
        oled.show()
        return False 

reference=''

def OLED():
                global text
                global uid
        # Create blank image for drawing
                print(str(text))
        # Display card info on OLED
                draw.text((0, 40), str(text), font=font, fill=220)

                oled.image(image)
                oled.show()
                time.sleep(2)
                oled.fill(0)
                oled.show()
def UIDExists():

    global uid,text,reader
    uid,text=reader.read()
    #print(f"'{text}'",type(text),repr(text))
    global ref
    global valid
    
    if not text or text.isspace()or set(text)=={'\x00'}:
        print('card is not registered')
        inValidCardLed()
          
        valid=False


    else:
    
            print('in else block')
            try:
                data=func_timeout(3,ref.child(str(uid) + str(text)).get)
                if data:
                    print('card is valid')
                    valid=True
                else:
                    print('card is not valid')
                    valid=False
                    inValidCardLed()
        
            except FunctionTimedOut:
                    print('data fetch nahi ho paya')
        
                    valid=False 

            except UnavailableError:
                print('firebase connect nahi ho paya -_-')
                valid=False
            except Exception as e:
                print(str(e) , 'while fetching data')
                valid=False






def readRFID():
    print(valid,"entered reader block")
    global uid,text
    
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    ref= db.reference('/Members/'+str(uid)+str(text))
    print(text)
   
    try:
        reference=ref.child('boardingTime').push(timestamp)
        if reference.key:
            turnOnLed()
            print('buzzz')
            GPIO.output(buzzer,GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(buzzer,GPIO.LOW)
            OLED()
            updateLocalStorage()                                
    
        print(uid,timestamp)
    except Exception as e:
        print(str(e),'rfid read block error')
localDbPath='localStorage.db'

def createLocalDb():
    conn=sqlite3.connect(localDbPath)
    cursor=conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS local_data(
                        uid TEXT PRIMARY KEY,
                        timestamp TEXT)''')
    conn.commit()
    conn.close()

def updateLocalStorage():
    global uid,localDbPath

    conn=sqlite3.connect(localDbPath)
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor=conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO local_data VALUES (?, ?)',(uid,timestamp))
        conn.commit()
        
    except EXception as e:
        print(f"Error updating local storage:{str(e)}")
    finally:
        conn.close()
def run():
    
        createLocalDb()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(buzzer,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(solonoid,GPIO.OUT,initial=GPIO.LOW)
        
        GPIO.setup(ledpinRed,GPIO.OUT)
        GPIO.setup(ledpinGreen,GPIO.OUT)
        
        
        #draw.text((0, 20), "Place your card:", font=font, fill=255)
        print('now place your RFID')
        UIDExists()
        if valid:
            try:
                func_timeout(8,readRFID)
                

            except FunctionTimedOut:
                print('time out ho gya')

            finally:
                    GPIO.output(ledpinGreen,GPIO.LOW)
                    GPIO.cleanup()


while True:
    GPIO.setmode(GPIO.BCM)

    if checkInternet():
        run()
