import pyautogui
import pytesseract
from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  
import cv2
import re
from english_words import english_words_lower_set
import json
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx

#hardcoded start!
start=[[120, 20], [120, 270], [1500, 1000]]
img = cv2.imread('screen2.png') #random default stuff
hImg, wImg, _ = img.shape #yeah
all=""

def hardMove(arr, speed):
    for i in arr: 
        pyautogui.moveTo(i[0], i[1], speed)
        pyautogui.click()

def essentialStuff():
    global img; img = cv2.imread('screen2.png')
    global hImg, wImg, _ ; hImg, wImg, _ = img.shape
    out=pytesseract.image_to_string(img)
    global all
    all+=out

def read_article(file_name):
  file = open(file_name, 'r') 
  filedata = file.readlines()
  filedata = [x for x in filedata if x != '\n'] 
  filedata = [x.replace('\n',' ') for x in filedata] 
  filedata = ''.join(filedata) 
  filedata = filedata.split('. ') 
  sentences = []
  for sentence in filedata:
    sentences.append(sentence.replace('[^a-zA-Z]', ' ').split(' '))
    
  return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def generate_summary(file_name, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    sentences =  read_article(file_name)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
    print("Indexes of top ranked_sentence order are ", ranked_sentence)    

    for i in range(top_n):
      summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Step 5 - Offcourse, output the summarize texr
    print("Summarize Text: \n", ". ".join(summarize_text))

#MAIN STARTS HERE TODO

pyautogui.keyDown("alt")
pyautogui.press("tab")
pyautogui.keyUp("alt")

hardMove(start, 0.15)
for page in range(14): #number of pages
    myScreenshot = pyautogui.screenshot(region=(0,100,1920,1080))
    myScreenshot.save(r'screen2.png')

    essentialStuff()

    pyautogui.moveTo(800, 500, 0.2)
    pyautogui.scroll(-960) #around the scroll amount for 1 page
    pyautogui.moveTo(1500, 1000, 0.5) #wait for page to update before next screenshot

f = open("article.txt", "w")  
f.write(all)
f.close()

generate_summary( "article.txt", 3)