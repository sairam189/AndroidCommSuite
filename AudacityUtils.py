# Audacity Automation for recording audio
# pre-requiste 
#	Python-3
# 	Audacity-2.0.5
#	Install the PyPI package:
#		$ sudo pip install keyboard
#	
#	or clone the repository (no installation required, source files are sufficient):
#		$ git clone https://github.com/boppreh/keyboard

import time as t
import os
from pymouse import PyMouse
from pykeyboard import PyKeyboard


#gets mouse current position coordinates
m = PyMouse()
k = PyKeyboard()
duration =20

def audacity(duration):

    #Launching Audacity
    print("Audacity.....")
    os.system("audacity &")

    # Step 1: Recording the Audio.
    print("Recording the Audio")
    t.sleep(5)
    k.tap_key('r')


    #Step 2: Screeshot
    #print("capturing Screenshot")
    #k.press_key(k.alt_key)
    #k.tap_key('s')
    #k.release_key(k.alt_key)
    t.sleep(duration)

    #Step 3: Stop Recording
    print("Stop Recording")
    k.tap_key('space')
    t.sleep(5)

    #Step 4: Exporting recorded audio to .wav file.
    print("Exporting Audio")
    k.press_key(k.shift_key)
    k.tap_key('e')
    k.release_key(k.shift_key)
    t.sleep(2)

    #Step 5: Give the Path to save the file name.
    print("Path to save the .wav file")
    k.type_string("Aud1")
    t.sleep(2)


    #Step 6: Save recorded audio.
    print("\nSave Audio")
    k.tap_key(k.enter_key)
    t.sleep(2)
    k.tap_key(k.enter_key)
    t.sleep(2)
    k.tap_key(k.enter_key)
    t.sleep(2)

    # Capturing Mouse Movement.
    m.move(200, 200)
    m.click(200, 200, 1)

    # Step 7: Save the .Aup Project.
    print("Saving .Aup Project")
    k.press_key(k.control_key)
    k.tap_key('s')
    k.release_key(k.control_key)
    t.sleep(2)
    k.type_string("/home/Audacity/Aud111")
    t.sleep(2)

    # Step 7: Exit Audacity.
    print("Exiting Audacity")
    k.press_key(k.control_key)
    k.tap_key('q')
    k.release_key(k.control_key)
    t.sleep(2)

