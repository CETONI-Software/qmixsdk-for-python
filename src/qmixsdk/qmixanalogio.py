import ctypes
from . import qmixbus
from collections import namedtuple
from . import _qmixloadlib

analogio_api = _qmixloadlib.load_lib("labbCAN_AnalogIO_API")


class AnalogChannel(qmixbus.HandleOwner):
    """
    Base class for analog in and analog out channel device with common 
    functionality
    """
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle) 

    def get_name(self):
        """
        Query name of this channel
        """
        name = ctypes.create_string_buffer(255)
        result = analogio_api.LCAIO_GetChanName(self.handle, name, ctypes.sizeof(name))
        qmixbus.throw_on_error(result)
        return name.value.decode('ascii')

    def get_io_device(self):
        """
        Returns the handle of the I/O device this channel is attached to
        """
        handle = ctypes.c_longlong()
        result = analogio_api.LCAIO_GetAnalogIoDevice(self.handle, ctypes.byref(handle))
        qmixbus.throw_on_error(result)
        return qmixbus.Device(handle)

    @staticmethod
    def lookup_io_device_by_name(name):
        """
        Lookup an analog I/O device by its name.
        """
        handle = ctypes.c_longlong()
        result = analogio_api.LCAIO_LookupAnalogIoDeviceByName(
            ctypes.c_char_p(name.encode('ascii')), ctypes.byref(handle))
        qmixbus.throw_on_error(result)
        return qmixbus.Device(handle)



class AnalogInChannel(AnalogChannel):
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)

    #---------------------------------------------------------------------------
    # Initialisation
    @staticmethod
    def get_no_of_channels():
        """
        Query number of available analog input channels
        """
        result = analogio_api.LCAIO_GetNoOfInputChannels()
        qmixbus.throw_on_error(result)
        return result


    def lookup_channel_by_name(self, name):
        """
        Lookup for an analog channel by its name.
        """
        self.handle = ctypes.c_longlong()
        result = analogio_api.LCAIO_LookupInChanByName(
                ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_channel_by_index(self, index):
        """
        Get analog channel handle by its index.
        """
        self.handle = ctypes.c_longlong()
        result = analogio_api.LCAIO_GetInChanHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def read_input(self):
        """
        Read analog input of this channel.
        """
        value = ctypes.c_double()
        result = analogio_api.LCAIO_ReadInput(self.handle, ctypes.byref(value))
        qmixbus.throw_on_error(result)
        return value.value


    def read_status(self):
        """
        Read additional status information from analog channel.
        """
        value = ctypes.c_ulong()
        result = analogio_api.LCAIO_ReadStatus(self.handle, ctypes.byref(value))
        qmixbus.throw_on_error(result)
        return value.value


    def enable_software_scaling(self, enable):
        """
        Enable / disable software scaling.
        """
        result = analogio_api.LCAIO_SetInputSwScalingOn(self.handle, 
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
        result = analogio_api.LCAIO_SetInputSwScalingParam(self.handle, ctypes.c_double(factor), 
            ctypes.c_double(offset))
        qmixbus.throw_on_error(result)


    def get_scaling_param(self): 
        """
        Query software scaling parameters.
        """
        factor = ctypes.c_double()
        offset = ctypes.c_double()
        result = analogio_api.LCAIO_GetInputSwScalingParam(self.handle,
            ctypes.byref(factor), ctypes.byref(offset))
        qmixbus.throw_on_error(result)
        scaling = namedtuple("scaling", ["factor", "offset"])
        return scaling(factor.value, offset.value)



class AnalogOutChannel(AnalogChannel):
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)

    #---------------------------------------------------------------------------
    # Initialisation
    @staticmethod
    def get_no_of_channels():
        """
        Query number of available analog input channels
        """
        result = analogio_api.LCAIO_GetNoOfOutputChannels()
        qmixbus.throw_on_error(result)
        return result


    def lookup_channel_by_name(self, name):
        """
        Lookup for an analog channel by its name.
        """
        self.handle = ctypes.c_longlong()
        result = analogio_api.LCAIO_LookupOutChanByName(
                ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_channel_by_index(self, index):
        """
        Get analog channel handle by its index.
        """
        self.handle = ctypes.c_longlong()
        result = analogio_api.LCAIO_GetOutChanHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def write_output(self, value):
        """
        Set analog output value of single channel.
        """
        result = analogio_api.LCAIO_WriteOutput(self.handle, ctypes.c_double(value))
        qmixbus.throw_on_error(result)

    def get_output_vaue(self):
        """
        Return the output value of this channel.
        """
        value = ctypes.c_double()
        result = analogio_api.LCAIO_GetOutputValue(self.handle, ctypes.byref(value))
        qmixbus.throw_on_error(result)
        return value.value

    def enable_software_scaling(self, enable):
        """
        Enable / disable software scaling.
        """
        result = analogio_api.LCAIO_SetOutputSwScalingOn(self.handle, 
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
        result = analogio_api.LCAIO_SetOutputSwScalingParam(self.handle, 
            ctypes.c_double(factor), ctypes.c_double(offset))
        qmixbus.throw_on_error(result)


    def get_scaling_param(self): 
        """
        Query software scaling parameters.
        """
        factor = ctypes.c_double()
        offset = ctypes.c_double()
        result = analogio_api.LCAIO_GetOutputSwScalingParam(self.handle,
            ctypes.byref(factor), ctypes.byref(offset))
        qmixbus.throw_on_error(result)
        scaling = namedtuple("scaling", ["factor", "offset"])
        return scaling(factor.value, offset.value)
