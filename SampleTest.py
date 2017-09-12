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

import os
import time
import threading
from acts.test_utils.bt import BtEnum

from acts import asserts
from acts.base_test import BaseTestClass
from acts.controllers import iperf_server
from acts.test_utils.bt.BluetoothBaseTest import BluetoothBaseTest
from acts.test_utils.bt.bt_test_utils import reset_bluetooth
from acts.test_utils.bt.bt_test_utils import connect_dev_to_headset
from acts.test_utils.bt.bt_test_utils import pair_dev_to_headset
from acts.test_utils.bt.bt_test_utils import play_media
from acts.test_utils.wifi import wifi_test_utils


DEFAULT_PING_ADDR = "http://www.google.com/robots.txt"
network= {'SSID': 'Google_test123'}

class SampleTest(BluetoothBaseTest):
    default_timeout = 20
    iterations = 5

    def __init__(self, controllers):
        BluetoothBaseTest.__init__(self, controllers)
        self.dev = self.android_devices[0]
        self.headset_to_connect = "E4:22:A5:0B:C1:66"
        self.Ip_Address = "192.168.1.9"
        self.path = "MUNGARUALEYE.mp3"
        self.med_to_play = ""
        wifi_test_utils.wifi_test_device_init(self.dev)
        wifi_test_utils.wifi_connect(self.dev, network)
        wifi_test_utils.check_internet_connection(self.dev, DEFAULT_PING_ADDR)
        self.tests = (
            "test_coex_connectivity",
            "test_connect_disconnect_headset",
            "test_a2dp_long_duration",
        )

    def teardown_test(self):
        super(BluetoothBaseTest, self).teardown_test()
        self.log_stats()
        return True
    
    def test_wifi_toggle_state(self):
        
        wifi_test_utils.wifi_toggle_state(self.dev, False)
        return True
            
    def test_coex_connectivity(self):
        
        t = threading.Thread(target = self.dev.run_iperf_client,
		args=(self.Ip_Address, "-i 1 -t %s" %self.iterations))
        t.start()

        for n in range(self.iterations):
            self.log.info("Toggling bluetooth iteration {}.".format(n + 1))
            if not reset_bluetooth([self.android_devices[0]]):
                self.log.error("Failure to reset Bluetooth")
                return False
        t.join()
        return True

    def test_connect_disconnect_headset(self):

        t = threading.Thread(target = self.dev.run_iperf_client,
		args=(self.Ip_Address, "-i 1 -t %s" %self.iterations))
        t.start()

        if not pair_dev_to_headset(self.log, self.dev, self.headset_to_connect):
            self.log.error("Could not pair to {}".format(self.headset_to_connect))
            return False
        
        for n in range(self.iterations):
            self.log.info("Connecting to Headset(A2DP) iterations {}.".format(n + 1))
            if not connect_dev_to_headset(
                self.log, self.dev.droid, self.headset_to_connect,
                set([BtEnum.BluetoothProfile.A2DP_SINK.value])):
                self.log.error("Failure to connect Headset")
                return False
            time.sleep(5)
            self.dev.droid.bluetoothDisconnectConnected(self.headset_to_connect)
        t.join()
        return True

    def test_a2dp_long_duration(self):

        t = threading.Thread(target = self.dev.run_iperf_client,
                             args=(self.Ip_Address, "-i 1 -t %s" %self.iterations))

        if not pair_dev_to_headset(self.log, self.dev, self.headset_to_connect):
            self.log.error("Could not pair to {}".format(self.headset_to_connect))
            return False
        
        if not connect_dev_to_headset(
            self.log, self.dev.droid, self.headset_to_connect,
            set([BtEnum.BluetoothProfile.A2DP_SINK.value])):
            self.log.error("Failure to connect A2dp Headset")
            return False

        self.log.info("Starting audio.....")
        if not play_media(self.log, self.dev.droid, self.path):
            self.log.error("Failure to play audio")
            return False
        self.dev.droid.bluetoothDisconnectConnected(self.headset_to_connect)
        t.join()
        return True
            
