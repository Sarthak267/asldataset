import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import time

# Define OLED display parameters
WIDTH = 128
HEIGHT = 64
I2C_ADDR = 0x3C  # I2C address (adjust if necessary)

# Initialize I2C communication
i2c = busio.I2C(3,2)

# Initialize the OLED display
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=I2C_ADDR)

# Initialize the RFID reader
reader = SimpleMFRC522()

# Clear the display
oled.fill(0)
oled.show()
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
x=oled.width
try:
    while True:
        
        # Scan for RFID cards
        id, text = reader.read()

        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)


        # Clear OLED display
        
        oled.fill(0)
        # Create blank image for drawing
        print(str(text))
        # Display card info on OLED
        draw.text((0, 0), "Card ID:", font=font, fill=255)
        draw.text((0,10), str(id), font=font, fill=255)
        draw.text((0, 20), "Card Data:", font=font, fill=255)
        draw.text((0, 40), str(text), font=font, fill=220)

        oled.image(image)
        oled.show()



        time.sleep(0.1)  # Wait for 2 seconds before scanning the next card

except KeyboardInterrupt:
    GPIO.cleanup()
