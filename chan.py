from softioc import builder, softioc, alarm
import epics
#!file:///usr/local/epics/modules/pythonIoc/docs/html/softioc.html
#http://cars9.uchicago.edu/software/python/pyepics3/
#softioc.builder.aIn

class Channels: 
  def __init__(self, chanID,BoardID,relay):
    self.chanID = chanID
    self.BoardID = BoardID
    self.relay = relay
    #print "Hi, I am channel",self.chanID, "and board",self.BoardID	
    pvname = '{0:02d}:{1:02d}:'.format(self.BoardID, self.chanID)
    self.pv_vmon = builder.aIn(pvname+"vmon")
    self.pv_vmon.PREC = 2
    self.pv_current = builder.aIn(pvname+"current")
    self.pv_vset = builder.aOut(pvname+"vset",on_update=self.write_voltage)
    self.pv_vset.PREC = 2
    self.pv_vset.HOPR = 3000 
    self.pv_vset.LOPR = 0
    self.calc = builder.records.calc(pvname+'calc', CALC = 'ABS(A-B)')
    self.calc.INPA = self.pv_vset.name
    self.calc.INPB = self.pv_vmon.name
    self.pv_vmon.FLNK = builder.PP(self.calc)
    self.pv_vset.FLNK = builder.PP(self.calc)
    self.hihi = 30
    self.high = 25
    self.calc.HIHI = self.hihi
    self.calc.HIGH = self.high
    self.calc.HHSV = "MAJOR"
    self.calc.HSV = "MINOR"
    self.ramprate = builder.aOut(pvname+"ramprate",on_update=self.set_ramp, initial_value=100) 
    #print self.calc.name
    self.calc_high = epics.PV(self.calc.name+".HIGH")
    self.calc_hihi = epics.PV(self.calc.name+".HIHI")
		
  def write_voltage(self, val):
    command = "write ({0:d},{1:d}) {2:.1f}".format(self.BoardID, self.chanID, (-1)*val)
    self.relay.put_cmd(command)

  def reset_calc_limits(self):
    self.calc_high.put(self.high)
    self.calc_hihi.put(self.hihi)
    #softioc.dbpf(self.calc.name+".HIGH", str(self.high))
    #softioc.dbpf(self.calc.name+".HIHI", str(self.hihi))
    
  def set_invalid(self):
    self.pv_vmon.set_alarm(alarm.INVALID_ALARM,alarm.TIMEOUT_ALARM)
    self.pv_current.set_alarm(alarm.INVALID_ALARM,alarm.TIMEOUT_ALARM)

  def set_ramp(self, val):
    command = "set ramp ({0:d},{1:d}) {2:f}".format(self.BoardID, self.chanID, val)
    self.relay.put_cmd(command) 

  #def voltage_limits(self):
  #def current_limits(self):   





