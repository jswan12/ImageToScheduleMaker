import uuid
import json
import random
import pytesseract
import os
import requests
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image
from bs4 import BeautifulSoup

def generate_color():
    color = "#{:02x}{:02x}{:02x}".format(*map(lambda x: random.randint(0, 255), range(3)))
    while(color in listOfColorsUsed):
        color = "#{:02x}{:02x}{:02x}".format(*map(lambda x: random.randint(0, 255), range(3)))
    listOfColorsUsed.append(color)
    return color

def createCourse(titleOfCourse, startTime, endTime, weekdays, courseType = "", instructor = "", location = ""):
    var = int(startTime[0]) if int(startTime[0]) >= 7 else int(convertToPM(startTime[0]))
    course = {
        "uid":str(uuid.uuid4()),
        "type":"Course",
        "title":str(titleOfCourse),
        "meetingTimes":[{
            "uid":meetingTimesUID,
            "courseType":str(courseType),
            "instructor":str(instructor),
            "location":str(location),
            "startHour":var,
            "endHour":int(convertToPM(endTime[0])) if int(endTime[0]) < var else int(endTime[0]),
            "startMinute":int(startTime[1]),
            "endMinute":int(endTime[1])
            ,
            "days":weekdays
        }],
    "backgroundColor":generate_color()
    }
    return course

def createJSON(title, listOfItems):
    data = {
        "dataCheck":"69761aa6-de4c-4013-b455-eb2a91fb2b76",
        "saveVersion":4,
        "schedules":[{
            "title":title,
            "items":listOfItems
        }],
        "currentSchedule":0
        }
    return data

def generateFullLocationString(text):
    location = ""
    for word in range(len(text)):
        location += " " + text[word]
    return location

def getWeekdays(text):
    weekdays = {"monday":False, "tuesday":False, "wednesday":False, "thursday":False, "friday":False, "saturday":False, "sunday":False}
    text = text.lower()
    for c in range(len(text)):
        if(text[c] == 'm'):
            weekdays['monday'] = True
            continue
        elif(text[c] == 't'):
            if(text[c+1] == 'h'):
                weekdays['thursday'] = True
                continue
            weekdays['tuesday'] = True
            continue
        elif(text[c] == 'w'):
            weekdays['wednesday'] = True
            continue
        elif(text[c] == 'f'):
            weekdays['friday'] = True
            continue
        elif(text[c] == 's'):
            weekdays['saturday'] = True
            continue
        elif(text[c] == 'u'):
            weekdays['sunday'] = True
            continue
        else:
            if(text[c].isdigit()):
                text[c] = 'M'
                weekdays['monday'] = True
            continue
    return weekdays

def createPropertiesDictionary(item):
    propObj = {
        "code":item[0]+" "+item[1],
        "startTime":splitHourAndMinutes(item[4]),
        "endTime":splitHourAndMinutes(item[5]),
        "days":getWeekdays(item[6]),
        "location":generateFullLocationString(item[7:]) if len(item) > 7 else ""
    }
    return propObj

def convertToPM(hour):
    switcher = {
        "1": "13",
        "2": "14",
        "3": "15",
        "4": "16",
        "5": "17",
        "6": "18",
        "7": "19",
        "8": "20",
        "9": "21",
        "10": "22",
        "11": "23",
        "12": "24"
    }
    return switcher.get(hour)

def splitHourAndMinutes(time):
    split = []
    if(len(time) == 4):
        split.append(time[:2])
        split.append(time[2:])
    else:
        split.append(time[0])
        split.append(time[1:])
    return split

##############################################################
#MAIN PROGRAM
##############################################################
print("( I ) to read from an image\n( W ) to web-scrape\nSelection: ")
menuChoice = input().upper()
while(True):
    if menuChoice == "I":
        Tk().withdraw()
        filename = askopenfilename(initialdir = os.getcwd(),title = "Select image",filetypes = (("jpeg files","*.jpg"),("png files","*.png"),("all files","*.*")))
        #if(filename..find(".jpg") != -1 or filename.find(".png") != -1):
        image = pytesseract.image_to_string(Image.open(filename)).upper()

        meetingTimesUID = str(uuid.uuid4())
        startIndex = image.find("ROOM")
        endIndex = image.find("TOTAL")
        listOfCourses = []
        properties = []
        listOfColorsUsed = []
        
        if(startIndex != -1 and endIndex != -1):
            image = image[startIndex+4:endIndex].strip()
            image = image.split("\n")

            for f in range(len(image)-1):
                if(image[f] == ""):
                    for i in range(len(image)-2):
                        image[f+i] = image[(f+i)+1]
                    image.remove(image[len(image)-1])
                if(image[f].find(" __ ") != -1):
                    image[f] = image[f].replace(" __ ", " ")
                if(image[f].find(" = ") != -1):
                    image[f] = image[f].replace(" = ", " ")
                properties.append(image[f].split(" "))
                properties[f] = createPropertiesDictionary(properties[f])
                listOfCourses.append(createCourse(properties[f].get('code'), properties[f].get('startTime'), properties[f].get('endTime'), properties[f].get('days'), "", "", properties[f].get('location')))   
            
            data = createJSON(input("Enter in a title for your schedule: "), listOfCourses)
            
            try:
                with open("schedule.csmo", "w") as write_file:
                    json.dump(data, write_file)
                    print("File has been created and saved to " + os.getcwd() + " as " + "\"schedule.csmo\"\n")
                    break
            except:
                print("\nError when creating .csmo file.")
        else:
            print("Error reading from image.")
        #else:
            print("Invlaid file type.\nPlease select a .jpg or .png file")
    elif menuChoice == "W":
        print("running web scrape")
        page = requests.get("https://myproxy01.apps.lsu.edu/reg/Schedule.nsf/(NoteID)/")
        print(page.text)
        #soup = BeautifulSoup(page.text, 'html.parser')
        #print(soup.find_all('p'))
        #print(soup.prettify())
        break
    else:
        print("( I ) to read from an image\n( W ) to web-scrape\nSelection: ")
        menuChoice = input().upper()

