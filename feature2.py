import time
import Image
from PyDictionary import PyDictionary
from collections import deque
import numpy as np
import argparse
import glob
import cv2
from matplotlib import pyplot as plt
import pytesseract
import os
import audio_fn as ad
import enchant
import math

global time
time = time.asctime(time.localtime(time.time()))


rot = 0
z = 0
#low1 = (25, 60, 195)
#high1 = (50, 125, 230)

#low1 = (160,150,100)
# = (180, 255,255)

#low1 = (14, 200, 230)	#orange1
#high1 = (27, 255, 255)

low1 = (5, 140, 150)
high1 = (27, 255, 255)  #orange2

def point_cordinate(): #cordinates of point

	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help="path to the (optional) video file")
	ap.add_argument("-b", "--buffer", type=int, default=32,
		help="max buffer size")
	args = vars(ap.parse_args())

	#low1 = (low1)
	#high1 = (high1)
	 
	# initialize the list of tracked points, the frame counter, and the coordinate deltas
	pts = deque(maxlen=args["buffer"])
	#counter = 0
	(dX, dY) = (100 , 100)
	t=300

	camera = cv2.VideoCapture(0)

	while True:
		(grabbed, frame) = camera.read()		
		if not grabbed:
			break
		# blur it, and convert it to the HSV color space
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	 
		# construct a mask for the color "green", then perform a series of dilations and erosions to remove any small blobs left in the mask
		mask = cv2.inRange(hsv, low1, high1)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)
		cv2.imshow('mask', mask)

		# find contours in the mask and initialize the current (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None
		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)

			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			# only proceed if the radius meets a minimum size
			if radius > 5:
				#update the list of tracked points
				pts.appendleft(center)
		if len(pts)>10 :
			# loop over the set of tracked points
			for i in np.arange(1, len(pts)):
				# if either of the tracked points are None, ignore them
				if pts[i - 1] is None or pts[i] is None:
					continue

				# check to see if enough points have been accumulated in the buffer
				if i == 1 and pts[-10] is not None:
					# compute the difference between the x and y coordinates
					dX = pts[-2][0] - pts[i][0]
					dY = pts[-2][1] - pts[i][1]	
		# show the frame to our screen and increment the frame counter
		cv2.imshow("frame", frame)
		key = cv2.waitKey(1) & 0xFF
		#counter += 1
		t=t-1
		# if the 'q' key is pressed, or if the object slows down, loop is exited and the cropped part is displayed
		if (key == ord('q')) or  (len(pts)>24 and np.abs(dX) < 5 and np.abs(dY) < 5):
			a = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))	 
			break
		if t == 0:
			ad.tts("the corner is not visible")
			t = 250	
	# cleanup the camera and close any open windows
	camera.release()
	cv2.destroyAllWindows()
	return a;

def page_setup():	
	ad.tts("show top left corner")	
	global a
	a = point_cordinate()
	ad.tts("show top right corner")
	global b
	b = point_cordinate()
	ad.tts("show bottom left corner")
	global c
	c = point_cordinate()
	ad.tts("show bottom right corner")
	global d
	d = point_cordinate()
	cv2.destroyAllWindows()
	
def trep_matr():
	
	global p1
	global p2 
	pt1 = np.float32([a,b,c,d])
	dist1 = math.sqrt( (b[0] - a[0])**2 + (b[1] - a[1])**2 )
	dist2 = math.sqrt( (d[0] - c[0])**2 + (d[1] - c[1])**2 )
	p3 = (dist1+dist2)/2
	dist3 = math.sqrt( (c[0] - a[0])**2 + (c[1] - a[1])**2 )
	dist4 = math.sqrt( (b[0] - d[0])**2 + (b[1] - d[1])**2 )
	p4 = (dist3+dist4)/2
	p1 = int(p3)
	p2 = int(p4)
	pt2 = np.float32([[0,0],[p1,0],[0,p2],[p1,p2]])
	#pt2 = np.float32([[0,0],[600,0],[0,900],[600,900]])
	M5 = cv2.getPerspectiveTransform(pt1,pt2)
	#frame2 = cv2.warpPerspective(frame,M5,(600,900))
	return M5;

#Rotate
def rotate(c):
	if c[0] < 300.0 and c[1] < 225.0:		#the values are dependant upon the pixels of the frame
		rot= 1;
		print 2
		return cv2.getRotationMatrix2D((600/2,450/2),90,1);
		
	elif c[0] < 300.0 and c[1] >= 225.0:
		rot= 2;
		print 2
		return cv2.getRotationMatrix2D((600/2,450/2),0,1);

	elif c[0] >= 300.0 and c[1] < 225.0:
		rot=3;
		print 2
		return cv2.getRotationMatrix2D((600/2,450/2),180,1);

	elif c[0] >= 300.0 and c[1] >= 225.0:
		rot=4;
		print 2
		return cv2.getRotationMatrix2D((600/2,450/2),270,1);
	# cleanup the camera and close any open windows
	camera.release()
	cv2.destroyAllWindows()
	return;

