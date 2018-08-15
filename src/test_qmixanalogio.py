import test_common
import unittest
import time
import sys

from qmixsdk import qmixbus
from qmixsdk import qmixanalogio


class QmixAnalogIoTestCase(test_common.QmixTestBase):
    """
    Test for testing the python integration of the QmixSDK analog I/O interface
    """
    def step01_capi_open(self):
        print("Opening bus with deviceconfig ", deviceconfig)
        self.bus = qmixbus.Bus()
        self.bus.open(deviceconfig, 0)


    def step02_input_lookup(self):
        print("Looking up input channels...")
        channel_count = qmixanalogio.AnalogInChannel.get_no_of_channels()
        print("Number of analog in channels: ", channel_count)
        for i in range (channel_count):
            channel = qmixanalogio.AnalogInChannel()
            channel.lookup_channel_by_index(i)
            print("Name of channel ", i, " is ", channel.get_name())
        self.input = qmixanalogio.AnalogInChannel()
        self.input.lookup_channel_by_name("QmixIO_1_AI0")


    def step03_output_lookup(self):
        print("Looking up output channels..")
        channel_count = qmixanalogio.AnalogOutChannel.get_no_of_channels()
        print("Number of analog out channels: ", channel_count)
        for i in range (channel_count):
            channel = qmixanalogio.AnalogOutChannel()
            channel.lookup_channel_by_index(i)
            print("Name of channel ", i, " is ", channel.get_name()) 
        self.output = qmixanalogio.AnalogOutChannel()
        self.output.lookup_channel_by_name("QmixIO_1_AO0_PWM")

    
    def step04_bus_start(self):
        print("Starting bus communication...")
        self.bus.start()


    def step05_scaling(self):
        print("Testing scaling...")

        scaling = self.input.get_scaling_param()
        print("Input scaling: ", self.input.get_scaling_param())
        self.input.set_scaling_param(10, 2)
        print("Input scaling: ", self.input.get_scaling_param())
        self.input.set_scaling_param(scaling.factor, scaling.offset)
        self.assertEqual(scaling, self.input.get_scaling_param())
        self.input.enable_software_scaling(False)
        self.input.enable_software_scaling(True)

        scaling = self.output.get_scaling_param()
        print("Output scaling: ", self.output.get_scaling_param())
        self.output.set_scaling_param(10, 2)
        print("Output scaling: ", self.output.get_scaling_param())
        self.output.set_scaling_param(scaling.factor, scaling.offset)
        self.assertEqual(scaling, self.output.get_scaling_param())
        self.output.enable_software_scaling(False)
        self.output.enable_software_scaling(True)


    def step06_read_input(self):
        print("Testing input readint...")
        for i in range (5):
            print("Value: ", self.input.read_input())
            time.sleep(0.1)

        self.input.enable_software_scaling(False)
        for i in range (5):
            print("Value: ", self.input.read_input())
            time.sleep(0.1)
        self.input.enable_software_scaling(True)


    def step07_write_output(self):
        self.output.write_output(5)
        print("Output: ", self.output.get_output_vaue())


    def step08_io_device(self):
        inputdevice = self.input.get_io_device()
        print("Input device: ", inputdevice.get_device_name())
        outputdevice = self.output.get_io_device()
        print("Output device: ", outputdevice.get_device_name())


    def step25_capi_close(self):
        print("Closing bus...")
        self.bus.stop()
        self.bus.close()

if __name__ == '__main__':
    deviceconfig = sys.argv[1]
    del sys.argv[1:]
    unittest.main()
