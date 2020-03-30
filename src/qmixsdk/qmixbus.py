import ctypes
import time
from enum import Enum
from collections import namedtuple
from . import _qmixloadlib

bus_api = _qmixloadlib.load_lib("labbCAN_Bus_API")


def throw_on_error(errorcode, api_function = None):
    """
    Throw an exception if the given errorcode indicates an error condition.

    All returned errors are negative
    """
    if errorcode < 0:
        raise DeviceError(errorcode, api_function)


class UnitPrefix(Enum):
    """
    Unit prefix for unit construction
    """
    unit = 0
    deci = -1
    centi = -2
    milli = - 3
    micro = -6

class TimeUnit(Enum):
    """
    Time unit identifiers for construction of derived units
    """
    per_second = 1
    per_minute = 60
    per_hour = 3600


class CommState(Enum):
    """
    Communication state identifiers for Bus.set_communication_state() function
    """
    stopped = 0x02
    configurable = 0x80
    operational = 0x01


class EventId(Enum):
    """
    Event identifiers for event sreturned by Bus.read_event() function
    """
    data_link_layer = 2
    error = 4
    device_emergency = 5
    device_guard = 6


class GuardEventId(Enum):
    """
    Identifiers dfor device_guard events read via Bus.read_event() function
    """
    nodeguard_err_occurred = 0
    nodeguard_err_resolved = 1
    heartbeat_err_occurred = 2
    heartbear_err_resolved = 3
    notestate_err = 4
    notestate_changed = 5


class Error(Exception):
    """
    Base class for exceptions in this module.
    """
    pass


class DeviceError(Error):
    """
    Exception for all device errors.

    This error contains the returned error code and the string representation
    of the error
    """

    def __init__(self, errorcode, api_function = None):
        msg = ctypes.create_string_buffer(255)
        bus_api.LCB_GetErrMsg(errorcode, msg, ctypes.sizeof(msg))
        # Call the base class constructor with the parameters it needs
        error_msg = ""
        if not api_function is None:
            error_msg = api_function + " caused error: "
        error_msg += msg.value.decode('ascii')
        super().__init__(error_msg, errorcode)
        self.errorcode = errorcode


class PollingTimer:
    """
    Simple polling timer.

    This is the declaration of a simple polling timer class. This timer
    is not active - that means it is no alarm timer. In order to use the
    timer and time stamp functionality of this timer it has to be polled
    in regular intervals.
    """
    def __init__(self, period_ms = 0):
        self.period_ms = period_ms
        self.set_timestamp(period_ms)

    @staticmethod
    def get_msecs():
        """
        Helper funtion that returns a monotonic millisecond clock value
        """
        return time.monotonic() * 1000

    def is_expired(self):
        """
        Returns true if timer is expired.
        """
        return self.get_msecs() > self.expiration_time

    def set_timestamp(self, period_ms):
        """
        Set timer expiration time.
        """
        self.period_ms = period_ms
        self.expiration_time = self.get_msecs() + period_ms

    def set_period(self, period_ms):
        """
        Set timer period
        """
        self.period_ms = period_ms

    def restart(self):
        """
        Restarts timer

        This function set a new time stamp value according to internal timer
        period.
        """
        self.set_timestamp(self.period_ms)

    def restart_from(self, start_msecs):
        """
        Restarts the timer - takes the given start time as base for
       expiration time calculation.
        """
        self.expiration_time = start_msecs + self.period_ms

    def elapsed_msecs(self):
        """
        Returns the number of milliseconds that have elapsed since the last
	    time restart() was called or since timer was constructed.
        """
        return self.get_msecs() + self.period_ms - self.expiration_time

    def get_msecs_to_expiration(self):
        """
        Returns the remaining milliseconds till timer expiration
        """
        return 0 if self.is_expired() else self.expiration_time - self.get_msecs()

    def wait_until(self, fun, expected_result, *args):
        """
        This function waits until the function given in fun parameter returns
        true or until the timer expires
        """
        self.restart()
        result = fun(*args)
        while (result != expected_result) and not self.is_expired():
            time.sleep(0.1)
            result = fun(*args)
        return result == expected_result



class HandleOwner:
    """
    Base class for all Qmix devices and channels that use a device handle
    """
    def __init__(self, handle=ctypes.c_longlong()):
        self.handle = handle



