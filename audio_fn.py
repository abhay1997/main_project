import speech_recognition as sr
from gtts import gTTS
import pyaudio
import wave
from pydub import AudioSegment
import os


def stt():
	# obtain audio from the microphone
	r = sr.Recognizer()
	with sr.Microphone() as source:
		#   print("Say something!")
		r.adjust_for_ambient_noise(source,duration=1)
		print("say your command")
		audio = r.listen(source)
		print("i have listened what you spoke")

	# recognize speech using Google Speech Recognition
	try:
	 	# for testing purposes, we're just using the default API key
	 	# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
	   	# instead of `r.recognize_google(audio)`
		return r.recognize_google(audio)
	except sr.UnknownValueError:
		tts("I could not understand, please speak again")
		stt()
	except sr.RequestError as e:
		tts("I am having some trouble") #Could not request results from Google Speech Recognition service


def play(file_name):
	print("in play_mp3")
	song = AudioSegment.from_mp3(file_name)
	song.export("temp.wav", format="wav")
	print (" converted")	
	play_wave("temp.wav")
	return

def play_wave(file_wave):
	chunk = 1024
	wf = wave.open(file_wave, 'rb')
	p = pyaudio.PyAudio()

	stream = p.open(
    		format = p.get_format_from_width(wf.getsampwidth()),
    		channels = wf.getnchannels(),
    		rate = wf.getframerate(),
    		output = True)
	data = wf.readframes(chunk)

	while data != '':
    		stream.write(data)
    		data = wf.readframes(chunk)

	stream.close()
	p.terminate()
	return

def tts( str ):
	obj = gTTS(text=str, lang='en')
	obj.save("temp.mp3")	
	play("temp.mp3")



def find( str , cmmd ):
	if cmmd in str:
		return True
	else:
		return False

def remove_files():
	os.remove("temp.mp3")
	os.remove("temp.wav")



if __name__=="__main__":
	a=stt()
	print a
	tts(a)
