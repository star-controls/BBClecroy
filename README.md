# BBClecroy
List of all python files:
BBCdemandClass.py
boardClass.py
chan.py
leCroy_com.py
myApp.py
PPHVdemandclass.py
st.py
VPDdemandclass.py
ZDCdemandclass.py

What each python file does:
  myApp.py
    Top level, where all other python files are used.  This makes the classes 
    BBC, PPHV, VPD, and ZDC able to place values.  This also turns the lecroy on
    and off.
  chan.py
    This is where the channels are created, which is then imported into 
    boardClass.py
  boardClass.py
    The board class creates the boards while incoprorating the channels that
    were created in chan.py. setToZero and reset_calc_limits functions are 
    defined here.
  st.py
    Executable file that runs the ioc and the application (myApp.py). The ioc 
    shell is also started.  This file needs to be running in order for GUIs to 
    function. The shell will also let the user know when the lecroy is turned on
    and off.
  BBCdemandClass.py
    Class to set demand voltages for BBC
  PPHVdemandclass.py
    Class to set demand votlages for PP2PP
  VPDdemandclass.py
    Class to set demand voltages for VPD. Also includes functions for VPDSMD
  ZDCdemandclass.py
    Class to set demand voltages for ZDC
  leCroy_com.py
    Creates a serial connection to lecroy power supply
