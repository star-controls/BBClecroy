from threading import Timer

class watchdog():
  #_____________________________________________________________________________
  def __init__(self, timeout, bdlist):
    self.timeout = timeout
    self.bdlist = bdlist
    self.timer = Timer(self.timeout, self.handler)
  #_____________________________________________________________________________
  def start(self):
    self.timer.start()
  #_____________________________________________________________________________
  def reset(self):
    self.timer.cancel()
    self.timer = Timer(self.timeout, self.handler)
    self.timer.start()
  #_____________________________________________________________________________
  def handler(self):
    print "Timeout in watchdog"
    #set all channels as invalid
    for ibd in range(len(self.bdlist)):
      for ich in range(len(self.bdlist[ibd].channels)):
        self.bdlist[ibd].channels[ich].set_invalid()
