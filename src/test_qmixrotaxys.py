import test_common
import unittest
import time
import sys

from qmixsdk import qmixbus
from qmixsdk import qmixmotion
from qmixsdk.qmixbus import UnitPrefix, TimeUnit
from collections import namedtuple


class QmixRotaxysTestCase(test_common.QmixTestBase):
    """
    Test for testing the python integration of the QmixSDK digital I/O interface
    """
    def step01_capi_open(self):
        print("Opening bus with deviceconfig ", deviceconfig)
        self.bus = qmixbus.Bus()
        self.bus.open(deviceconfig, 0)


    def step02_device_name_lookup(self):
        lift_axis = qmixmotion.Axis()
        lift_axis.lookup_by_name("rotAXYS_1_Lift")
        self.rotaxys = qmixmotion.AxisSystem()
        self.rotaxys.lookup_by_name("rotAXYS_1")

        axis_system_count = qmixmotion.AxisSystem.get_axis_system_count()
        print("Available axis systems: ")
        for i in range(axis_system_count):
            axis_system = qmixmotion.AxisSystem()
            axis_system.lookup_by_device_index(i)
            print("Name of axis system ", i, " is ", axis_system.get_device_name())

        print("Available rotaxys axes :")
        for i in range(self.rotaxys.get_axes_count()):
            axis = self.rotaxys.get_axis_device(i)
            print("Axis ", i, " name: ", axis.get_device_name())


    def step03_bus_start(self):
         print("Starting bus communication...")
         self.bus.start()

        
    @staticmethod
    def wait_axis_homing_attained(axis, timeout_seconds):
        """
        The function waits until the given axis has finished homing move
        until the timeout occurs.
        """
        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        result = False
        while (result == False) and not timer.is_expired():
            time.sleep(0.1)
            result = axis.is_homing_position_attained()
        return result


    @staticmethod
    def wait_homing_attained(axis_system, timeout_seconds):
        """
        The function waits until the given axis system has finished homing move
        until the timeout occurs.
        """
        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        result = False
        while (result == False) and not timer.is_expired():
            time.sleep(0.1)
            result = axis_system.is_homing_position_attained()
        return result


    @staticmethod
    def wait_axis_target_reached(axis, timeout_seconds):
        """
        The function waits until the given axis has reached target position or
        until the timeout occurs.
        """
        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        result = False
        while (result == False) and not timer.is_expired():
            time.sleep(0.1)
            result = axis.is_target_position_reached()
            print("Position: ", axis.get_actual_position(), " Velocity: ",
                axis.get_actual_velocity(), " target reached: ", result)
        return result


    @staticmethod
    def wait_target_reached(axis_system, timeout_seconds):
        """
        The function waits until the given axis system has reached target 
        position or until the timeout occurs.
        """
        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        result = False
        while (result == False) and not timer.is_expired():
            time.sleep(0.1)
            result = axis_system.is_target_position_reached()
        return result


    def step04_axis_system_enable(self):
        print("Enabling axis system...")
        self.rotaxys.enable(True)
        for i in range(self.rotaxys.get_axes_count()):
            axis = self.rotaxys.get_axis_device(i)
            self.assertTrue(axis.is_enabled())


    def step05_axis_system_homing(self):
        print("Moving to home position...")
        self.rotaxys.find_home()
        homing_attained = self.wait_axis_homing_attained(self.rotaxys, 10)
        self.assertTrue(homing_attained)


    def step06_positioning(self):
        print("Moving around...")
        point = namedtuple("point", ["x", "y"])
        positions = [point(-49.51, -121.49), 
                     point(49.26, -121.49),
                     point(-49.51, -58.50),
                     point( 49.26, -58.50)]
        for position in positions:
            print("Moving to position: ", position)
            self.rotaxys.move_to_postion_xy(position.x, position.y, 1)
            target_reached = self.wait_target_reached(self.rotaxys, 5)
            self.assertTrue(target_reached)

            print("Moving Z to position: ", 0)
            zaxis = self.rotaxys.get_axis_device(2)
            velocity_z = zaxis.get_velocity_max()
            print("velocity_z: ", velocity_z)
            zaxis.move_to_position(0, velocity_z)
            target_reached = self.wait_axis_target_reached(zaxis, 5)
            self.assertTrue(target_reached)

            max_z = zaxis.get_position_max()
            print("Moving Z to position: ", max_z)
            zaxis.move_to_position(max_z, velocity_z)
            target_reached = self.wait_axis_target_reached(zaxis, 5)
            self.assertTrue(target_reached)


    def step07_axes_disable(self):
        print("Disabling axis system...")
        self.rotaxys.enable(False)
        time.sleep(0.2)
        for i in range(self.rotaxys.get_axes_count()):
            axis = self.rotaxys.get_axis_device(i)
            self.assertFalse(axis.is_enabled())
            self.assertFalse(axis.is_in_fault_state())

    def step08_device_property(self):
        rotaxys360 = qmixmotion.AxisSystem()
        rotaxys360.lookup_by_name("rotAXYS360_1")
        print("rotAXYS360 device property 0: ", rotaxys360.get_device_property(0))
        value = 90
        rotaxys360.set_device_property(0, value)
        self.assertEqual(value, rotaxys360.get_device_property(0))

    def step25_capi_close(self):
        print("Closing bus...")
        self.bus.stop()
        self.bus.close()

if __name__ == '__main__':
    deviceconfig = sys.argv[1]
    del sys.argv[1:]
    unittest.main()
