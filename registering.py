import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time 
ledpinGreen=5
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledpinGreen,GPIO.OUT)
GPIO.output(ledpinGreen,GPIO.LOW)

cred=credentials.Certificate('/home/kali/ACIC/ACIC.json')
firebase_admin.initialize_app(cred,{'databaseURL':'https://acic-7e587-default-rtdb.asia-southeast1.firebasedatabase.app/'})
registered=False
ref=db.reference('/Members')
reader = SimpleMFRC522()
def checkIfUIDExists():
    global registered
    uid,text=reader.read()
    if text=='' or text is None:
        print(type(text))

        print(str(uid) + str(text))
        data=ref.child(str(uid)+str(text)).get()
        print("readin from firebase is success")
        if data:
            print("the card is already registered"+ str(uid)+str(text) )
            registered=True
            return True
        
        else :
            print("card is not registered proceed to register")
            registered=False
            return False
    else:
        print('no Id card text found card not registered')
def putRollNumberToIcard():
    print("place your Icard")
    global registered
    if checkIfUIDExists():
        print('card exists')
        print(registered ,'in roll number')
        reRegister=str(input('still wish to register this card'))
        if reRegister=='yes' or reRegister=='Yes':
            print('reRegistering')
            registered=False                                                                      
            print("the roll number bloc")
            print("enter Students roll number")
            rollnumber=int(input())
            print("place your Icard")
            reader.write(str(rollnumber))
            print("success, Proceed to enter student details")

        else:
            return

    else:
        print("the roll number bloc")
        print("enter Students roll number")
        rollnumber=int(input())
        print("place your Icard")
        reader.write(str(rollnumber))
        print("success, Proceed to enter student details")
        return
Data={}
def takingData():

        
    Data['firstName']=input('Enter Student First Name : ')
    Data['lastName']=input('Enter Student Last Name : ')
    Data['contactNumber']=int(input('Enter Student Contact Number : '))
    Data['studentRollNumber']=input('Enter Student Roll Number : ')
    return

studentData={'studentData':Data,'boardingTime':''}
putRollNumberToIcard()
print(registered, 'after decision')
if not registered:
    
    try:

        takingData()
        print('place your I card to complete registeration')
    
        uid, text=reader.read()
        print("uid",uid)
        if text:
            ref.child(str(uid)+str(text)).set(studentData)
            GPIO.output(ledpinGreen,GPIO.HIGH)
            time.sleep(2)
            GPIO.output(ledpinGreen,GPIO.LOW)
        else:
                print("register the ID with roll number first")
    finally :
        GPIO.cleanup()
else:
    print("take a new card")

