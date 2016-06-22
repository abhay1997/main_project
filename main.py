import interface as intf
import audio_fn as ad

if __name__ == "__main__":
        intf.start()
#       configure()
        ad.tts(str(intf.name)+", What do you intend to do?")
        intf.which_mode()
#       dict_crop()

	
	ad.remove_files()
