import test_common
import unittest
import time
import sys

from qmixsdk import qmixbus
from qmixsdk import qmixcontroller

class QmixQPlusTestCase(test_common.QmixTestBase):
    """
    Test for testing the python integration of the QmixSDK controller interface
    The test uses a Qmix Q+ device for testing.
    """
    def step01_capi_open(self):
        print("Opening bus with deviceconfig ", deviceconfig)
        self.bus = qmixbus.Bus()
        self.bus.open(deviceconfig, 0)

    
    def step02_device_lookup(self):
        print("Looking up devices...")
        self.reactor_zone = qmixcontroller.ControllerChannel()
        self.reactor_zone.lookup_channel_by_name("QmixQplus_1_ReactorZone")
        self.reaction_loop = qmixcontroller.ControllerChannel()
        self.reaction_loop.lookup_channel_by_name("QmixQplus_1_ReactionLoop")


    def setp03_channel_enumeration(self):
        print("Enumerating channels...")
        channel_count = qmixcontroller.ControllerChannel.get_no_of_channels()
        print("Number of control channels: ", channel_count)
        for i in range(channel_count):
            channel = qmixcontroller.ControllerChannel()
            channel.lookup_channel_by_index(i)
            print("Name of channel ", i, " is ", channel.get_name())


    def step04_bus_start(self):
        print("Starting bus communication...")
        self.bus.start()


    def step05_control_loop_enable(self):
        print("Testing control loop enabling...")
        setpoint = 40
        self.reaction_loop.write_setpoint(setpoint)
        self.reaction_loop.enable_control_loop(True)
        self.assertTrue(self.reaction_loop.is_control_loop_enabled())
        self.reaction_loop.enable_control_loop(False)
        self.assertFalse(self.reaction_loop.is_control_loop_enabled())


    def step06_heating_up(self):
        setpoint = 40
        self.reaction_loop.enable_control_loop(True)
        print("Control loop enabled. This test runs until the actual value raises above "
            , setpoint, "°C...")
        reaction_loop_value = self.reaction_loop.read_actual_value()
        while reaction_loop_value < (setpoint - 1):
            # We display the temperature of both control loops - one should
            # one should raise and one should remain constant
            reaction_loop_value = self.reaction_loop.read_actual_value()
            print("Reactor zone actual value: ", self.reactor_zone.read_actual_value())
            print("Reaction loop actual value: ", reaction_loop_value)
            time.sleep(1)

        # Now we disable the control loop and wait until the temperature dropped
        # by 10 degree
        self.reaction_loop.enable_control_loop(False)
        print("Control loop disabled. This test runs until the actual value drops below ",
            setpoint - 5)
        while reaction_loop_value > (setpoint - 5):
            reaction_loop_value = self.reaction_loop.read_actual_value()
            print("Reaction loop actual value: ", reaction_loop_value)
            time.sleep(1)
        
    def step25_capi_close(self):
        print("Closing bus...")
        self.bus.stop()
        self.bus.close()

if __name__ == '__main__':
    deviceconfig = sys.argv[1]
    del sys.argv[1:]
    unittest.main()
