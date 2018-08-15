import ctypes
from . import qmixbus
from . import qmixvalve
import sys
from enum import Enum
from collections import namedtuple
from .qmixbus import UnitPrefix, TimeUnit

# Ensure that the shared library is in the search path
if sys.platform.startswith('win32'):
    motion_api = ctypes.windll.LoadLibrary(r"labbCAN_MotionControl_API.dll")
else:
    motion_api = ctypes.cdll.LoadLibrary(r"liblabbCAN_MotionControl_API.so")


MAXIMUM_VELOCITY = 0xFFFFFFFF


class PositionUnit(Enum):
    meters = 1
    revolutions = 254
    degree = 65
    radian = 16
    device = 0


class Axis(qmixbus.Device):  
    """
    An QmixSDK axis instance
    """
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)  


    #-------------------------------------------------------------------------
    # API Initialisaton
    @staticmethod
    def get_axes_count():
        """
        Returns the number of available axes registered in the Qmix SDK 
        environment instance
        """
        result = motion_api.LCA_AxisCount()
        qmixbus.throw_on_error(result)
        return result


    def lookup_by_name(self, name):
        """
        Lookup an axis by its name.
        """
        self.handle = ctypes.c_longlong()
        result = motion_api.LCA_LookupAxisByName(ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_by_device_index(self, index):
        """
        Get an axis handle by its index.
        """
        self.handle = ctypes.c_longlong()
        result = motion_api.LCA_GetAxisHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def is_in_fault_state(self):
        """
        Check if axis is in a fault state.
        """
        result = motion_api.LCA_IsAxisInFaultState(self.handle)
        qmixbus.throw_on_error(result) 
        return True if result > 0 else False       


    def clear_fault(self):
        """
        Clear fault condition.

        This is some kind of error acknowledge that clears the last fault and
        sets the device in an error free state. You can enable an exis
        only, if all faults are cleared
        """
        result = motion_api.LCA_ClearAxisFault(self.handle)
        qmixbus.throw_on_error(result)   


    def is_enabled(self):
        """
        Query if axis is enabled.
        """
        result = motion_api.LCA_IsAxisEnabled(self.handle)
        qmixbus.throw_on_error(result) 
        return True if result > 0 else False


    def enable(self, enable):
        """
        Set single axis into enabled state.  

        If the axis is in fault state, you need to clear the fault state first
        by calling clear_fault()
        """
        if enable:
            result = motion_api.LCA_EnableAxis(self.handle)
        else:
            result = motion_api.LCA_DisableAxis(self.handle)
        qmixbus.throw_on_error(result)       


    def find_home(self):
        """
        Move single axis into its home position.
        """
        result = motion_api.LCA_FindHomeOfAxis(self.handle)
        qmixbus.throw_on_error(result)


    def is_homing_position_attained(self):
        """
        Check if homing position of the given axis system is attained.
        """
        result = motion_api.LCA_IsAxisHomingPosAttained(self.handle)
        qmixbus.throw_on_error(result)
        return result > 0


    def set_homing_switch_speed(self, speed):
        """
        Set speed for move to homing or limit switch.
        """
        result = motion_api.LCA_SetAxisHomingSwitchSpeed(self.handle, ctypes.c_double(speed))
        qmixbus.throw_on_error(result) 


    def get_homing_switch_speed(self):
        """
        Query speed for move to homing or limit switch.
        """   
        speed = ctypes.c_double()
        result = motion_api.LCA_GetAxisHomingSwitchSpeed(self.handle, ctypes.byref(speed))
        qmixbus.throw_on_error(result)
        return speed.value        

    
    def set_homing_offset(self, offset):
        """
        Set the home offset used for homing moves.
        """
        result = motion_api.LCA_SetAxisHomingOffset(self.handle, ctypes.c_double(offset))
        qmixbus.throw_on_error(result)        


    def get_position_counter(self):
        """
        Query the value of the internal axis position counter.

        You can readout the position counter and save the value before you
        power down your devices. Later on next start you can restore the saved
        value by calling restore_position_counter() function with the saved
        value
        """
        counter = ctypes.c_long()
        result = motion_api.LCA_GetAxisPosCnt(self.handle, ctypes.byref(counter))
        qmixbus.throw_on_error(result)         
        return counter.value


    def restore_position_counter(self, counter):
        """
        Restore internal hardware position counter value.

        The function restores the internal position counter value
        saved via get_position_counter().
        """
        result = motion_api.LCA_RestoreAxisPosCnt(self.handle, ctypes.c_long(counter))
        qmixbus.throw_on_error(result) 


    def set_position_unit(self, prefix : qmixbus.UnitPrefix, unit : PositionUnit):
        """
        Set default position unit 
        """
        result = motion_api.LCA_SetDefaultPosUnit(self.handle, prefix.value, unit.value)
        qmixbus.throw_on_error(result)

    
    def get_position_unit(self):
        """
        Queries the default position unit.
        """
        prefix = ctypes.c_int()
        position_unit = ctypes.c_int()
        result = motion_api.LCA_GetDefaultPosUnit(self.handle, ctypes.byref(prefix), 
            ctypes.byref(position_unit))
        qmixbus.throw_on_error(result)
        unit = namedtuple("unit", ["prefix", "unitid"])
        return unit(UnitPrefix(prefix.value), PositionUnit(position_unit.value))   


    def set_velocity_unit(self, prefix : qmixbus.UnitPrefix, unit : PositionUnit,
        time_unit : qmixbus.TimeUnit):
        """
        Set default velocity unit.
        """
        result = motion_api.LCA_SetDefaultVelUnit(self.handle, prefix.value, unit.value,
            time_unit.value)
        qmixbus.throw_on_error(result)


    def get_velocity_unit(self):
        """
        Queries the default velocity unit.
        """
        prefix = ctypes.c_int()
        pos_unit = ctypes.c_int()
        time_unit = ctypes.c_int()
        result = motion_api.LCA_GetDefaultVelUnit(self.handle, ctypes.byref(prefix), 
            ctypes.byref(pos_unit), ctypes.byref(time_unit))
        qmixbus.throw_on_error(result)
        unit = namedtuple("unit", ["prefix", "unitid", "time_unitid"])
        return unit(UnitPrefix(prefix.value), PositionUnit(pos_unit.value), TimeUnit(time_unit.value))
   

    def get_position_min(self):
        """
        Query minimum position limit for axis.
        """
        limit = ctypes.c_double()
        result = motion_api.LCA_GetAxisPosMin(self.handle, ctypes.byref(limit))
        qmixbus.throw_on_error(result)
        return limit.value


    def get_position_max(self):
        """
        Query maximum position limit for axis.
        """
        limit = ctypes.c_double()
        result = motion_api.LCA_GetAxisPosMax(self.handle, ctypes.byref(limit))
        qmixbus.throw_on_error(result)
        return limit.value


    def get_velocity_max(self):
        """
        Query maximum velocity for axis.
        """
        limit = ctypes.c_double()
        result = motion_api.LCA_GetAxisVelMax(self.handle, ctypes.byref(limit))
        qmixbus.throw_on_error(result)
        return limit.value

    
    #-------------------------------------------------------------------------
    # Axis motion functions
    def move_to_position(self, position, velocity):
        """
        Move axis to a certain absolute position with a certain velocity.
        """
        result = motion_api.LCA_MoveToPos(self.handle, ctypes.c_double(position),
            ctypes.c_double(velocity), 0)
        qmixbus.throw_on_error(result)


    def move_distance(self, distance, velocity):
        """
        Move a certain distance.

        This is a relytive position move in one or another direction. The sign
        of the distance value defines the direction
        """ 
        result = motion_api.LCA_MoveDistance(self.handle, ctypes.c_double(distance),
            ctypes.c_double(velocity), 0)
        qmixbus.throw_on_error(result)


    def move_with_velocity(self, velocity):
        """
        Perform a velocity move.

        The sign of the velocity value defines the direction. The axis moves
        until it is stopped or until a limit is reached.
        """
        result = motion_api.LCA_MoveWithVelocity(self.handle,
            ctypes.c_double(velocity), 0)
        qmixbus.throw_on_error(result)    


    def stop_move(self):
        """
        Stop axis movement of this axis
        """    
        result = motion_api.LCA_StopMoveOfAxis(self.handle)
        qmixbus.throw_on_error(result) 


    def is_stopped(self):
        """
        Check if drive is stopped or if it is moving.
        """
        result = motion_api.LCA_IsAxisStopped(self.handle)
        qmixbus.throw_on_error(result) 
        return result > 0


    def get_actual_position(self):
        """
        Query the actual position of the axis.
        """
        position = ctypes.c_double()
        result = motion_api.LCA_GetAxisPosIs(self.handle, ctypes.byref(position))
        qmixbus.throw_on_error(result) 
        return position.value


    def get_actual_velocity(self):
        """
        Query the actual position of the axis.
        """
        velocity = ctypes.c_double()
        result = motion_api.LCA_GetAxisVelIs(self.handle, ctypes.byref(velocity))
        qmixbus.throw_on_error(result) 
        return velocity.value


    def is_target_position_reached(self):
        """
        Check if axis reached its target position.
        """
        result = motion_api.LCA_IsAxisTargetPosReached(self.handle)
        qmixbus.throw_on_error(result) 
        return result > 0



class AxisSystem(qmixbus.Device):
    """
    An QmixSDK axis system instance
    """
    def __init__(self, handle = ctypes.c_longlong()):
        super().__init__(handle)

    
    #-------------------------------------------------------------------------
    # API Initialisation
    @staticmethod
    def get_axis_system_count():
        """
        Returns the number of registered and available axis systems
        """
        result = motion_api.LCA_GetNoOfAxisSystems()
        qmixbus.throw_on_error(result)
        return result


    def lookup_by_name(self, name):
        """
        Lookup an axis system by its name.
        """
        self.handle = ctypes.c_longlong()
        result = motion_api.LCA_LookupAxisSystemByName(ctypes.c_char_p(name.encode('ascii')), ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)


    def lookup_by_device_index(self, index):
        """
        Get an axis system handle by its index.
        """
        self.handle = ctypes.c_longlong()
        result = motion_api.LCA_GetAxisSystemHandle(index, ctypes.byref(self.handle))
        qmixbus.throw_on_error(result)

    
    def get_axes_count(self):
        """
        Returns the number of axes of this axis system.
        """
        result = motion_api.LCA_GetAxisSystemAxisNumber(self.handle)
        qmixbus.throw_on_error(result)
        return result


    def get_axis_device(self, index):
        """
        Returns the axis device for the given index
        """
        handle = ctypes.c_longlong()
        result = motion_api.LCA_GetAxisHandle(self.handle, ctypes.c_uint8(index),
            ctypes.byref(handle))
        qmixbus.throw_on_error(result)
        return Axis(handle)


    #-------------------------------------------------------------------------
    # Axis System Initialization
    def enable(self, enable):
        """
        Set all axis of an axis system into enabled (operational) state or
        into disabled state.
        """
        if enable:
            result = motion_api.LCA_Enable(self.handle)
        else:
            result = motion_api.LCA_Disable(self.handle)
        qmixbus.throw_on_error(result)
    

    def find_home(self):
        """
        Move all axes into its home position
        """
        result = motion_api.LCA_FindHome(self.handle)
        qmixbus.throw_on_error(result)



    def is_homing_position_attained(self):
        """
        Check if homing position of the given axis system is attained.

        Homing it attained, if all axes reached their homing position
        """
        result = motion_api.LCA_IsHomingPosAttained(self.handle)
        qmixbus.throw_on_error(result)
        return result > 0    


    #-------------------------------------------------------------------------
    # Axis System motion functions
    def move_to_postion_xy(self, position_x, position_y, velocity):
        """
        Moves XY positioning system to a certain XY position in coordinate space.
        """
        result = motion_api.LCA_MoveToPosXY(self.handle, ctypes.c_double(position_x),
            ctypes.c_double(position_y), ctypes.c_double(velocity))
        qmixbus.throw_on_error(result)


    def stop_move(self):
        """
        Stop movement of axis system - send stop command to all axis system axes.
        """
        result = motion_api.LCA_StopMove(self.handle)
        qmixbus.throw_on_error(result)


    #-------------------------------------------------------------------------
    # Axis System status
    def get_actual_position_xy(self):
        """
        Query the actual XY position of the axis system.

        Returns the XY position as named tuple
        """
        x = ctypes.c_double()
        y = ctypes.c_double()
        result = motion_api.LCA_GetActualPostitionXY(self.handle, 
            ctypes.byref(x), ctypes.byref(y))
        qmixbus.throw_on_error(result)
        position = namedtuple("position", ["x", "y"])
        return position(x.va, y.value)


    def is_target_position_reached(self):
        """
        Check if an axis system reached its target position.

        The target position is reached, if all axis devices of an axis system
        reached their target positions.
        """
        result = motion_api.LCA_IsTargetPosReached(self.handle)
        qmixbus.throw_on_error(result)
        return result > 0

    # Position marker functionality not implemented yet
    # will be implemented on request    

        