#Crop
def crop (M2,M5,picno):
	
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help="path to the (optional) video file")
	ap.add_argument("-b", "--buffer", type=int, default=32,
		help="max buffer size")
	args = vars(ap.parse_args())

	
	# initialize the list of tracked points and the coordinate deltas
	pts = deque(maxlen=args["buffer"])
	(dX, dY) = (0 , 0)
	l=0
	
	camera = cv2.VideoCapture(0)
	
	while True:
		ad.tts("to start, say okay")		#NEW*
		
		cmmd=ad.stt()
		if cmmd is None:
			continue
		if ad.find(cmmd, "ok"):
			l=0
			while True:
			
				if l==0:
					ad.tts("I am ready.")
			
					ret,frame0 = camera.read()
					frame0 = cv2.warpPerspective(frame0,M5,(p1,p2))
					l=-1
				
				# grab the current frame
				(grabbed, frame) = camera.read()

				# if we are viewing a video and we did not grab a frame, then we have reached the end of the video
				if args.get("video") and not grabbed:
					break
				# resize the frame, crop it(into a quadrilateral), blur it, and convert it to the HSV color space
				frame = cv2.warpPerspective(frame,M5,(p1,p2))
				blurred = cv2.GaussianBlur(frame, (11, 11), 0)
				hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
			 
				# construct a mask for a color, then perform a series of dilations and erosions to remove any small blobs left 							#in the mask
				mask = cv2.inRange(hsv, low1, high1)
				mask = cv2.erode(mask, None, iterations=2)
				mask = cv2.dilate(mask, None, iterations=2)
				cv2.imshow('mask', mask)
				
				# find contours in the mask and initialize the current (x, y) center of the ball
				cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
					cv2.CHAIN_APPROX_SIMPLE)[-2]
				center = None
				# only proceed if at least one contour was found
				if len(cnts) > 0:
					# find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
					c = max(cnts, key=cv2.contourArea)
					((x, y), radius) = cv2.minEnclosingCircle(c)
					M = cv2.moments(c)

					center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
					if l==-1 :							#NEW*
						a = int(M["m10"] / M["m00"])
						b = int(M["m01"] / M["m00"])
						l=-2							#NEW*

					# only proceed if the radius meets a minimum size
					if radius > 5:
						#update the list of tracked points
						cv2.circle(frame, (int(x), int(y)), int(radius),
						(0, 255, 255), 2)
						pts.appendleft(center)
	
				if len(pts)>10 :
					# check to see if enough points have been accumulated in
					# the buffer
					if pts[-10] is not None:
						# compute the difference between the x and y
						# coordinates
						dX = pts[-10][0] - pts[1][0]
						dY = pts[-10][1] - pts[1][1]	

				# show the frame to our screen and increment the frame counter
				cv2.imshow("frame", frame)
				key = cv2.waitKey(1) & 0xFF
				#counter += 1
				if (l==-2 and (np.abs(dX) > 15 or np.abs(dY) > 15)):			#NEW*
					l=-3								#NEW*
				# if the 'q' key is pressed, or if the object slows down, loop is exited and the cropped part is displayed
				if (l==-3 and key == ord('q')) or  (l==-3 and len(pts)>24 and np.abs(dX) < 10 and np.abs(dY) < 10):
					c = int(M["m10"] / M["m00"])
					d = int(M["m01"] / M["m00"])
					
					if (np.abs(d-b)>35):
						if b<d or c<a :
							ad.tts("sorry, invalid, please try again")
							break
						ad.tts("image is found and being cropped")
						crop_img = frame0[d:b,a:c]
										
						camera.release()
						newpath = '/home/sam/Desktop/itsp/photos'+str(time)  	
						if not os.path.exists(newpath):
							os.makedirs(newpath)
						cv2.imwrite(newpath + '/' + str(picno)+'.jpg',crop_img)
						cv2.imshow('cropped', crop_img)
						cv2.waitKey(5000)
						cv2.destroyAllWindows()
						return 0;
					#else treat it as an underline of a word
					else:
						if c<a :
							ad.tts("sorry, invalid, please try again")
							break
						ad.tts("I am looking for the meaning")
						crop_img = frame0[b-50:b-15,a:c]
						cv2.imwrite('Image0.jpg',crop_img)
						crop_img = cntour(crop_img)
						cv2.imwrite('Image.jpg',crop_img)
						z=2
					# cleanup the camera and close any open windows
					camera.release()
					cv2.destroyAllWindows()
					return crop_img;
					
		elif ad.find(cmmd, "done"):
			break		
		else:
			ad.tts("I don't get you. If you want my assistance than speak okay.")
			continue

