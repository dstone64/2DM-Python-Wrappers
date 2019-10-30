"""
REQUIRES:
AttocubeAPI.dll
anc350v4.dll
"""

from ctypes import *
import time

class Attocube:
    X_AXIS = 0
    Y_AXIS = 1
    Z_AXIS = 2
    
    def __init__(self):
        self.api = CDLL("AttocubeAPI.dll")
        self.api.Attocube_connect.argtypes = []
        self.api.Attocube_connect.restype = c_int
        self.api.Attocube_disconnect.argtypes = []
        self.api.Attocube_disconnect.restype = c_int
        self.api.Attocube_getAxisStatus.argtypes = [POINTER(c_int), POINTER(c_bool), POINTER(c_bool), POINTER(c_bool), POINTER(c_bool), POINTER(c_bool), POINTER(c_bool), POINTER(c_bool)]
        self.api.Attocube_getAxisStatus.restype = c_int
        self.api.Attocube_setAxisOutput.argtypes = [POINTER(c_int), POINTER(c_bool), POINTER(c_bool)]
        self.api.Attocube_setAxisOutput.restype = c_int
        self.api.Attocube_setAmplitude.argtypes = [POINTER(c_int), POINTER(c_double)]
        self.api.Attocube_setAmplitude.restype = c_int
        self.api.Attocube_setFrequency.argtypes = [POINTER(c_int), POINTER(c_double)]
        self.api.Attocube_setFrequency.restype = c_int
        self.api.Attocube_setDcVoltage.argtypes = [POINTER(c_int), POINTER(c_double)]
        self.api.Attocube_setDcVoltage.restype = c_int
        self.api.Attocube_getAmplitude.argtypes = [POINTER(c_int), POINTER(c_double)]
        self.api.Attocube_getAmplitude.restype = c_int
        self.api.Attocube_getFrequency.argtypes = [POINTER(c_int), POINTER(c_double)]
        self.api.Attocube_getFrequency.restype = c_int
        self.api.Attocube_startSingleStep.argtypes = [POINTER(c_int), POINTER(c_bool)]
        self.api.Attocube_startSingleStep.restype = c_int
        self.api.Attocube_startContinuousMove.argtypes = [POINTER(c_int), POINTER(c_bool), POINTER(c_bool)]
        self.api.Attocube_startContinuousMove.restype = c_int
        self.api.Attocube_startAutoMove.argtypes = [POINTER(c_int), POINTER(c_bool), POINTER(c_bool)]
        self.api.Attocube_startAutoMove.restype = c_int
        self.api.Attocube_setTargetPosition.argtypes = [POINTER(c_int), POINTER(c_double)]
        self.api.Attocube_setTargetPosition.restype = c_int
        self.api.Attocube_setTargetRange.argtypes = [POINTER(c_int), POINTER(c_double)]
        self.api.Attocube_setTargetRange.restype = c_int
        self.api.Attocube_setTargetGround.argtypes = [POINTER(c_int), POINTER(c_bool)]
        self.api.Attocube_setTargetGround.restype = c_int
        self.api.Attocube_getPosition.argtypes = [POINTER(c_int), POINTER(c_double)]
        self.api.Attocube_getPosition.restype = c_int

        r = int(0)
        r = self.api.Attocube_connect()
        if r != 0:
            raise Exception("ERROR: Could not connect to attocube")
    
    def __del__(self):
        self.api.Attocube_disconnect()

    """
    conn: If the axis is connected to a sensor
    enab: If the axis voltage output is enabled
    move: If the axis is moving
    targ: If the target is reached in automatic positioning
    eotF: If end of travel detected in forward direction
    eotB: If end of travel detected in backward direction
    err:  If the axis' sensor is in error state
    """
    def getAxisStatus(self, axis):
        t_ax = (c_int)(axis)
        conn = (c_bool)(False)
        enab = (c_bool)(False)
        move = (c_bool)(False)
        targ = (c_bool)(False)
        eotF = (c_bool)(False)
        eotB = (c_bool)(False)
        err  = (c_bool)(False)
        r = int(0)
        r = self.api.Attocube_getAxisStatus(byref(t_ax), byref(conn), byref(enab), byref(move), byref(targ), byref(eotF), byref(eotB), byref(err))
        return (r, conn.value, enab.value, move.value, targ.value, eotF.value, eotB.value, err.value)

    def isConnected(self, axis):
        _, conn, _, _, _, _, _, _ = self.getAxisStatus(axis)
        return conn

    def isEnabled(self, axis):
        _, _, enab, _, _, _, _, _ = self.getAxisStatus(axis)
        return enab

    def isMoving(self, axis):
        _, _, _, move, _, _, _, _ = self.getAxisStatus(axis)
        return move

    def targetReached(self, axis):
        _, _, _, _, targ, _, _, _ = self.getAxisStatus(axis)
        return targ

    """
    enable: True to enable or False to disable axis output
    autoDisable: The voltage output is to be deactivated automatically when end of travel is detected
    """
    def setAxisOutput(self, axis, enable, autoDisable):
        t_ax = (c_int)(axis)
        enab = (c_bool)(enable)
        aDis = (c_bool)(autoDisable)
        r = int(0)
        r = self.api.Attocube_setAxisOutput(byref(t_ax), byref(enab), byref(aDis))
        return r

    def setAmplitude(self, axis, amplitude):
        t_ax = (c_int)(axis)
        ampl = (c_double)(amplitude)
        r = int(0)
        r = self.api.Attocube_setAmplitude(byref(t_ax), byref(ampl))
        return r

    def setFrequency(self, axis, frequency):
        t_ax = (c_int)(axis)
        freq = (c_double)(frequency)
        r = int(0)
        r = self.api.Attocube_setFrequency(byref(t_ax), byref(freq))
        return r

    def setDcVoltage(self, axis, voltage):
        t_ax = (c_int)(axis)
        volt = (c_double)(voltage)
        r = int(0)
        r = self.api.Attocube_setDcVoltage(byref(t_ax), byref(volt))
        return r

    def getAmplitude(self, axis):
        t_ax = (c_int)(axis)
        ampl = (c_double)(0)
        r = int(0)
        r = self.api.Attocube_getAmplitude(byref(t_ax), byref(ampl))
        return (r, ampl.value)

    def getFrequency(self, axis):
        t_ax = (c_int)(axis)
        freq = (c_double)(0)
        r = int(0)
        r = self.api.Attocube_getFrequency(byref(t_ax), byref(freq))
        return (r, freq.value)

    def startSingleStep(self, axis, backward):
        t_ax = (c_int)(axis)
        back = (c_bool)(backward)
        r = int(0)
        r = self.api.Attocube_startSingleStep(byref(t_ax), byref(back))
        return r

    def startContinuousMove(self, axis, start, backward):
        t_ax = (c_int)(axis)
        strt = (c_bool)(start)
        back = (c_bool)(backward)
        r = int(0)
        r = self.api.Attocube_startContinuousMove(byref(t_ax), byref(strt), byref(back))
        return r

    def startAutoMove(self, axis, enable, relative):
        t_ax = (c_int)(axis)
        enab = (c_bool)(enable)
        rela = (c_bool)(relative)
        r = int(0)
        r = self.api.Attocube_startAutoMove(byref(t_ax), byref(enab), byref(rela))
        return r

    def setTargetPosition(self, axis, target):
        t_ax = (c_int)(axis)
        targ = (c_double)(target)
        r = int(0)
        r = self.api.Attocube_setTargetPosition(byref(t_ax), byref(targ))
        return r

    """
    Defines the range around the target position where the target is considered to be reached.
    targetRange: Target range
    """
    def setTargetRange(self, axis, targetRange):
        t_ax = (c_int)(axis)
        tRng = (c_double)(targetRange)
        r = int(0)
        r = self.api.Attocube_setTargetRange(byref(t_ax), byref(tRng))
        return r

    def setTargetGround(self, axis, targetGround):
        t_ax = (c_int)(axis)
        tGnd = (c_bool)(targetGround)
        r = int(0)
        r = self.api.Attocube_setTargetGround(byref(t_ax), byref(tGnd))
        return r

    def getPosition(self, axis):
        t_ax = (c_int)(axis)
        posn = (c_double)(0)
        r = int(0)
        r = self.api.Attocube_getPosition(byref(t_ax), byref(posn))
        return posn.value

    """
    HIGH LEVEL API COMMMANDS
    """
    def bStep(self, axis, numSteps, backward):
        for i in range(abs(numSteps)):
            self.startSingleStep(axis, backward)
            time.sleep(1)
