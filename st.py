#!/usr/local/epics/modules/pythonIoc/pythonIoc

#set pythonIoc interpreter above

#import basic softioc framework
from softioc import softioc, builder

#import the the application
import myApp

#run the ioc
builder.LoadDatabase()
softioc.iocInit()

#start the application
myApp.do_startthread()

#start the ioc shell
softioc.interactive_ioc(globals())
