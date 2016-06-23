import time
import imutils
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


rot = 0
z = 0
#low1 = (25, 60, 195)
#high1 = (50, 125, 230)

low1 = (160,150,100)
high1 = (180, 255,255)

#low1 = (0,0,220)
#high1 = (180, 4, 255)

def point_cordinate(): #cordinates of point

	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help="path to the (optional) video file")
	ap.add_argument("-b", "--buffer", type=int, default=32,
		help="max buffer size")
	args = vars(ap.parse_args())

	greenLower = (low1)
	greenUpper = (high1)
	 
	# initialize the list of tracked points, the frame counter, and the coordinate deltas
	pts = deque(maxlen=args["buffer"])
	counter = 0
	(dX, dY) = (100 , 100)
	t=300

	camera = cv2.VideoCapture(0)

	while True:
		#will start tracking when q is pressed, until then just display the video grab the current frame
		(grabbed, frame) = camera.read()		
		#frame = cv2.warpAffine(frame,Rotate.rotate(),(cols,rows)) if we are viewing a video and we did not grab a frame, then we have reached the end of the video
		if not grabbed:
			break
		# blur it, and convert it to the HSV color space
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	 
		# construct a mask for the color "green", then perform a series of dilations and erosions to remove any small blobs left in the mask
		mask = cv2.inRange(hsv, greenLower, greenUpper)
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
		counter += 1
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
	pt1 = np.float32([a,b,c,d])
	pt2 = np.float32([[0,0],[600,0],[0,900],[600,900]])
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
def crop (M2,M5):
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help="path to the (optional) video file")
	ap.add_argument("-b", "--buffer", type=int, default=32,
		help="max buffer size")
	args = vars(ap.parse_args())

	# define the lower and upper boundaries of the "green"
	# ball in the HSV color space
	greenLower = low1
	greenUpper = high1
	 
	# initialize the list of tracked points, the frame counter,
	# and the coordinate deltas
	pts = deque(maxlen=args["buffer"])
	counter = 0
	(dX, dY) = (0 , 0)
	direction = ""
	k=1
	l=0
	p=''

	# if a video path was not supplied, grab the reference
	# to the webcam
	if not args.get("video", False):
		camera = cv2.VideoCapture(0)
	 
	# otherwise, grab a reference to the video file
	else:
		camera = cv2.VideoCapture(args["video"])

	ad.tts("to start, say okay")
	while True:
		cmmd=ad.stt()
		if ad.find(cmmd, "ok"):
			l=0
			while True:
		
				if l==0:
					ad.tts("I am eveready.")
			
					ret,frame0 = camera.read()
					frame0 = imutils.resize(frame0, width=600)
					frame0 = cv2.warpAffine(frame0,M2,(600,450))
					frame0 = cv2.warpPerspective(frame0,M5,(600,900))
					l=-1
		
				# grab the current frame
				(grabbed, frame) = camera.read()

				# if we are viewing a video and we did not grab a frame, then we have reached the end of the video
				if args.get("video") and not grabbed:
					break
				# resize the frame, blur it, and convert it to the HSV color space
				frame = imutils.resize(frame, width=600)
				frame = cv2.warpAffine(frame,M2,(600,450))
				frame = cv2.warpPerspective(frame,M5,(600,900))
				blurred = cv2.GaussianBlur(frame, (11, 11), 0)
				hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
			 
				# construct a mask for the color "green", then perform a series of dilations and erosions to remove any small blobs left in the mask
				mask = cv2.inRange(hsv, greenLower, greenUpper)
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
					if k==1 :
						a = int(M["m10"] / M["m00"])
						b = int(M["m01"] / M["m00"])
						k=0

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
				counter += 1
				if (l==-1 and (np.abs(dX) > 15 or np.abs(dY) > 15)):
					l=-2
				# if the 'q' key is pressed, or if the object slows down, loop is exited and the cropped part is displayed
				if (l==-2 and key == ord('q')) or  (l==-2 and len(pts)>24 and np.abs(dX) < 10 and np.abs(dY) < 10):
					c = int(M["m10"] / M["m00"])
					d = int(M["m01"] / M["m00"])
					if (np.abs(d-b)>35):
						ad.tts("image is found and being croped")
						crop_img = frame0[d:b,a:c]
						camera.release()
						cv2.imshow('cropped', crop_img)
						cv2.waitKey(0)
						cv2.destroyAllWindows()
						cv2.imwrite('Image.jpg',crop_img)
						return 0;
					#else treat it as an underline of a word
					else:
						ad.tts("I am looking for the meaning")
						crop_img = frame0[b-60:b-5,a:c]
						crop_img = cntour(crop_img)
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
	greenLower = (0, 0, 100)
	greenUpper = (255, 100, 255)
	pts = deque(maxlen=args["buffer"])
	# resize the frame, blur it, and convert it to the HSV color space
	blurred = cv2.GaussianBlur(crop_img, (11, 11), 0)
	hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
	# construct a mask for the color "green", then perform a series of dilations and erosions to remove any small blobs left in the mask
	cv2.imshow("window", hsv)
	cv2.waitKey(3000)
	mask = cv2.inRange(hsv, greenLower, greenUpper)
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
			crop_img2 = crop_img[f+5:1000000,0:10000000]
			#cv2.imwrite('pic3.jpg',crop_img2)
	cv2.destroyAllWindows()
	return crop_img2;


#Ocr
def ocr(img):
	
	#hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	cv2.imwrite('test.jpg', gray)
	str1 = pytesseract.image_to_string(Image.open('test.jpg'))
	os.remove('test.jpg')
	return str1



#Dictionary
def dictionary(word):
	i=0
	#while (1):
	print word
	dictionary=PyDictionary()
	dict=dictionary.meaning(word)
	
	if dict is not None:
		ad.tts("your word is " + word)
		 
		if ( dict.has_key('Adjective')) :

			s= dict['Adjective']
			if len(s)>=i :
				print s[i] 	
				ad.tts("(adjective)" + s[i])
				
		if dict.has_key('Noun') :
			s= dict['Noun']
			if len(s)>=i :
				print s[i] 	
				ad.tts("(NOUN)" + s[i])
				
		if dict.has_key('Verb') :
			s= dict['Verb']
			if len(s)>=i :
				print s[i] 
				ad.tts("VERB" + s[i])
				
		if dict.has_key('Adverb') :
			s= dict['Adverb']
			if len(s)>=i :
				print s[i] 
				ad.tts("(ADVERB)" + s[i])
				
		if dict.has_key('Preposition') :
			s= dict['Preposition']
			if len(s)>=i :
				print s[i] 
				ad.tts("(PREPO)" + s[i])
				
		
		#ad.tts("If alternate meaning required, give a double tap within the next 3 seconds")
		#audio trigger will be awaited here, after message for one, in case user didnt get meaning that was wanted
		#if received, then i++


		
#if __name__ =="__main__":
def main():	
	page_setup()	
	M = rotate(c)
	M5=trep_matr()
	crop_img = crop(M,M5)
	if crop_img is not 0:
		s=ocr(crop_img)
		dictionary(s)
