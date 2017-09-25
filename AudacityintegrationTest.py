#!/usr/bin/env python3.4
#
#   Copyright 2016 - The Android Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import time
import threading

import AudacityUtils

from acts.test_utils.bt import BtEnum
from acts.test_utils.bt.BluetoothBaseTest import BluetoothBaseTest
from acts.test_utils.bt.bt_test_utils import connect_dev_to_headset
from acts.test_utils.bt.bt_test_utils import pair_dev_to_headset

DEFAULT_PING_ADDR = "http://www.google.com/robots.txt"
network = {'SSID': 'Google_test123'}

class AudacityintegrationTest(BluetoothBaseTest):
    duration = 20
    
    def __init__(self, controllers):

        BluetoothBaseTest.__init__(self, controllers)
        self.dev = self.android_devices[0]
        self.headset_mac_addr = "88:C6:26:A8:48:F3"
        self.path = "Maatikichi.mp3"
        self.tests = (
            "test_a2dp_long_duration",
        )

    def teardown_test(self):
        super(BluetoothBaseTest, self).teardown_test()
        self.log_stats()
        return True

    def is_a2dp_connected(self):
        devices = self.dev.droid.bluetoothA2dpGetConnectedDevices()
        for device in devices:
            self.dev.log.debug("A2dp Connected device {}".format(device[
                "name"]))
            if (device["address"] == self.headset_mac_addr):
                return True
        return False
    
    def start_media_stream(self):

        self.log.info("Starting music stream")
        if not (self.dev.droid.mediaPlayOpen("file:///sdcard/Music/{}"
                                             .format(self.path))):
            self.log.error("Failed to play music")
            return False
        self.dev.droid.mediaPlaySetLooping(True)
        self.log.info("Music is now playing on device {}".format(
                                                self.dev.serial))
        return True
    
    def media_stream_check(self, duration):

        time.sleep(10)
        
        while time.time() < duration:
            
            if not self.is_a2dp_connected():
                self.log.error("A2dp connection not active at {}".format(
                                                self.dev.droid.getBuildSerial()))
                return False
            time.sleep(1)
        
        return True

    def test_a2dp_long_duration(self):

        if not pair_dev_to_headset(self.log, self.dev, self.headset_mac_addr):
            self.log.error("Could not pair to {}".format(self.headset_mac_addr))
            return False
                
        if not connect_dev_to_headset(self.dev, self.headset_mac_addr,
                                    set([BtEnum.BluetoothProfile.A2DP.value])):
            self.log.error("Failure to connect A2dp Headset")
            return False

        t = threading.Thread(target=AudacityUtils.audacity, args=(self.duration))
        t.start()
        
        if not self.start_media_stream():
            self.log.error("Could not start stream at {}".format(
                                        self.dev.getBuildSerial()))
            return False
        
        stream_time = time.time() + self.duration
        if not self.media_stream_check(stream_time):
            self.log.error("A2DP Connection not active at {}".format(
                                        self.dev.getBuildSerial()))
            return False
	
        t.join()
        return True
