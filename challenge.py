from getpass import getpass
import os
import time
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import http.client
import json
import requests
from PIL import Image
from io import BytesIO
import tensorflow as tf
import numpy
import gdown

numberOfClasses = 128

def startNewGame(token,cookie):
	conn = http.client.HTTPSConnection("www.geoguessr.com")
	payload = json.dumps({
	  "map": "world",
	  "type": "standard",
	  "timeLimit": 0,
	  "forbidMoving": True,
	  "forbidZooming": True,
	  "forbidRotating": False
	})
	headers = {
	  'authority': 'www.geoguessr.com',
	  'accept': '*/*',
	  'accept-language': 'en-US,en;q=0.9',
	  'content-type': 'application/json',
	  'cookie': cookie,
	  'origin': 'https://www.geoguessr.com',
	  'referer': 'https://www.geoguessr.com/maps/world/play',
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
	  'x-client': 'web'
	}
	conn.request("POST", "/api/v3/challenges/"+token, payload, headers)
	res = conn.getresponse()
	data = res.read()
	resString = data.decode("utf-8")
	resString = resString[resString.index("token")+8:]
	token = resString[:resString.index("\"")]
	resString = resString[resString.index("\"rounds\""):]
	resString = resString[resString.index("panoId")+9:]
	panoId = resString[:resString.index("\"")]
	panoId = bytes.fromhex(panoId).decode('utf-8')
	return token, panoId


def makeDirs():
	if not os.path.exists("image"):
		os.makedirs("image")
	for i in range(numberOfClasses):
		if not os.path.exists("image/" + str(i)):
			os.makedirs("image/" + str(i))

def getImageForKey(key):
	img1 = getImage(0,0,2,key)
	img2 = getImage(1,0,2,key)
	img3 = getImage(2,0,2,key)
	img4 = getImage(3,0,2,key)
	img5 = getImage(0,1,2,key)
	img6 = getImage(1,1,2,key)
	img7 = getImage(2,1,2,key)
	img8 = getImage(3,1,2,key)
	fimg = get_concat_h_cut(img1,img2)
	fimg = get_concat_h_cut(fimg,img3)
	fimg = get_concat_h_cut(fimg,img4)
	fimg2 = get_concat_h_cut(img5,img6)
	fimg2 = get_concat_h_cut(fimg2,img7)
	fimg2 = get_concat_h_cut(fimg2,img8)
	finalImage = get_concat_v_cut(fimg,fimg2)
	finalImage.save("image/0/0.png")

def getImage(x,y,zoom,key):
	url = "https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=apiv3&panoid=" + key + "&output=tile&x="\
	+ str(x) + "&y=" + str(y) + "&zoom=" + str(zoom) + "&nbt=0&fover=0"
	response = requests.get(url)
	img = Image.open(BytesIO(response.content))
	return img

