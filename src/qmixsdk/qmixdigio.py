import ctypes
from . import qmixbus
from . import _qmixloadlib

digio_api = _qmixloadlib.load_lib("labbCAN_DigIO_API")


class DigitalChannel(qmixbus.HandleOwner):
    """
    Base class for digital in and digital out channel device with common 
    functionality
    """
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)

    def get_name(self):
        """
        Query name of this channel
        """
        name = ctypes.create_string_buffer(255)
        result = digio_api.LCDIO_GetChanName(self.handle, name, ctypes.sizeof(name))
        qmixbus.throw_on_error(result)
        return name.value.decode('ascii')


    @staticmethod
    def lookup_io_device_by_name(name):
        """
        Lookup an digital I/O device by its name.
        """
        handle = ctypes.c_longlong()
        result = digio_api.LCDIO_LookupIoDeviceByName(
            ctypes.c_char_p(name.encode('ascii')), ctypes.byref(handle))
        qmixbus.throw_on_error(result)
        return qmixbus.Device(handle)


class DigitalInChannel(DigitalChannel):
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)

    #---------------------------------------------------------------------------
    # Initialisation
    @staticmethod
    def get_no_of_channels():
        """
        Query number of available digital input channels
        """
        result = digio_api.LCDIO_GetNoOfInputChannels()
        qmixbus.throw_on_error(result)
        return result


    def lookup_channel_by_name(self, name):
        """
        Lookup for an digital input channel by its name.
        """
        self.handle = ctypes.c_longlong()
        result = digio_api.LCDIO_LookupInChanByName(
                ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_channel_by_index(self, index):
        """
        Get input channel handle by its index.
        """
        self.handle = ctypes.c_longlong()
        result = digio_api.LCDIO_GetInChanHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def is_on(self):
        """
        Read digital input state of channel.
        """
        result = digio_api.LCDIO_IsInputOn(self.handle)
        qmixbus.throw_on_error(result)
        return True if result > 0 else False


class DigitalOutChannel(DigitalChannel):
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)

    #---------------------------------------------------------------------------
    # Initialisation
    @staticmethod
    def get_no_of_channels():
        """
        Query number of available digital output channels
        """
        result = digio_api.LCDIO_GetNoOfOutputChannels()
        qmixbus.throw_on_error(result)
        return result


    def lookup_channel_by_name(self, name):
        """
        Lookup for an digital output channel by its name.
        """
        self.handle = ctypes.c_longlong()
        result = digio_api.LCDIO_LookupOutChanByName(
                ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_channel_by_index(self, index):
        """
        Get output channel handle by its index.
        """
        self.handle = ctypes.c_longlong()
        result = digio_api.LCDIO_GetOutChanHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)

    
    def write_on(self, on):
        """
        Switch digital output channel on/off.
        """
        on = 1 if on else 0
        result = digio_api.LCDIO_WriteOn(self.handle, on)
        qmixbus.throw_on_error(result)

    
    def is_output_on(self):
        """
        Return the state of a digital output channel - True if it is on
        """
        result = digio_api.LCDIO_IsOutputOn(self.handle)
        qmixbus.throw_on_error(result)
        return True if result > 0 else False
