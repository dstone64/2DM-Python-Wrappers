"""
Requires:
Newport.CONEXCC.CommandInterface.dll
Diagnostics.Logging.Applet.dll
FTD2XX_NET.dll
FTDIWrap.dll
VCPWrap.dll
"""

import sys
import os
import clr

if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))
clr.AddReference("Newport.CONEXCC.CommandInterface")

from CommandInterfaceConexCC import *

class Servo:
    def __init__(self, com_port):
        self.CC = ConexCC()
        if self.CC.OpenInstrument(com_port) != 0:
            raise Exception('ERROR(Servo): Could not connect to ConexCC')
        self.home()

    def __del__(self):
        self.CC.CloseInstrument()

    def home(self):
        errCode, errStr = self.CC.OR(1, '')
        if errCode != 0:
            raise Exception('ERROR(Servo.home): ' + errStr)

    def setAbsolutePos(self, pos):
        if pos < 0:
            pos = 0
        elif pos > 12:
            pos = 12
        errCode, errStr = self.CC.PA_Set(1, float(pos), '')
        if errCode != 0:
            raise Exception('ERROR(Servo.setAbsolutePos): ' + errStr)

    def getCurrentPos(self):
        errCode, pos, errStr = self.CC.TP(1, 0, '')
        if errCode != 0:
            raise Exception('ERROR(Servo.getCurrentPos): ' + errStr)
        return pos

    @property
    def isMoving(self):
        errCode, _, controlState, errStr = self.CC.TS(1, '', '', '')
        if errCode != 0:
            raise Exception('ERROR(Servo.isMoving): ' + errStr)
        if controlState == '28':
            return True
        else:
            return False
