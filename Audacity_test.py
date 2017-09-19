# Audacity Automation for recording audio
# pre-requiste 
#	Python-3
# 	Audacity-2.0.5
#	Install the PyPI package:
#		$ sudo pip install keyboard
#	
#	or clone the repository (no installation required, source files are sufficient):
#		$ git clone https://github.com/boppreh/keyboard
	

from acts.test_utils.bt.BluetoothBaseTest import BluetoothBaseTest
import keyboard
import time as t
import os
from pymouse import PyMouse

 #gets mouse current position coordinates


class Audacity_test(BluetoothBaseTest):
    def __init__(self, controllers):
        BluetoothBaseTest.__init__(self, controllers)
        m = PyMouse()
        m.position()

    def audacity(self):
        m = PyMouse()
        m.position()  # gets mouse current position coordinates

        #Launching Audacity
        print("Audacity.....")
        os.system("audacity &")

        # Step 1: Recording the Audio.
        print("Recording the Audio")
        t.sleep(5)
        keyboard.press_and_release('shift+r')
        keyboard.press_and_release('r')

        #Step 2: Screeshot
        #print("capturing Screenshot")
        #keyboard.press_and_release('Alt+s')
        t.sleep(5)

        #Step 3: Stop Recording
        print("Stop Recording")
        keyboard.press_and_release('space')
        t.sleep(5)

        #Step 4: Exporting recorded audio to .wav file.
        print("Exporting Audio")
        keyboard.press_and_release('ctrl+shift+e ')
        t.sleep(2)

        #Step 5: Give the Path to save the file name.
        print("Path to save the .wav file")
        keyboard.write("Aud1")
        t.sleep(2)


        #Step 6: Save recorded audio.
        print("\nSave Audio")
        keyboard.press_and_release('enter')
        t.sleep(2)
        keyboard.press_and_release('enter')
        t.sleep(2)
        keyboard.press_and_release('enter')
        t.sleep(2)

        # Capturing Mouse Movement.
        m.move(200, 200)
        m.click(200, 200, 1)

        # Step 7: Save the .Aup Project.
        print("Saving .Aup Project")
        keyboard.press_and_release('ctrl+s')
        t.sleep(2)
        keyboard.write("Aud11")
        t.sleep(2)
        keyboard.press_and_release('enter')
        t.sleep(2)

        # Step 7: Exit Audacity.
        print("Exiting Audacity")
        keyboard.press_and_release('ctrl+q')
        t.sleep(2)
