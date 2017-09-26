#!/usr/bin/env python 3.4
#
#  Implementation of KPI test cases
#

import os
import time
import threading

from collections import defaultdict
from collections import OrderedDict

from acts.controllers.iperf_server import IPerfServer, IPerfResult
from acts.test_utils.bt import BtEnum
from acts.test_utils.bt.bt_test_utils import connect_dev_to_headset
from acts.test_utils.bt.bt_test_utils import disconnect_headset_from_dev
from acts.test_utils.bt.bt_test_utils import pair_dev_to_headset
from acts.test_utils.bt.bt_test_utils import enable_bluetooth
from acts.test_utils.bt.bt_test_utils import disable_bluetooth
from acts.test_utils.bt.BluetoothBaseTest import BluetoothBaseTest

from acts.test_utils.wifi import wifi_test_utils as wutils


class CoexKpiA2dpTest(BluetoothBaseTest):
    interval = "-i1 -t 5 -p"

    def __init__(self, controllers):
        BluetoothBaseTest.__init__(self, controllers)
        self.headset_mac_addr = "E4:22:A5:0B:C1:66"
        self.Ip_Address = "192.168.1.9"
        self.path_to_audio = "original_dance_audio.mp3"
        self.duration=30.0
        self.tests = (
            'test_A2DP_iperf_tcp_ul_kpi_017',
            'test_A2DP_iperf_tcp_dl_kpi_018',
            'test_A2DP_iperf_udp_ul_kpi_019',
            'test_A2DP_iperf_udp_dl_kpi_020'
        )

    def setup_class(self):

        self.result_dict = defaultdict(list)
        self.dev = self.android_devices[0]
        self.network = self.user_params["network"]
        self.dev1=self.android_devices[1]
        self.port = "5033"
        self.path_to_logs = "/tmp/logs/"
        self.tag = 0
        wutils.wifi_test_device_init(self.dev)
        wutils.wifi_connect(self.dev, self.network)

    def setup_test(self):
        self.iperf_server = IPerfServer(self.port, self.path_to_logs)
        self.tag = self.tag + 1
        self.iperf_server.start(tag=str(self.tag))
        out_file_name = "iPerf{}/IPerfClient,{},{}.log".format(
            self.port, self.port, self.tag)
        self.client_file_name = os.path.join(self.path_to_logs, out_file_name)
        self.log.info(self.client_file_name)

    def teardown_class(self):

        wutils.reset_wifi(self.dev)
        wutils.wifi_toggle_state(self.dev, False)

    def teardown_test(self):
        super(BluetoothBaseTest, self).teardown_test()
        self.log_stats()
        self.iperf_server.stop()

        return True

    '''Helper Functions'''

    def iperf_result(self, uplink=False, udp=False):

        '''
        Calculates Iperf Throughput value.

        Args:
            uplink: To check whether iperf traffic is uplink or downlink
            udp:  To check whether iperf iperf traffic is udp or tcp,
            True if its udp

        Returns:
            Throughput of iperf run
        '''


        if not udp:
            if not uplink:
                result = IPerfResult(self.path_to_logs + "iPerf{}/IPerfServer,{},{},0.log"
                                     .format(self.port, self.port, self.tag))
                throughput = result.avg_send_rate
                self.log.info("IPERF Client TPT : {} Mbits/s".format(
                    str(round((throughput * 8), 2))))
                result = IPerfResult(self.client_file_name)
                throughput = result.avg_receive_rate
                throughput = str(round((throughput * 8), 2))
                self.log.info("IPERF Server TPT : {} Mbits/s".format(
                    throughput))
                return throughput

            result = IPerfResult(self.path_to_logs + "iPerf{}/IPerfServer,{},{},0.log"
                                     .format(self.port, self.port, self.tag))
            throughput = result.avg_receive_rate
            self.log.info("IPERF Server TPT : {} Mbits/s".format(
                    str(round((throughput * 8), 2))))
            result = IPerfResult(self.client_file_name)
            throughput = result.avg_send_rate
            throughput = str(round((throughput * 8), 2))
            self.log.info("IPERF Client TPT : {} Mbits/s".format(
                    throughput))
            return throughput

        result = IPerfResult(self.path_to_logs + "iPerf{}/IPerfServer,{},{},0.log".
                                 format(self.port, self.port, self.tag))
        throughput = result.avg_rate
        self.log.info("IPERF Server TPT : {} Mbits/s".format(
                str(round((throughput * 8), 2))))
        result = IPerfResult(self.client_file_name)
        throughput = result.avg_rate
        self.log.info(throughput)
        throughput=str(round((throughput * 8), 2))
        self.log.info("IPERF Client TPT : {} Mbits/s".format(
                throughput))
        return throughput

    def iperf_log_parser(self, status, result):
        '''
        Accepts the iperf logs and dumps to a file then calculates the throughput
        Returns throughput on success else throws an error saying iperf failed.

        Args:
            status: True if the iperf has successfully ran
            result: contains the logs of iperf

        Returns:
            Throughput from iperf log
        '''

        if not status:
            raise AssertionError("Iperf run Failed")

        with open(self.client_file_name, "w") as f:
            for i in range(0, len(result)):
                f.write((result[i]))
                f.write("\n")

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
                                                     .format(self.path_to_audio))):
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

    def a2dp_long_duration(self):
        
        if not pair_dev_to_headset(self.log, self.dev, self.headset_mac_addr):
            self.log.error("Could not pair to {}".format(self.headset_mac_addr))
            return False
        if not connect_dev_to_headset(self.dev, self.headset_mac_addr,
                                              set([BtEnum.BluetoothProfile.A2DP.value])):
            self.log.error("Failure to connect A2DP Headset")
            return False

        if not self.start_media_stream():
            self.log.error("Could not start stream at {}".format(
                self.dev.getBuildSerial()))
            return False
        return True

    ''' Tests '''
    
    def test_A2DP_iperf_tcp_ul_kpi_017(self):

        stream_time = time.time() + self.duration

        if  not self.a2dp_long_duration():
            self.log.info("A2DP streaming failed")
            return False

        t = threading.Thread(target=self.media_stream_check, args=(stream_time,))
        t.start()
        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                                       self.interval + self.port + " -J" + " -w" + " 512K")
        iperf_tp = self.iperf_log_parser(status, result)
        result = self.iperf_result(uplink=True)
        t.join()

    def test_A2DP_iperf_tcp_dl_kpi_018(self):

        stream_time = time.time() + self.duration

        if  not self.a2dp_long_duration():
            self.log.info("A2DP streaming failed")
            return False

        t = threading.Thread(target=self.media_stream_check, args=(stream_time,))
        t.start()
        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                                   self.interval + self.port + " -R" + " -J" + " -w" + " 512K")
        iperf_tp = self.iperf_log_parser(status, result)
        result = self.iperf_result(uplink=False)
        t.join()

    def test_A2DP_iperf_udp_ul_kpi_019(self):

        stream_time = time.time() + self.duration
        if  not self.a2dp_long_duration():
            self.log.info("A2DP streaming failed")
            return False
        t = threading.Thread(target=self.media_stream_check, args=(stream_time,))
        t.start()
        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                                self.interval + self.port + " -J" + " -u" + " -b" + " 200M")
        iperf_tp = self.iperf_log_parser(status, result)
        result = self.iperf_result(uplink=True,udp=True)
        t.join()

    def test_A2DP_iperf_udp_dl_020(self):

        stream_time = time.time() + self.duration
        if not  self.a2dp_long_duration():
            self.log.info("A2DP streaming failed")
            return False

        t = threading.Thread(target=self.media_stream_check, args=(stream_time,))
        t.start()
        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                                   self.interval + self.port + " -R" +" -J" + "-u" + "-b" + " 200M")
        iperf_tp = self.iperf_log_parser(status, result)
        result = self.iperf_result(uplink=True,udp=True)
        t.join()

   

