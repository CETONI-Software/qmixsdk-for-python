import ctypes
from . import qmixbus
from . import _qmixloadlib

valve_api = _qmixloadlib.load_lib("labbCAN_Valve_API")


class Valve(qmixbus.Device):
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)

    #-------------------------------------------------------------------------
    # Initialisaton
    @staticmethod
    def get_no_of_valves():
        result = valve_api.LCV_GetNoOfValves()
        qmixbus.throw_on_error(result)
        return result


    def lookup_by_name(self, name):
        """
        Lookup for a valve device by its name.
        Initialize internal valve handle using the given name.
        """
        self.handle = ctypes.c_longlong()
        result = valve_api.LCV_LookupValveByName(ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_by_device_index(self, index):
        """
        Get pump valve by its device index.
        Initialize the internal pump handle using the given index.
        """
        self.handle = ctypes.c_longlong()
        result = valve_api.LCV_GetValveHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def number_of_valve_positions(self):
        """
        Returns the number of valve positions
        Each valve has a number of available valve positions. I.e. a switching
        valve has two positions or a rotation valve can have 4 or even more
        positions.
        """
        result = valve_api.LCV_NumberOfValvePositions(self.handle)
        qmixbus.throw_on_error(result)
        return result


    def actual_valve_position(self):
        """
        Returns the actual logical valve position.

        Each valve position is identified by a logical valve position identifier
        from 0 - number of valve positions - 1. This function returns the logical
        valve position identifier for the current valve position.
        """
        result = valve_api.LCV_ActualValvePosition(self.handle)
        qmixbus.throw_on_error(result)
        return result


    def switch_valve_to_position(self, logical_valve_position):
        """
        Switches the valve to a certain logical valve position.
        """
        result = valve_api.LCV_SwitchValveToPosition(self.handle, ctypes.c_int(logical_valve_position))
        qmixbus.throw_on_error(result)
