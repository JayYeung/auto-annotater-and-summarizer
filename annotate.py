import pyautogui
import pytesseract
from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  
import cv2
import re
from english_words import english_words_lower_set
from nltk.corpus import wordnet
import json

#hardcoded start!
start=[[120, 20], [120, 270], [1500, 1000]]
underline=[[1000, 15], [700, 65], [500, 65], [1050, 65], [1030, 175], [1500, 1000]]
highlight=[[920, 15], [660, 65], [880, 65], [1000, 65], [1050, 170], [1500, 1000]]
text=[[920, 15], [660, 65], [770, 70], [1500, 1000]]
arr=[]
img = cv2.imread('screen.png') #random default stuff
hImg, wImg, _ = img.shape #yeah

def hardMove(arr, speed):
    for i in arr: 
        pyautogui.moveTo(i[0], i[1], speed)
        pyautogui.click()

def outlineMove(outline, speed):
    for i in range (len(outline)):
        temp1=arr[outline[i][0]]
        temp2=arr[outline[i][1]]
        points=[temp1[1], temp1[2], temp2[1], temp2[2]] #where the line is gonna go
        pyautogui.moveTo(points[0], points[1])
        pyautogui.dragTo(points[2], points[3], speed)
def meaning(word):
    data = None
    word = word.upper()
    with open('wordbank/D'+word[0]+'.json') as f:
        data = json.load(f)
    res=str(data[word]['MEANINGS']['1'][1])
    #res=res.replace('[', ''); res=res.replace(']', ''); res=res.replace(',', ''); res=res.replace('\'', '')
    #index=res.find(' ')
    #res = res[:index] + ": " + res[index + 1:]
    return(res)
    
def essentialStuff():
    global img; img = cv2.imread('screen.png')
    global hImg, wImg, _ ; hImg, wImg, _ = img.shape
    global arr; arr=[]
    out=pytesseract.image_to_boxes(img)
    
    #create arr: its a conversion from char to where the char is
    for i in out.splitlines():
        i=i.split(' ')
        #if(i[0]=='~'): #weird case
            #continue
        arr.append([i[0], int(i[1]), hImg-int(i[2]), int(i[3]), hImg-int(i[4])])

def underlinePage():
    hardMove(underline, 0.15)

    para=pytesseract.image_to_string(img).split("\n\n")
    paraToArr=[]

    #clean the paragraphs
    for i in range(len(para)):
        new = para[i]
        new = new.replace(" ", "")
        new = new.replace("\t", "")
        para[i] = new.split(".")

    #create paraToArr: a way to convert from para to arr, if term is \n, will have -1 as spot
    spot=0
    print("new page")
    print(para)
    for i in range(len(para)):
        temp=[]
        for j in range(len(para[i])):
            temp2=[]
            for k in range(len(para[i][j])):
                #print(para[i][j][k]) ; print(arr[spot][0])
                if(para[i][j][k]=='\n'):
                    #print("newline")
                    temp2.append(-1)
                    continue
                while(para[i][j][k]!=arr[spot][0]):
                    spot+=1
                temp2.append(spot)
            temp.append(temp2)
        paraToArr.append(temp)

    #noise remover for len<3 (those aren't actually paragraphs)
    for i in para[:]:
        if len(i) < 3:
            para.remove(i)
    for i in paraToArr[:]:
        if len(i) < 3:
            paraToArr.remove(i)

    #outline contains the spots where line needs to be drawn
    outline=[]
    for i in range(len(para)): #iterate by paragraph
        indexes = [x.start() for x in re.finditer('\n', para[i][0])] 
        start = 0
        #print(indexes)
        for j in indexes: #underline each line
            spot1=paraToArr[i][0][start]
            spot2=paraToArr[i][0][j-1]
            outline.append([spot1, spot2])
            start=j+1

        spot1=paraToArr[i][0][start] #underline up to the period
        spot2=paraToArr[i][0][len(para[i][0])-1]
        outline.append([spot1, spot2])
    outlineMove(outline, 1)

def wordsPage():
    hardMove(highlight, 0.15)
    temp=pytesseract.image_to_string(img).replace("\n", "").split(" ")
    para=[]
    for i in temp:
        if(i.lower() in english_words_lower_set):
            para.append(i)
    para = sorted(para, key=len, reverse = True)
    word=para[0] #shortest length word will be the word we define for now
    spot=-1
    print(word)
    for i in range(len(arr)):
        check=True
        for j in word:
            if(arr[i][0]==j):
                i+=1
            else:
                check=False
                break
            if(i>len(arr)):
                break
        if(check):
            spot=i-len(word)
    if(spot==-1):
        print("could not find: ", word)
    else:
        print("found spot: ", spot)
    pyautogui.moveTo(arr[spot][1], arr[spot][2])
    pyautogui.dragTo(arr[spot+len(word)][1], arr[spot+len(word)][2], 1)

    hardMove(text, 0.15)
    pyautogui.moveTo(arr[spot][1], arr[spot][2]-25, 0.5) #go up a little bit
    pyautogui.click()
    definition=meaning(word)
    pyautogui.write(definition, 0.1)
    pyautogui.moveTo(1500, 1000, 0.2)
    pyautogui.click()
    pyautogui.moveTo(1500, 1000, 0.2)
    pyautogui.click()

    
#MAIN STARTS HERE TODO

pyautogui.keyDown("alt")
pyautogui.press("tab")
pyautogui.keyUp("alt")

hardMove(start, 0.15)
for page in range(14): #number of pages
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(r'screen.png')
    essentialStuff()
    underlinePage()
    wordsPage()

    pyautogui.moveTo(800, 500, 0.2)
    pyautogui.scroll(-960) #around the scroll amount for 1 page
    pyautogui.moveTo(1500, 1000, 0.5) #wait for page to update before next screenshot