#contour
def cntour (crop_img):
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
	ap.add_argument("-b", "--buffer", type=int, default=32,
	help="max buffer size")
	args = vars(ap.parse_args())
	# define the lower and upper boundaries of the "green" ball in the HSV color space, then initialize the list of tracked points
	low1 = (0, 0, 100)
	high1 = (255, 100, 255)
	pts = deque(maxlen=args["buffer"])
	# resize the frame, blur it, and convert it to the HSV color space
	blurred = cv2.GaussianBlur(crop_img, (11, 11), 0)
	hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
	# construct a mask for the color "green", then perform a series of dilations and erosions to remove any small blobs left in the mask
	
	mask = cv2.inRange(hsv, low1, high1)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)[-2]
	if len(cnts) > 0:
		# find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		e = int(M["m10"] / M["m00"])
		f = int(M["m01"] / M["m00"])
		cv2.imwrite('pic3.jpg',crop_img)
		crop_img2 = crop_img[f-5:1000000,0:10000000]
		#cv2.imwrite('pic3.jpg',crop_img2)
	cv2.destroyAllWindows()
	return crop_img2;


#Ocr
def ocr(img):

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	cv2.imwrite('test.jpg', gray)
	str1 = pytesseract.image_to_string(Image.open('test.jpg'))
	os.remove('test.jpg')
	str1 = str1.strip()		#to remove any leading blank spaces, if any
	n = str1.find('\n')

	if n!=-1:
		str1 = str1[0:n]		#first line stored

	
	str1 = str1.strip()			#to remove any leading or trailing blank spaces, if any
	l= len(str1)
	str1 = str1 + ' '		
	if (str1.count(' ')) <=3 :		#at most 3 words
		n=str1.count(' ')
	else:
		n=3
	if l==0:
		n=0
	a=list();
	print l
	i=0
	word=''
	
	c=0
	while c<n :
		if str1[i] == ' ' :
			a.append(word)
			word = ''
			c= c+1
		else:
		
			word = word + str1[i]
		i=i+1

	print n
	i=0
	d = enchant.Dict("en_GB")
	while n>i:
		print a[i]
		if not d.check(a[i]):
			if len(d.suggest(a[i])) >0:
				a[i] = d.suggest(a[i])[0]
				print a[i]

		ad.tts("is your word " + a[i])
		cmmd = ""
		while (1):
			cmmd=ad.stt()
			if cmmd is None:
				ad.tts("Try again")
				continue
			elif (ad.find(cmmd, "yes")):
				return a[i];
			elif (ad.find(cmmd, "no")):
				
				break

		i=i+1
	return "";


#Dictionary
def dictionary(word):
	if word == "":						
		ad.tts("Didn't get the word")			
		return;						
	d = enchant.Dict("en_GB")
	if not d.check(word):
		word = d.suggest(word)[0]
	if word[-1] == '.':
		word= word[0:-1]
	i=0
	print word
	dictionary=PyDictionary()
	dict=dictionary.meaning(word)
	while (1):
		c=0

		if dict is not None:
			ad.tts("your word is " + word)
			 
			if ( dict.has_key('Adjective')) :

				s= dict['Adjective']
				if len(s)>i :
					print s[i] 	
					ad.tts("adjective, " + s[i])
					c=1
				
			if dict.has_key('Noun') :
				s= dict['Noun']
				if len(s)>i :
					print s[i] 	
					ad.tts("Noun, " + s[i])
					c=1
				
			if dict.has_key('Verb') :
				s= dict['Verb']
				if len(s)>i :
					print s[i] 
					ad.tts("Verb, " + s[i])
					c=1
				
			if dict.has_key('Adverb') :
				s= dict['Adverb']
				if len(s)>i :
					print s[i] 
					ad.tts("Adverb, " + s[i])
					c=1
				
			if dict.has_key('Preposition') :
				s= dict['Preposition']
				if len(s)>=i :
					print s[i] 
					ad.tts("Preposition, " + s[i])
					c=1
			i=i+1
			if c==0:
				ad.tts("sorry, no more meanings available")
				break
		else:
			ad.tts("sorry, the meaning is not available")
			break
			
				
		
		ad.tts("Do you want an alternate meaning?" )
		while (1):
			cmmd=ad.stt()
			if cmmd == None:
				continue
			elif ad.find(cmmd, "yes") or ad.find(cmmd, "yeah"):
				break
			elif ad.find(cmmd, "no"):
				return;
				
	return;


#if __name__ =="__main__":
def main(tme):
	if tme == 1:	
		page_setup()	
		global M
		M = rotate(c)
		global M5
		M5 = trep_matr()
		tme = 2
	crop_img = crop(M,M5,tme/2)
	if crop_img is not 0:
		s=ocr(crop_img)
		dictionary(s)
	ad.tts('do you want to continue reading?')
	while(1):
		cmmd = ad.stt()
		if cmmd == None:
			ad.tts('try again')
			continue
		elif ad.find(cmmd, 'bye') or ad.find(cmmd, 'no'):
			break
		elif ad.find(cmmd, 'yes') or ad.find(cmmd, 'yeah'):
			
			tme = tme +1
			break
	if not tme %2 ==0:
		tme = tme +1
		main(tme)
