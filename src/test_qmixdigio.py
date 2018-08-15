import test_common
import unittest
import time
import sys

from qmixsdk import qmixbus
from qmixsdk import qmixdigio


class QmixDigitalIoTestCase(test_common.QmixTestBase):
    """
    Test for testing the python integration of the QmixSDK digital I/O interface
    """
    def step01_capi_open(self):
        print("Opening bus with deviceconfig ", deviceconfig)
        self.bus = qmixbus.Bus()
        self.bus.open(deviceconfig, 0)


    def step02_input_lookup(self):
        print("Looking up input channels...")
        channel_count = qmixdigio.DigitalInChannel.get_no_of_channels()
        print("Number of digital in channels: ", channel_count)
        for i in range (channel_count):
            channel = qmixdigio.DigitalInChannel()
            channel.lookup_channel_by_index(i)
            print("Name of channel ", i, " is ", channel.get_name())
        self.input = qmixdigio.DigitalInChannel()
        self.input.lookup_channel_by_name("neMESYS_Low_Pressure_1_DigINA")


    def step03_output_lookup(self):
        print("Looking up output channels..")
        channel_count = qmixdigio.DigitalOutChannel.get_no_of_channels()
        print("Number of digital out channels: ", channel_count)
        for i in range (channel_count):
            channel = qmixdigio.DigitalOutChannel()
            channel.lookup_channel_by_index(i)
            print("Name of channel ", i, " is ", channel.get_name()) 
        self.output = qmixdigio.DigitalOutChannel()
        self.output.lookup_channel_by_name("neMESYS_Low_Pressure_1_DigOUTA")

    
    def step04_bus_start(self):
         print("Starting bus communication...")
         self.bus.start()


    def step06_read_input(self):
        print("Testing input reading...")
        print("Input state: ", self.input.is_on())


    def step07_write_output(self):
        print("Testing output writing...")
        self.output.write_on(True)
        print("Output state (True): ", self.output.is_output_on())
        self.output.write_on(0)
        print("Output state (0): ", self.output.is_output_on())


    def step25_capi_close(self):
        print("Closing bus...")
        self.bus.stop()
        self.bus.close()

if __name__ == '__main__':
    deviceconfig = sys.argv[1]
    del sys.argv[1:]
    unittest.main()