def get_concat_h_cut(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, min(im1.height, im2.height)))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_concat_v_cut(im1, im2):
    dst = Image.new('RGB', (min(im1.width, im2.width), im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def getNextMove(token,cookie):
	conn = http.client.HTTPSConnection("www.geoguessr.com")
	payload = ''
	headers = {
	  'authority': 'www.geoguessr.com',
	  'accept': '*/*',
	  'accept-language': 'en-US,en;q=0.9',
	  'content-type': 'application/json',
	  'cookie': cookie,
	  'referer': 'https://www.geoguessr.com/game/' + token,
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
	  'x-client': 'web'
	}
	conn.request("GET", "/api/v3/games/"+token+"?client=web", payload, headers)
	res = conn.getresponse()
	data = res.read()
	resString = data.decode("utf-8")

	if "\"round\":5" in resString and "\"xpProgressions\":" in resString:
		resString = resString[resString.index("\"round\":5")+10:]
		for x in range(5):
			resString = resString[resString.index("\"panoId\"")+10:]
			panoId = resString[:resString.index("\"")]
			panoId = bytes.fromhex(panoId).decode('utf-8')
		resString = data.decode("utf-8")

	resString = resString[resString.rindex("\"totalScore\""):]
	resString = resString[resString.index("\"amount\"")+10:]
	totalScore = resString[:resString.index("\"")]
	totalScore = float(totalScore)

	resString = data.decode("utf-8")

	resString = resString[resString.rindex("\"panoId\"")+10:]
	panoId = resString[:resString.index("\"")]
	panoId = bytes.fromhex(panoId).decode('utf-8')

	return totalScore, panoId

def makeMove(token,cookie,lat,lon):
	conn = http.client.HTTPSConnection("www.geoguessr.com")
	payload = json.dumps({
	  "token": "\"token\"",
	  "lat": lat,
	  "lng": lon,
	  "timedOut": False
	})
	headers = {
	  'authority': 'www.geoguessr.com',
	  'accept': '*/*',
	  'accept-language': 'en-US,en;q=0.9',
	  'content-type': 'application/json',
	  'cookie': cookie,
	  'origin': 'https://www.geoguessr.com',
	  'referer': 'https://www.geoguessr.com/game/' + token,
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
	  'x-client': 'web'
	}
	conn.request("POST", ("/api/v3/games/"+token), payload, headers)
	res = conn.getresponse()

def getChallengeCode(cookie,forbidMoving,forbidRotating,forbidZooming):
	conn = http.client.HTTPSConnection("www.geoguessr.com")
	payload = json.dumps({
	  "map": "world",
	  "forbidMoving": forbidMoving,
	  "forbidRotating": forbidRotating,
	  "forbidZooming": forbidZooming,
	  "timeLimit": 0
	})
	headers = {
	  'authority': 'www.geoguessr.com',
	  'accept': '*/*',
	  'accept-language': 'en-US,en;q=0.9',
	  'content-type': 'application/json',
	  'cookie': cookie,
	  'origin': 'https://www.geoguessr.com',
	  'referer': 'https://www.geoguessr.com/maps/world/play',
	  'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
	  'sec-ch-ua-mobile': '?0',
	  'sec-ch-ua-platform': '"Windows"',
	  'sec-fetch-dest': 'empty',
	  'sec-fetch-mode': 'cors',
	  'sec-fetch-site': 'same-origin',
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
	  'x-client': 'web'
	}
	conn.request("POST", "/api/v3/challenges", payload, headers)
	res = conn.getresponse()
	data = res.read()
	resString = data.decode("utf-8")
	resString = resString[resString.index(":")+2:]
	token = resString[:resString.index("\"")]
	return token

def getCookie(email,password):
	conn = http.client.HTTPSConnection("www.geoguessr.com")
	payload = json.dumps({
	  "email": email,
	  "password": password
	})
	headers = {
	  'authority': 'www.geoguessr.com',
	  'accept': '*/*',
	  'accept-language': 'en-US,en;q=0.9',
	  'content-type': 'application/json',
	  'origin': 'https://www.geoguessr.com',
	  'referer': 'https://www.geoguessr.com/signin',
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
	  'x-client': 'web'
	}
	conn.request("POST", "/api/v3/accounts/signin", payload, headers)
	res = conn.getresponse()
	return res.headers["Set-Cookie"]

def estimate(panoId):
	getImageForKey(panoId) 	
	predictions = model.predict(gg_generator,verbose=0) 
	class_dict=gg_generator.class_indices
	rev_dict={}
	for key, value in class_dict.items():
	  rev_dict[value]=key

	modelPred = numpy.argmax(predictions[0])
	modelPred = rev_dict[modelPred]

	with open("points.csv", "r") as f:
	    lines = f.readlines()
	    line = lines[int(modelPred)]
	    line = line[line.index(",")+1:]
	    lat = float(line[:line.index(",")])
	    lon = float(line[line.index(",")+1:])
	    return lat,lon

def loadModel():
	if not os.path.exists("model"):
		print("downloading model")
		url = "https://drive.google.com/drive/folders/1eDtVBu9Q-uX2WJztRCi3jKlnR67MbuyK?usp=sharing"
		gdown.download_folder(url, use_cookies=False)
		print("download complete")

	return tf.keras.models.load_model('model')

makeDirs()
print('Enter your geoguessr email address:') 
email = input()
password = getpass()
cookie = getCookie(email,password)

target_size = (1024, 2048)
gg_datagen = ImageDataGenerator(1./255)
gg_generator = gg_datagen.flow_from_directory( #todo stop using this
    'image/',
    target_size=target_size
)

model = loadModel()


sleepTime = 0.3 #lower or remove at your own risk, I have gotten suspended before 

totalScore = 0
moves = 0

forbidMoving = True
forbidRotating = False
forbidZooming = True

for i in range(5):
	code = getChallengeCode(cookie,forbidMoving,forbidRotating,forbidZooming)
	time.sleep(sleepTime)
	token, panoId = startNewGame(code,cookie)
	for j in range(4):
		lat, lon = estimate(panoId)
		time.sleep(sleepTime)
		makeMove(token,cookie,lat,lon)
		score,panoId = getNextMove(token,cookie)
	lat, lon = estimate(panoId)
	time.sleep(sleepTime)
	makeMove(token,cookie,lat,lon)
	moves+=1
	score,panoId = getNextMove(token,cookie)
	totalScore += score
	avg = totalScore / moves
	url = "https://www.geoguessr.com/challenge/"+code
	print("final score:",score, url, "\naverage score:",avg, "\ngames played:",(i+1),"\n")