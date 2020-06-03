#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 27 14:17:29 2020

@author: Luca Barbera


"""
from tango import AttrWriteType, DevState, DebugIt, DevVarLong64Array
from tango.server import Device, attribute, command
import time
import ni_usb_6501 as ni


class NIUSB6501(Device):
    
    
    port3 = attribute(fget='read_port3',fset='write_port3',name='Port3',access=AttrWriteType.READ_WRITE,dtype=bool)
    
    port4 = attribute(fget='read_port4',fset='write_port4',name='Port4',access=AttrWriteType.READ_WRITE,dtype=bool)
    
    port5 = attribute(fget='read_port5',fset='write_port5',name='Port5',access=AttrWriteType.READ_WRITE,dtype=bool)
    
    port6 = attribute(fget='read_port6',fset='write_port6',name='Port6',access=AttrWriteType.READ_WRITE,dtype=bool)
    
    port7 = attribute(fget='read_port7',fset='write_port7',name='Port7',access=AttrWriteType.READ_WRITE,dtype=bool)
    
    
    
    
    
    def init_device(self):
        self.info_stream('Trying to establish connection')
        
        try:
            Device.init_device(self)
            self.dev = ni.get_adapter()
            self.set_state(DevState.ON)
            self.dev.set_io_mode(0b00000000,0b01111111,0b00000000)
            self.__ports = {3:False,4:False,5:False,6:False,7:False}
            self.__active = '0b00000000'
            self.dev.write_port(1,int(self.__active,2))
            self.info_stream('Connection established.')
            
        except:
            if not self.dev:
                self.error_stream('Connection could not be established')
                self.set_state(DevState.FAULT)
            else:
                #Connection already running (info_stream gets called in case
                #the init method is called more than once)
                self.info_stream('Connection has already been established in a prior run.')
                
        
    def read_port3(self):
        return self.__ports[3]
    
    def write_port3(self,state):
        self.change_port(3,state)
    
    def read_port4(self):
        return self.__ports[4]
    
    def write_port4(self,state):
        self.change_port(4,state)
    
    def read_port5(self):
        return self.__ports[5]
    
    def write_port5(self,state):
        self.change_port(5,state)
    
    def read_port6(self):
        return self.__ports[6]
    
    def write_port6(self,state):
        self.change_port(6,state)
    
    def read_port7(self):
        return self.__ports[7]
    
    def write_port7(self,state):
        self.change_port(7,state)

    @DebugIt()            
    def change_port(self, port, state):
        
        new = -1-port
        self.__active=list(self.__active)
        
        if state:    
            self.__active[new] = '1'
        if not state:
            self.__active[new] = '0'
        self.__active = ''.join(self.__active)
        self.dev.write_port(1,int(self.__active,2))
        self.__ports[port] = state
        self.debug_stream('changed port'+str(port)+' to '+str(state))
    
    @DebugIt()
    @command(dtype_in=DevVarLong64Array)    
    def gate_timer(self,inp):
        start = time.time()
        port,duration = inp
        self.change_port(port,True)
        time.sleep(duration)
        self.change_port(port,False)
        act_dur = time.time()-start
        self.debug_stream('Actual duration of gate: '+ str(act_dur))

    
	#work in progress...
    @DebugIt()
    @command(dtype_in=DevVarLong64Array)
    def pulsetrain(self,inp):
        hits = 0
        port, freq, duration = inp
        start = time.time()
        while time.time() <= start+duration:
            hits += 1
            self.change_port(port,True)
            time.sleep(1/(2*freq))
            self.change_port(port,False)
            time.sleep(1/(2*freq))
        end = time.time()
        self.debug_stream('Actual duration:'+str(end-start))
        self.debug_stream('Actual frequency: '+str(hits/(end-start)))
    
            
        
if __name__ == "__main__":
    NIUSB6501.run_server()
            
