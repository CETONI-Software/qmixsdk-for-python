import ctypes
from . import qmixbus
from . import qmixvalve
import sys
from enum import Enum
from collections import namedtuple
from .qmixbus import UnitPrefix, TimeUnit

# Ensure that the shared library is in the search path
if sys.platform.startswith('win32'):
    pump_api = ctypes.windll.LoadLibrary(r"labbCAN_Pump_API.dll")
else:
    pump_api = ctypes.cdll.LoadLibrary(r"liblabbCAN_Pump_API.so")


class VolumeUnit(Enum):
    litres = 68


class Pump(qmixbus.Device):
    """
    A pump presents the QmixSDK pump API as a python class
    """
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)

    #-------------------------------------------------------------------------
    # Initialisaton
    @staticmethod
    def get_no_of_pumps():
        result = pump_api.LCP_GetNoOfPumps()
        qmixbus.throw_on_error(result)
        return result


    def lookup_by_name(self, name):
        """
        Lookup for a pump device by its name.
        Initialize internal pump handle using the given name.
        """
        self.handle = ctypes.c_longlong()
        result = pump_api.LCP_LookupPumpByName(ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_by_device_index(self, index):
        """
        Get pump handle by its index.
        Initialize the internal pump handle using the fiven index.
        """
        self.handle = ctypes.c_longlong()
        result = pump_api.LCP_GetPumpHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    #-------------------------------------------------------------------------
    # Configuration
    def set_volume_unit(self, prefix : UnitPrefix, volume_unit : VolumeUnit):
        """
        Sets the default volume unit

        All parameters of subsequent dosing function calls are given in this new
        unit.
        """
        result = pump_api.LCP_SetVolumeUnit(self.handle, prefix.value, volume_unit.value)
        qmixbus.throw_on_error(result)


    def get_volume_unit(self):
        """
        Queries the current volume unit used for all dosage functions.
        Returns the volume unit as named tuple
        """
        prefix = ctypes.c_int()
        volume_unit = ctypes.c_int()
        result = pump_api.LCP_GetVolumeUnit(self.handle, ctypes.byref(prefix), ctypes.byref(volume_unit))
        qmixbus.throw_on_error(result)
        unit = namedtuple("unit", ["prefix", "unitid"])
        return unit(UnitPrefix(prefix.value), VolumeUnit(volume_unit.value))


    def set_flow_unit(self, prefix : UnitPrefix, volume_unit : VolumeUnit, time_unit : TimeUnit):
        """
        Sets the flow unit for a certain pump.

        The flow unit defines the unit to be used for all flow values passed
        to API functions or retrieved from API functions.
        """
        result = pump_api.LCP_SetFlowUnit(self.handle, prefix.value, volume_unit.value,
            time_unit.value)
        qmixbus.throw_on_error(result)


    def get_flow_unit(self):
        """
        Queries the current flow unit used for passing flow values.
        Returns the flow unit as named tuple
        """
        prefix = ctypes.c_int()
        volume_unit = ctypes.c_int()
        time_unit = ctypes.c_int()
        result = pump_api.LCP_GetFlowUnit(self.handle, ctypes.byref(prefix), 
            ctypes.byref(volume_unit), ctypes.byref(time_unit))
        qmixbus.throw_on_error(result)
        unit = namedtuple("unit", ["prefix", "unitid", "time_unitid"])
        return unit(UnitPrefix(prefix.value), VolumeUnit(volume_unit.value), TimeUnit(time_unit.value))

    
    def get_flow_rate_max(self):
        """
        Get maximum flow rate that is realizable with current dosing unit configuration.

        The maximum flow rate depends on the mechanical configuration of the
        dosing unit (gear) and on the syringe configuration. If larger syringes
        are used then larger flow rates are realizable.
        """
        maxflow = ctypes.c_double()
        result = pump_api.LCP_GetFlowRateMax(self.handle, ctypes.byref(maxflow))
        qmixbus.throw_on_error(result)
        return maxflow.value


    #-------------------------------------------------------------------------
    # Syringe Configuration
    def get_syringe_param(self):
        """
        Read syringe parameters.

        Returns the syringe parameters as named touple.
        """
        inner_diameter_mm = ctypes.c_double()
        max_piston_stroke_mm  = ctypes.c_double()
        result = pump_api.LCP_GetSyringeParam(self.handle, ctypes.byref(inner_diameter_mm),
            ctypes.byref(max_piston_stroke_mm))
        qmixbus.throw_on_error(result)
        syringe = namedtuple("syringe", ["inner_diameter_mm", "max_piston_stroke_mm"])
        return syringe(inner_diameter_mm.value, max_piston_stroke_mm.value)


    def set_syringe_param(self, inner_diameter_mm, max_piston_stroke_mm):
        """
        Set syringe parameters.

        If you change the syringe in one device, you need to setup the new
        syringe parameters to get proper conversion of flow rate und volume
        """
        result = pump_api.LCP_SetSyringeParam(self.handle, ctypes.c_double(inner_diameter_mm),
            ctypes.c_double(max_piston_stroke_mm))
        qmixbus.throw_on_error(result)


    def get_volume_max(self):
        """
        Returns the maximum volume a pump can aspirate into its container (syringe)
        """
        maxvolume = ctypes.c_double()
        result = pump_api.LCP_GetVolumeMax(self.handle, ctypes.byref(maxvolume))
        qmixbus.throw_on_error(result)
        return maxvolume.value

    #-------------------------------------------------------------------------
    # Pump control 
    def calibrate(self):
        """
        Executes a reference move for a syringe pump.
        """
        result = pump_api.LCP_SyringePumpCalibrate(self.handle)
        qmixbus.throw_on_error(result)

    
    def set_fill_level(self, level, flow):
        """
        Pumps fluid with the given flow rate until the requested fill level is reached.

        Depending on the requested fill level given in Level parameter this
        function may cause aspiration or dispension of fluid. This function only
        works properly for pump devices that support a fill level (eg. syringe
        pumps). Pumps like peristaltic pumps do not support a fill level and the
        function returns an error for unsupported pump types.
        """
        result = pump_api.LCP_SetFillLevel(self.handle, ctypes.c_double(level),
            ctypes.c_double(flow))
        qmixbus.throw_on_error(result)


    def pump_volume(self, volume, flow):
        """
        Pump a certain volume with a certain flow rate.
        """
        result = pump_api.LCP_PumpVolume(self.handle, ctypes.c_double(volume),
            ctypes.c_double(flow))
        qmixbus.throw_on_error(result)


    def dispense(self, volume, flow):
        """
        Dispense a certain volume with a certain flow rate.
        """
        result = pump_api.LCP_Dispense(self.handle, ctypes.c_double(volume),
            ctypes.c_double(flow))
        qmixbus.throw_on_error(result)


    def aspirate(self, volume, flow):
        """
        Aspirate a certain volume with a certain flow rate.
        """
        result = pump_api.LCP_Aspirate(self.handle, ctypes.c_double(volume),
            ctypes.c_double(flow))
        qmixbus.throw_on_error(result)


    def generate_flow(self, flow):
        """
        Generate a continuous flow.

        A negative flow indicates aspiration and a positiove flow indicates
        dispension.
        """
        result = pump_api.LCP_GenerateFlow(self.handle, ctypes.c_double(flow))
        qmixbus.throw_on_error(result)


    def stop_pumping(self):
        """
        Immediately stop pumping.
        """
        result = pump_api.LCP_StopPumping(self.handle)
        qmixbus.throw_on_error(result)


    @staticmethod
    def stop_all_pumps():
        """
        Immediately stop pumping off all pumps.
        """
        result = pump_api.LCP_StopAllPumps()
        qmixbus.throw_on_error(result)


    
    #-------------------------------------------------------------------------
    # Pump status 
    def get_flow_is(self):
        """
        Read the actual flow rate.
        """
        flow = ctypes.c_double()
        result = pump_api.LCP_GetFlowIs(self.handle, ctypes.byref(flow))
        qmixbus.throw_on_error(result)
        return flow.value


    def get_target_volume(self):
        """
        Read the target volume.

        This function simply returns the set target volume value
        """
        volume = ctypes.c_double()
        result = pump_api.LCP_GetTargetVolume(self.handle, ctypes.byref(volume))
        qmixbus.throw_on_error(result)
        return volume.value


    def get_dosed_volume(self):
        """
        Get the already dosed volume since last start of dosage.
        """
        volume = ctypes.c_double()
        result = pump_api.LCP_GetDosedVolume(self.handle, ctypes.byref(volume))
        qmixbus.throw_on_error(result)
        return volume.value


    def get_fill_level(self):
        """
        Returns the actual fill level of the pump.

        This function returns valid results only for pumps that support a fill level
        (eg. syringe pumps). Peristaltic pumps do not support fill level.
        For a syringe pump this function returns the current syringe fill level
        """
        level = ctypes.c_double()
        result = pump_api.LCP_GetFillLevel(self.handle, ctypes.byref(level))
        qmixbus.throw_on_error(result)
        return level.value


    def is_pumping(self):
        """
        Check if device is currently stopped or dosing.
        """
        result = pump_api.LCP_IsPumping(self.handle)
        qmixbus.throw_on_error(result)
        return True if result > 0 else False


    def is_calibration_finished(self):
        """
        Checks if calibration is finished.
        """
        result = pump_api.LCP_IsCalibrationFinished(self.handle)
        qmixbus.throw_on_error(result)
        return True if result > 0 else False   


    #-------------------------------------------------------------------------
    # Pump drive functions
    def is_enabled(self):
        """
        Query if pump drive is enabled.

        Only if the pump drive is enabled it is possible to pump fluid
        """
        result = pump_api.LCP_IsEnabled(self.handle)
        qmixbus.throw_on_error(result)
        return True if result > 0 else False

    
    def is_in_fault_state(self):
        """
        Check if pump is in a fault state.

        If the device is in fault state then it is necessary to call
        clear_fault() to clear the fault state and then enable()
        To enable the pump drive
        """
        result = pump_api.LCP_IsInFaultState(self.handle)
        qmixbus.throw_on_error(result)
        return True if result > 0 else False


    def clear_fault(self):
        """
        Clear fault condition.

        This is some kind of error acknowledge that clears the last fault and
        sets the device in an error free state. If the function
        LCP_IsInFaultState(void) indicates that device is in fault state, then
        this function may clear the fault. If the device is still in fault state
        after this function was called then a serious failure occurred
        """
        result = pump_api.LCP_ClearFault(self.handle)
        qmixbus.throw_on_error(result)


    def enable(self, enable):
        """
        Set pump drive in enabled or disabled state

        If the drive is enabled, then power is applied to the output power
        stage and the drive starts regulatig to keep its current position.
        """
        if enable:
            result = pump_api.LCP_Enable(self.handle)
        else:
            result = pump_api.LCP_Disable(self.handle) 
        qmixbus.throw_on_error(result)
        


    def get_position_counter_value(self):
        """
        Query the value of the internal drive position counter.

        You can store this value and restore it later when with the
        restore_position_counter_value() function.
        """
        counter = ctypes.c_long()
        result = pump_api.LCP_GetDrivePosCnt(self.handle, ctypes.byref(counter))
        qmixbus.throw_on_error(result)
        return counter.value


    def restore_position_counter_value(self, counter):
        """
        Restore internal hardware position counter value of pump drive.

        The function restores the internal position counter value
        saved with get_position_counter_value()
        """
        result = pump_api.LCP_RestoreDrivePosCnt(self.handle, ctypes.c_long(counter))
        qmixbus.throw_on_error(result)


    def get_pump_name(self):
        """
        Returns the device name of the pump
        """
        name = ctypes.create_string_buffer(255)
        result = pump_api.LCP_GetPumpName(self.handle, name, ctypes.sizeof(name))
        qmixbus.throw_on_error(result)
        return name.value.decode('ascii')


    #-------------------------------------------------------------------------
    # Valve functions
    def has_valve(self):
        """
        Returns true if this pump has a valve
        """
        result = pump_api.LCP_HasValve(self.handle)
        qmixbus.throw_on_error(result)
        return True if result > 0 else False


    def get_valve(self):
        """
        Returns the valve of this pump
        """
        if not hasattr(self, "valve"):
            valve_handle = ctypes.c_longlong()
            result = pump_api.LCP_GetValveHandle(self.handle,
                ctypes.byref(valve_handle))
            qmixbus.throw_on_error(result)
            self.valve = qmixvalve.Valve(valve_handle)
        return self.valve
