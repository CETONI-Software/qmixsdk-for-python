import time
import test_common
import unittest
import sys

from qmixsdk import qmixbus

def print_event(event: qmixbus.Event):
    """
    Prints the event string and the information in the event
    """
    print(event.string)
    print("Event type: ", event.event_id)
    if event.event_id == qmixbus.EventId.device_emergency.value:
        print("Event device: ", event.device.get_device_name())
        print("Emergency error code: ", hex(event.data[0]))
        print("Emergency error message ", event.device.get_error_message(event.data[0]))
        return

    if event.event_id == qmixbus.EventId.device_guard.value:
        print("Event device: ", event.device.get_device_name())
        print("Guard event id: ", event.data[0])
        return

    if event.event_id == qmixbus.EventId.data_link_layer.value:
        print("Error code: ", hex(event.data[0]))
        return

    if event.event_id == qmixbus.EventId.error.value:
        print("Error code: ", hex(event.data[0]))
        return


class QmixEventQueueTestCase(test_common.QmixTestBase):
    """
    Test for python integration event queue reading
    """
    def step01_capi_open(self):
        """
        Opens the internal bus and starts communication
        """
        print("Opening bus with deviceconfig ", deviceconfig)
        self.bus = qmixbus.Bus()
        self.bus.open(deviceconfig, 0)
        self.bus.start()


    def step02_input_lookup(self):
        """
        Reads events from the event queue for 60 seconds
        """
        print("Reading event queue...")
        for i in range(60): # run for 60 seconds
            event = self.bus.read_event()
            if event.is_valid():
                print_event(event)
            else:
                print("Event queue is empty")
            time.sleep(1)


    def step03_capi_close(self):
        """
        Stops process data communication and closes the bus
        """
        print("Closing bus...")
        self.bus.stop()
        self.bus.close()

if __name__ == '__main__':
    deviceconfig = sys.argv[1]
    del sys.argv[1:]
    unittest.main()
