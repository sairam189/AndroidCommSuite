#!/usr/bin/env python 3.4
#
#  Implementation of KPI test cases
#

import os
import time

from datetime import datetime

from acts.base_test import BaseTestClass
from acts.test_utils.wifi import wifi_test_utils as wutils
from acts.test_utils.bt.bt_test_utils import enable_bluetooth
from acts.test_utils.bt.bt_test_utils import disable_bluetooth
from acts.controllers.iperf_server import IPerfServer, IPerfResult

class CoexKpiTest(BaseTestClass):
    interval = "-i1 -t 5 -p"


    def __init__(self, controllers):
        BaseTestClass.__init__(self, controllers)
        self.tests = (
            'test_wlan_standalone_tcp_ul',
            'test_wlan_with_bt_on_tcp_ul',
            'test_wlan_standalone_tcp_dl',
            'test_wlan_with_bt_on_tcp_dl',
            'test_wlan_standalone_udp_ul',
            'test_wlan_with_bt_on_udp_ul',
            'test_wlan_standalone_udp_dl',
            'test_wlan_with_bt_on_udp_dl',


        )

    def setup_class(self):

        self.dev = self.android_devices[0]
        self.network = self.user_params["network"]
        wutils.wifi_test_device_init(self.dev)
        wutils.wifi_connect(self.dev, self.network)
        self.port = "5033"
        self.path="/tmp/logs/"
        self.tag=0

    def setup_test(self):
        self.iperf_server = IPerfServer(self.port, self.path)
        self.tag = self.tag + 1
        self.iperf_server.start(tag=str(self.tag))
        out_file_name = "iPerf{}/IPerfClient,{},{}.log".format(
                            self.port, self.port, self.tag)
        self.client_file_name = os.path.join(self.path, out_file_name)
        self.log.info(self.client_file_name)


    def teardown_class(self):

        wutils.reset_wifi(self.dev)
        wutils.wifi_toggle_state(self.dev, False)

    def teardown_test(self):

        self.iperf_server.stop()

    '''Helper Functions'''

    def bluetooth_on(self):
        '''
        Turns on the Bluetooth of the android device
        '''

        if not enable_bluetooth(self.dev.droid, self.dev.ed):
            self.log.error("Failed to turn on bt")

    def bluetooth_off(self):
        '''
        Turns off the bluetooth of the android device
        '''

        if not disable_bluetooth(self.dev.droid):
            self.log.error("Failed to turn off bt")

    def iperf_result(self,uplink=False, udp=False):

        '''
        Calculates Iperf Throughput value.

        Args:
            uplink: To check whether iperf traffic is uplink or downlink
            udp:  To check whether iperf iperf traffic is udp or tcp,
            True if its udp

        Returns:
            Throughput of iperf run
        '''

        time.sleep(1)
        if udp:
            result = IPerfResult(self.path + "iPerf{}/IPerfServer,{},{},0.log".
                                     format(self.port, self.port,self.tag))
            throughput = result.avg_rate
            self.log.info("IPERF Server TPT : {} Mbits/s".format(
                                    str(round((throughput * 8), 2))))
            result = IPerfResult(self.client_file_name)
            throughput = result.avg_rate
            self.log.info("IPERF Client TPT : {} Mbits/s".format(
                                    str(round((throughput * 8), 2))))
        else:
            if uplink:
                result = IPerfResult(self.path + "iPerf{}/IPerfServer,{},{},0.log"
                                     .format(self.port, self.port,self.tag))
                throughput = result.avg_receive_rate
                self.log.info("IPERF Server TPT : {} Mbits/s".format(
                                    str(round((throughput * 8), 2))))
                result = IPerfResult(self.client_file_name)
                throughput = result.avg_send_rate
                self.log.info("IPERF Client TPT : {} Mbits/s".format(
                                    str(round((throughput * 8), 2))))
            else:
                result = IPerfResult(self.path + "iPerf{}/IPerfServer,{},{},0.log"
                                     .format(self.port, self.port, self.tag))
                throughput = result.avg_send_rate
                self.log.info("IPERF Client TPT : {} Mbits/s".format(
                                    str(round((throughput * 8), 2))))
                result = IPerfResult(self.client_file_name)
                throughput = result.avg_receive_rate
                self.log.info("IPERF Server TPT : {} Mbits/s".format(
                                    str(round((throughput * 8), 2))))



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

        if status:


            with open(self.client_file_name, "w") as f:
                for i in range(0, len(result)):
                    f.write((result[i]))
                    f.write("\n")
        else:
            raise AssertionError("Iperf run failed")

    ''' Tests '''

    def test_wlan_standalone_tcp_ul(self):

        '''
        Starts Iperf traffic with TCP- Uplink.
        '''


        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                            self.interval + self.port + " -J")
        self.iperf_log_parser(status, result)
        self.iperf_result(uplink=True)

    def test_wlan_standalone_tcp_dl(self):

        '''
        Starts Iperf traffic with TCP - Downlink.
        '''



        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                            self.interval + self.port + " -R" +" -J")
        self.iperf_log_parser(status, result)
        self.iperf_result()

    def test_wlan_standalone_udp_ul(self):

        '''
        Starts iperf traffic with UDP - Uplink.
        '''



        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                            self.interval + self.port + " -J" +" -u")
        self.iperf_log_parser(status, result)
        self.iperf_result(udp=True)

    def test_wlan_standalone_udp_dl(self):

        '''
        Starts iperf traffic with UDP - Downlink.
        '''



        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                        self.interval + self.port + " -R"+" -J"+" -u")
        self.iperf_log_parser(status, result)
        self.iperf_result(udp=True)

    def test_wlan_with_bt_on_tcp_ul(self):

        '''
        Starts iperf traffic over TCP - Uplink with Bluetooth state on.
        '''

        self.bluetooth_on()

        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                            self.interval + self.port + " -J")
        self.iperf_log_parser(status, result)
        self.iperf_result(uplink=True)
        self.bluetooth_off()

    def test_wlan_with_bt_on_tcp_dl(self):

        '''
        Start iperf traffic over TCP - Downliink with Bluetooth state on.
        '''

        self.bluetooth_on()

        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                        self.interval + self.port + " -R"+" -J")
        self.iperf_log_parser(status, result)
        self.iperf_result()
        self.bluetooth_off()

    def test_wlan_with_bt_on_udp_ul(self):

        '''
        Start iperf traffic over UDP - Uplink with Bluetooth state on.
        '''

        self.bluetooth_on()


        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                            self.interval+ self.port + " -J" + " -u")
        self.iperf_log_parser(status, result)
        self.iperf_result(udp=True)
        self.bluetooth_off()

    def test_wlan_with_bt_on_udp_dl(self):

        '''
        Start iperf traffic over UDP - Downlink with Bluetooth state on.
        '''

        self.bluetooth_on()

        status, result = self.dev.run_iperf_client(self.user_params["server_addr"],
                                        self.interval + self.port + " -R"+" -J" +" -u")
        self.iperf_log_parser(status, result)
        self.iperf_result(udp=True)
        self.bluetooth_off()