class Device(HandleOwner):
    """
    Base class for all Qmix device that provides some common functionality
    for all devices
    """
    def __init__(self, handle=ctypes.c_longlong()):
        super().__init__(handle)


    def get_device_name(self):
        """
        Query name of this device
        """
        name = ctypes.create_string_buffer(255)
        result = bus_api.LCB_GetDevName(self.handle, name, ctypes.sizeof(name))
        throw_on_error(result)
        return name.value.decode('ascii')


    def read_last_error_code(self):
        """
        Read last device error from a  device.
        """
        errorcode = ctypes.c_ulong()
        result = bus_api.LCB_ReadLastDevErr(self.handle, ctypes.byref(errorcode))
        throw_on_error(result)
        return errorcode.value


    def get_error_message(self, errorcode):
        """
        Translates a given error code into a human readable string
        """
        msg = ctypes.create_string_buffer(255)
        result = bus_api.LCB_GetDevErrMsg(self.handle, ctypes.c_ulong(errorcode), msg, ctypes.sizeof(msg))
        if result < 0:
            return ""
        else:
            return msg.value.decode('ascii')


    def read_last_error(self):
        """
        Returns an error as named tuple with error code and error message
        """
        code = self.read_last_error_code()
        msg = self.get_error_message(code)
        error = namedtuple("error", ["code", "message"])
        return error(code, msg)


    def set_communication_state(self, state : CommState):
        """
        Set device in a configurable state.
        
        Some device parameters are only writeable if the device is not
        operational but in a configurable state. The function LCB_WriteDevParam()
        might require to set the device into an configurable state.
        To set the device into a configurable state, this function should
        be called with the parameter "configurable". If the configuration
        is finished, the device should be set operational again by calling
        this function with the parameter "operational".
        """
        result = bus_api.LCB_SetCommState(self.handle, state.value)
        throw_on_error(result)

    
    def get_node_id(self):
        """
        Query node identifier of specific device

        Some devices, such as CANopen devices, have a unique node
        identifier. This function returns this identifier
        """
        result = bus_api.LCB_GetNodeId(self.handle)
        throw_on_error(result)
        return result if result >= 0 else -1


    def set_device_property(self, property_id : int, value : float):
        """
        Function for setting a device specific property.

        Devices may support special device properties that are not accessible
        via the common device specific API. Use this function to set the value
        of a certain property by providing a property ID and a value.
        """
        result = bus_api.LCB_SetDeviceProperty(self.handle, property_id, ctypes.c_double(value))
        throw_on_error(result)


    def get_device_property(self, property_id: int):
        """
        Function for reading a device specific property.
        """
        device_property = ctypes.c_double()
        result = bus_api.LCB_GetDeviceProperty(self.handle, property_id,
            ctypes.byref(device_property))
        throw_on_error(result)
        return device_property.value


class Event:
    """
    Encapsulates event data when reading from event queue
    """
    def __init__(self):
        self.event_id = -1
        self.device = Device(0)
        self.data = []
        self.string = ""

    def is_valid(self):
        """
        Returns true if the internal device identifier is valid
        Use this function to test, if the read event function returned
        a valid event or if the event queue is empty
        """
        return self.event_id > -1



class Bus:
    """
    The bus class represents a kind of logical software bus all devices
    are connected to.
    """
    @staticmethod
    def open(device_config_path, plugin_search_path):
        """ 
        Initializes resources for a LabCanBus instance, connects to LabCanBus
        and scans for connected devices.
        """
        result = bus_api.LCB_Open(ctypes.c_char_p(device_config_path.encode('ascii')), 0)
        throw_on_error(result, "LCB_Open")


    #---------------------------------------------------------------------------
    # Initialization
    @staticmethod
    def start():
        """
        Start network communication.
        
        This function sets all connected devices into state operational and
        enabled. After a call to this function it is possible to access the
        connected devices.
        """
        result = bus_api.LCB_Start()
        throw_on_error(result)


    @staticmethod
    def stop():
        """
        Stop network communication.

        This function stops network communication and closes the CAN device
        driver. The function should be called by application before close()
        """
        result = bus_api.LCB_Stop()
        throw_on_error(result)


    @staticmethod
    def close():
        """
        Close LabCanBus instance.
        This call deletes all internal data structures and frees all allocated
        resources
        """
        result = bus_api.LCB_Close()
        throw_on_error(result)

    
    @staticmethod
    def log(message):
        """
        Write one message into log file.
        """
        result = bus_api.LCB_Log(ctypes.c_char_p(message.encode('ascii')))
        throw_on_error(result)

    #---------------------------------------------------------------------------
    # Error / event handling
    @staticmethod
    def get_err_msg(errorcode):
        """
        Get descriptive error message for a certain error return code.
        """
        msg = ctypes.create_string_buffer(255)
        bus_api.LCB_GetErrMsg(errorcode, msg, ctypes.sizeof(msg))
        return msg.value.decode('ascii')

    @staticmethod
    def read_event():
        """
        Try to read one event from the lab event queue.
        The internal queue stores events like network events, emergency events
        of single devices. This function tries to read one event from this queue
        and returns immediately with an invalid event if the queue is empty.
        """
        event_id = ctypes.c_long()
        device_handle = ctypes.c_longlong()
        data1 = ctypes.c_long()
        data2 = ctypes.c_long()
        event_id = ctypes.c_long()
        event_string = ctypes.create_string_buffer(255)
        result = bus_api.LCB_ReadEventEx(ctypes.byref(event_id),
                                         ctypes.byref(device_handle),
                                         ctypes.byref(data1),
                                         ctypes.byref(data2),
                                         event_string,
                                         ctypes.sizeof(event_string))
        if result == -0xB: # -ERR_AGAIN
            return Event()
        throw_on_error(result)
        event = Event()
        event.event_id = event_id.value
        event.device = Device(device_handle)
        event.data = [data1.value, data2.value]
        event.string = event_string.value.decode('ascii')
        return event
