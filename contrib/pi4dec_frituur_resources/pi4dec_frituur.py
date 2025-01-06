import sys, os
import json
from escpos.printer import Serial
from escpos.printer import Network
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter
from datetime import datetime

debug = True

# Variables
filename = "contrib/pi4dec_frituur_resources/receipt.png"
headerheight = 180
finalRun = False
receiptWidth = 512
printer = "network" #serial or network

# Disable Print
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore Print
def enablePrint():
    sys.stdout = sys.__stdout__

def prepare_receipt(message):
    if debug:
        print("in prepare receipt")
        print(message)
    runs = 0
    totalHeight = 8000
    data = json.loads(message)
    account = data["user"]
    items = data["items"]
    
    while runs<2:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        if(runs): # The first run we create the receipt to determine the length, without a background.
            img = Image.new('RGB', size=(receiptWidth, totalHeight),color='white')
        else:
            img = Image.new('RGB', size=(receiptWidth, totalHeight))
        draw = ImageDraw.Draw(img)
        orderfromfont = ImageFont.truetype("./contrib/pi4dec_frituur_resources/tff/Arialn.ttf", 30)
        nickfont = ImageFont.truetype("./contrib/pi4dec_frituur_resources/tff/ArialNarrowBold.ttf", 50)
        timefont = ImageFont.truetype("./contrib/pi4dec_frituur_resources/tff/Arialn.ttf", 30)
        headerfont = ImageFont.truetype("./contrib/pi4dec_frituur_resources/tff/ArialNarrowBold.ttf", 30)
        font = ImageFont.truetype("./contrib/pi4dec_frituur_resources/tff/Arialn.ttf", 40)

        #if(len(account)>12):  account=account[0:12]

        # Header
        draw.text([0,0],'Bestelling voor:',fill= 'black',font=orderfromfont)
        draw.text([0,40],account,fill= 'black',font=nickfont)
        draw.text([0,headerheight-80],current_date + " "+ current_time,fill= 'black',font=timefont)
        draw.text([0,headerheight-40],'Snack',fill= 'black',font=headerfont)
        draw.text([280,headerheight-40],'In Pan  Uitgeleverd',fill= 'black',font=headerfont)
        draw.line((0, headerheight, receiptWidth, headerheight),fill='black',width=3)

        logo = Image.open('contrib/pi4dec_frituur_resources/logo.png')
        img.paste(logo,[receiptWidth - 140,20])

        # Items
        rows = 0
        for item in items:
            extrarow = False
            quantity = str(item["quantity"])
            #itemname = item["description"].split("(Frituur) ",1)[1]
            itemname = item["description"]
            if (quantity > '1'):
                itemname = quantity + "x " + itemname
            if(len(itemname)>20):
                extrarow = True
            draw.text([0,headerheight+(rows*45)],itemname,fill='black',font=font)
            if extrarow:
                rows = rows+1
            draw.rounded_rectangle([280,headerheight+(rows*45)+10,310,headerheight+(rows*45)+40],5,'white','black',3)
            '''draw.rounded_rectangle([370,headerheight+(rows*45)+10,400,headerheight+(rows*45)+40],5,'white','black',3)
            if "frytime" in item:
                draw.text([maxWidth-10,headerheight+(rows*45)],str(item["frytime"])+"m",fill= 'black',anchor="ra",font=font)
            rows = rows+1'''
            draw.rounded_rectangle([receiptWidth-40,headerheight+(rows*45)+10,receiptWidth-10,headerheight+(rows*45)+40],5,'white','black',3)
            if "frytime" in item:
                draw.text([430,headerheight+(rows*45)],str(item["frytime"])+" min",fill= 'black',anchor="ra",font=font)
            rows = rows+1
        draw = ImageDraw.Draw(img)
        test1,test2,test3,totalHeight = img.getbbox()
        totalHeight = totalHeight + 10
        runs = runs + 1
    img.save(filename, "PNG")

def print_frituur_receipt():
    blockPrint()
    if printer == "serial":
        """ 9600 Baud, 8N1, Flow Control Enabled """
        p = Serial(devfile='/dev/ttyUSB0',
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=1.00,
        dsrdtr=True
        )
    elif printer == "network":
        p = Network("10.33.0.22",profile='TM-T88V')
    enablePrint()
    p.image(filename)
    p.cut()

if len(sys.argv)>1: #print accountname and firstname
    prepare_receipt(sys.argv[1])
    if debug:
        print("Debug enabled: Not printing!")
    else:
        print("\nIk stuur de frituurbestelling naar de printer!\n")
        print_frituur_receipt()
elif debug:
    print("\nDebug enabled, just testing, not printing\n")
    testdata = r'''{"user":"TESTER","items":[{"quantity":11,"description":"Frikandel","product_id":"frikandel","frytime":"4"},{"quantity":2,"description":"Bitterballen 6 stuks","product_id":"bitterballen","frytime":"5"},{"quantity":1,"description":"Patat","product_id":"patat"}]}'''
    prepare_receipt(str(testdata))  
else: #give a nice prompt
    print("So, I was hoping for some JSON, but got none")
