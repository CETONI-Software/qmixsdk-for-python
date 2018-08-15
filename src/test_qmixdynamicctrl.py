import test_common
import unittest
import time
import sys

from qmixsdk import qmixbus
from qmixsdk import qmixcontroller
from qmixsdk import qmixanalogio

class QmixDynamicControlTestCase(test_common.QmixTestBase):
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


    def step03_build_controller(self):
        print("Building control loop...")
        control_loop_in = qmixanalogio.AnalogInChannel()
        control_loop_in.lookup_channel_by_name("QmixQplus_1_AI0_PT100")
        control_loop_out = qmixanalogio.AnalogOutChannel()
        control_loop_out.lookup_channel_by_name("QmixQplus_1_AO0_PWM")
        self.control_channel = qmixcontroller.ControllerChannel.create_pid_control_channel(
            control_loop_in, control_loop_out, qmixcontroller.LoopOutType.analog)


    def step04_set_param(self):
        print("Setting PID parameters...")
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.K, 3)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.Td, 0)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.Ti, 260)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.derivative_gain_limit, 20)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.Tt, 250)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.min_U, 0)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.max_U, 100)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.diabled_U, 0)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.initial_setpoint, 0)
        self.control_channel.set_pid_parameter(qmixcontroller.PIDParameter.sample_time, 500)


    def step05_bus_start(self):
        print("Starting bus communication...")
        self.bus.start()


    def step06_control_loop(self):
        print("Testing control loop...")
        # The Q+ module has a special digital enable output that we need to set
	    # to enable the PWM output
    

        setpoint = 50
        self.control_channel.write_setpoint(setpoint)
        self.control_channel.enable_control_loop(True)
        print("Control loop enables. This test runs until the actual value raises above ", 
            setpoint - 1)
        actual_value = self.control_channel.read_actual_value()
        while actual_value < (setpoint - 1):
            actual_value = self.control_channel.read_actual_value()
            print("Actual value: ", actual_value)
            time.sleep(1)

        # Now we disable the control loop and wait until the temperature dropped
	    # by 10 degre
        print("Control loop disabled. This test runs until the actual value drops below ",
            setpoint - 10)
        while actual_value > (setpoint - 10):
            actual_value = self.control_channel.read_actual_value()
            print("Actual value: ", actual_value)
            time.sleep(1)

        
    def step25_capi_close(self):
        print("Closing bus...")
        self.bus.stop()
        self.bus.close()

if __name__ == '__main__':
    deviceconfig = sys.argv[1]
    del sys.argv[1:]
    unittest.main()
