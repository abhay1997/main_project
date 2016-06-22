import audio_fn as ad
import time
#start
name="name"
def start():

	hour= int(time.strftime("%H"))
	print hour

	if (hour>5 and hour <12):
		ad.tts("Good morning")
	elif (hour>12 and hour <16):
		ad.tts("Good afternoon")
	else:
        	ad.tts("Good evening") 

	ad.tts("May i know your good  name?")
	global name
	name=str(ad.stt())
	print name
	ad.tts("Hello "+str(name)+", I am Amina. your helper.")
	return

def which_mode():
	#ad.tts(str(name)+"What do you intend to do?")
	wh=ad.stt()
	if ad.find(wh,"read"):
		ad.tts("ok, I am ready to assist you in reading.")
		#read()
	elif ( ad.find(wh,"sketch") or ad.find(wh,"draw") ):
		ad.tts("ok, I am ready to assist you in sketching.")
		#sketch()
	elif ( ad.find(wh,"note") or ad.find(wh,"write") ):
		ad.tts("ok, I am ready to assist you in taking notes.")
		#note()
	else:
		ad.tts("Sorry, I didn't get you. Are you reading or sketching or taking notes?")
		which_mode()	



if __name__ == "__main__":
	start()
#	configure()
	ad.tts(str(interface.name)+", What do you intend to do?")
	which_mode()
#	dict_crop()
