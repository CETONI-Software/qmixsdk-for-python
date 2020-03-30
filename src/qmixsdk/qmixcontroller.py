import ctypes
from . import qmixbus
from enum import Enum
from collections import namedtuple
from . import _qmixloadlib

ctrl_api = _qmixloadlib.load_lib("labbCAN_Controller_API")


class LoopOutType(Enum):
    """
    This enumeration defines the output types for dynamic control channels.
    """
    analog = 0
    digital = 1
    digital_pwm = 2
    pump_flow = 3


class PIDParameter(Enum):
    """
    Identifier for all PID control loop parameter that can be changed via
    LCC_SetPIDParameter. Before your can use a control loop, you should
    properly set all control loop parameters. You can use the QmixElements
    software for PID parameter testing and PID tuning.
    """
    K = 0
    Ti = 1
    Td = 2
    derivative_gain_limit = 3
    Tt = 4
    max_U = 5
    min_U = 6
    diabled_U = 7
    initial_setpoint = 8
    sample_time = 9


class ControllerChannel(qmixbus.HandleOwner):
    """
    A controller channel provides the Qmix Controller API as a python class
    """
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)        


    #---------------------------------------------------------------------------
    # Initialisation
    @staticmethod
    def get_no_of_channels():
        """
        Query number of available controller channels
        """
        result = ctrl_api.LCC_GetNoOfControlChannels()
        qmixbus.throw_on_error(result)
        return result


    def lookup_channel_by_name(self, name):
        """
        Lookup for a controller channel by its name.
        """
        self.handle = ctypes.c_longlong()
        result = ctrl_api.LCC_LookupChanByName(
                ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_channel_by_index(self, index):
        """
        Get controller channel handle by its index.
        """
        self.handle = ctypes.c_longlong()
        result = ctrl_api.LCC_GetChannelHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    @staticmethod
    def create_pid_control_channel(analog_in : qmixbus.HandleOwner, 
        analog_out : qmixbus.HandleOwner, loop_output_type : LoopOutType):
        """
        Function for creation of dynamic PID control channels.
        """
        handle = ctypes.c_longlong()
        result = ctrl_api.LCC_CreatePIDControlChannel(analog_in.handle, analog_out.handle,
            loop_output_type.value, ctypes.byref(handle))
        qmixbus.throw_on_error(result)
        return ControllerChannel(handle)


    #---------------------------------------------------------------------------
    # Control Channel access
    def set_pid_parameter(self, pid_param : PIDParameter, value):
        """
        Set a single PID parameter
        """
        result = ctrl_api.LCC_SetPIDParameter(self.handle, pid_param.value,
            ctypes.c_double(value))
        qmixbus.throw_on_error(result)

    
    def enable_control_loop(self, enable):
        """
        Enables / disables a control loop.
        """
        result = ctrl_api.LCC_EnableControlLoop(self.handle, 1 if enable else 0)
        qmixbus.throw_on_error(result)


    def is_control_loop_enabled(self):
        """
        Returns True if the control loop is enabled.
        """
        result = ctrl_api.LCC_IsControlLoopEnabled(self.handle)
        qmixbus.throw_on_error(result)
        return True if result > 0 else False


    def write_setpoint(self, setpoint):
        """
        Write setpoint value to controller device.
        """
        result = ctrl_api.LCC_WriteSetPoint(self.handle, ctypes.c_double(setpoint))
        qmixbus.throw_on_error(result)


    def write_setpoint_unscaled(self, setpoint):
        """
        Write setpoint value to controller device - bypass scaling stage.
        """
        result = ctrl_api.LCC_WriteSetPointUnscaled(self.handle, ctypes.c_double(setpoint))
        qmixbus.throw_on_error(result)


    def get_setpoint(self):
        """
        Query setpoint value from device object.
        """
        setpoint = ctypes.c_double()
        result = ctrl_api.LCC_GetSetPoint(self.handle, ctypes.byref(setpoint))
        qmixbus.throw_on_error(result)
        return setpoint.value

    
    def read_actual_value(self):
        """
        Read actual value from device.
        """
        actual_value = ctypes.c_double()
        result = ctrl_api.LCC_ReadActualValue(self.handle, ctypes.byref(actual_value))
        qmixbus.throw_on_error(result)
        return actual_value.value

    
    def read_actual_value_unscaled(self):
        """
        Read actual value from device - bypass scaling.
        """
        actual_value = ctypes.c_double()
        result = ctrl_api.LCC_ReadActualValueUnscaled(self.handle, 
            ctypes.byref(actual_value))
        qmixbus.throw_on_error(result)
        return actual_value.value


    def read_status(self):
        """
        Read additional status information from device.
        """
        status = ctypes.c_ulong()
        result = ctrl_api.LCC_ReadStatus(self.handle, ctypes.byref(status))
        qmixbus.throw_on_error(result)
        return status.value


    def enable_software_scaling(self, enable):
        """
        Enable / disable software scaling.
        """
        result = ctrl_api.LCC_SetSwScalingO(self.handle, 
            ctypes.c_int(1) if enable else ctypes.c_int(0))
        qmixbus.throw_on_error(result)


    def set_scaling_param(self, factor, offset):        
        """
        Set software scaling parameters.

        These parameters are used to scale the measured value from device.
        These scaling parameters are independent from the device scaling
        parameters and the scaling is performed on the local machine.
        Scaled Value = (Process Value * Scaling Factor) + Scaling Offset.
        The default value for Scaling Factor is 1 and for Scaling Offset is 0.
        """
        result = ctrl_api.LCC_SetSwScalingParam(self.handle, ctypes.c_double(factor), 
            ctypes.c_double(offset))
        qmixbus.throw_on_error(result)


    def get_scaling_param(self): 
        """
        Query software scaling parameters.
        """
        factor = ctypes.c_double()
        offset = ctypes.c_double()
        result = ctrl_api.LCC_GetSwScalingParam(self.handle,
            ctypes.byref(factor), ctypes.byref(offset))
        qmixbus.throw_on_error(result)
        scaling = namedtuple("scaling", ["factor", "offset"])
        return scaling(factor.value, offset.value)


    @staticmethod
    def lookup_control_device_by_name(name):
        """
        Lookup a controller device by its name.

        Each control channel is attached to a certain control device. A control
        device can have a number of control channels.
        """
        handle = ctypes.c_longlong()
        result = ctrl_api.LCC_LookupCtrlDeviceByName(
            ctypes.c_char_p(name.encode('ascii')), ctypes.byref(handle))
        qmixbus.throw_on_error(result)
        return qmixbus.Device(handle)

    
    def get_name(self):
        """
        Query name of this channel.
        Each channel has a unique name that is configured in the XML files
        of the device configuration.
        """
        name = ctypes.create_string_buffer(255)
        result = ctrl_api.LCC_GetChanName(self.handle, name, ctypes.sizeof(name))
        qmixbus.throw_on_error(result)
        return name.value.decode('ascii')
