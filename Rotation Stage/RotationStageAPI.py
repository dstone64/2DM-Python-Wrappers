import ctypes
import os
import sys

rot_stage_serial = 55958760

if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))

class RotationStage:
    def __init__(self):
        self.lib_apt = ctypes.WinDLL('APT.dll')
        if self.lib_apt.APTInit() != 0:
            raise Exception("Error initiating APT")
        
        self.lib_apt.GetHWSerialNumEx.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.POINTER(ctypes.c_long)]
        self.lib_apt.GetHWSerialNumEx.restype = ctypes.c_long
        self.lib_apt.InitHWDevice.argtypes = [ctypes.c_long]
        self.lib_apt.InitHWDevice.restype = ctypes.c_long
        self.lib_apt.MOT_GetPosition.argtypes = [ctypes.c_long, ctypes.POINTER(ctypes.c_float)]
        self.lib_apt.MOT_GetPosition.restype = ctypes.c_long
        self.lib_apt.MOT_GetStatusBits.argtypes = [ctypes.c_long, ctypes.POINTER(ctypes.c_long)]
        self.lib_apt.MOT_GetStatusBits.restype = ctypes.c_long
        self.lib_apt.MOT_EnableHWChannel.argtypes = [ctypes.c_long]
        self.lib_apt.MOT_EnableHWChannel.restype = ctypes.c_long
        self.lib_apt.MOT_DisableHWChannel.argtypes = [ctypes.c_long]
        self.lib_apt.MOT_DisableHWChannel.restype = ctypes.c_long
        self.lib_apt.MOT_Identify.argtypes = [ctypes.c_long]
        self.lib_apt.MOT_Identify.restype = ctypes.c_long
        self.lib_apt.MOT_GetVelParams.argtypes = [ctypes.c_long, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        self.lib_apt.MOT_GetVelParams.restype = ctypes.c_long
        self.lib_apt.MOT_SetVelParams.argtypes = [ctypes.c_long, ctypes.c_float, ctypes.c_float, ctypes.c_float]
        self.lib_apt.MOT_GetVelParamLimits.argtypes = [ctypes.c_long, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        self.lib_apt.MOT_GetVelParamLimits.restype = ctypes.c_long
        self.lib_apt.MOT_GetHomeParams.argtypes = [ctypes.c_long, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        self.lib_apt.MOT_GetHomeParams.restype = ctypes.c_long
        self.lib_apt.MOT_SetHomeParams.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_float, ctypes.c_float]
        self.lib_apt.MOT_SetHomeParams.restype = ctypes.c_long
        self.lib_apt.MOT_GetMotorParams.argtypes = [ctypes.c_long, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]
        self.lib_apt.MOT_GetMotorParams.restype = ctypes.c_long
        self.lib_apt.MOT_SetMotorParams.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.c_long]
        self.lib_apt.MOT_SetMotorParams.restype = ctypes.c_long
        self.lib_apt.MOT_GetStageAxisInfo.argtypes = [ctypes.c_long, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_float)]
        self.lib_apt.MOT_GetStageAxisInfo.restype = ctypes.c_long
        self.lib_apt.MOT_SetStageAxisInfo.argtypes = [ctypes.c_long, ctypes.c_float, ctypes.c_float, ctypes.c_long, ctypes.c_float]
        self.lib_apt.MOT_SetStageAxisInfo.restype = ctypes.c_long
        self.lib_apt.MOT_MoveAbsoluteEx.argtypes = [ctypes.c_long, ctypes.c_float, ctypes.c_bool]
        self.lib_apt.MOT_MoveAbsoluteEx.restype = ctypes.c_long
        self.lib_apt.MOT_MoveRelativeEx.argtypes = [ctypes.c_long, ctypes.c_float, ctypes.c_bool]
        self.lib_apt.MOT_MoveRelativeEx.restype = ctypes.c_long
        self.lib_apt.MOT_MoveHome.argtypes = [ctypes.c_long, ctypes.c_bool]
        self.lib_apt.MOT_MoveHome.restype = ctypes.c_long
        self.lib_apt.MOT_MoveVelocity.argtypes = [ctypes.c_long, ctypes.c_long]
        self.lib_apt.MOT_MoveVelocity.restype = ctypes.c_long

        if self.lib_apt.InitHWDevice(rot_stage_serial) != 0:
            raise Exception("Error initiating device")
        
        if not self.setVelocityParams(0, 10, 10):
            raise Exception("Error initiating device parameters")

    def __del__(self):
        self.lib_apt.APTCleanUp()

    def getStatus(self, mask):
        status_bits = ctypes.c_long()
        self.lib_apt.MOT_GetStatusBits(rot_stage_serial, ctypes.byref(status_bits))
        return bool(status_bits.value & mask)
        
    @property
    def isMoving(self):
        mask = 0x00000010 | 0x00000020 | 0x00000040 | 0x00000080 | 0x00000200
        return self.getStatus(mask)
    
    @property
    def isHomingComplete(self):
        mask = 0x00000400
        return self.getStatus(mask)
    
    @property
    def isTracking(self):
        mask = 0x00001000
        return self.getStatus(mask)
    
    @property
    def isSettled(self):
        mask = 0x00002000
        return self.getStatus(mask)
    
    @property
    def atCurrentLimit(self):
        mask = 0x01000000
        return self.getStatus(mask)
    
    @property
    def motionError(self):
        mask = 0x00004000
        return self.getStatus(mask)
    
    @property
    def isEnabled(self):
        mask = 0x80000000
        return self.getStatus(mask)
    
    @property
    def position(self):
        pos = ctypes.c_float()
        if self.lib_apt.MOT_GetPosition(rot_stage_serial, ctypes.byref(pos)) != 0:
            return False
        return pos.value
    
    def setEnable(self, enable):
        if enable:
            return self.lib_apt.MOT_EnableHWChannel(rot_stage_serial) == 0
        else:
            return self.lib_apt.MOT_DisableHWChannel(rot_stage_serial) == 0
    
    def identify(self):
        return self.lib_apt.MOT_Identify(rot_stage_serial) == 0
    
    def getVelocityParams(self):
        min_vel = ctypes.c_float()
        accl = ctypes.c_float()
        max_vel = ctypes.c_float()
        if self.lib_apt.MOT_GetVelParams(rot_stage_serial, ctypes.byref(min_vel), ctypes.byref(accl), ctypes.byref(max_vel)) != 0:
            return False
        return (min_vel.value, accl.value, max_val.value)
    
    def getVelocityLimits(self):
        max_accl = ctypes.c_float()
        max_vel = ctypes.c_float()
        if self.lib_apt.MOT_GetVelParamLimits(rot_stage_serial, ctypes.byref(max_accl), ctypes.byref(max_vel)) != 0:
            return False
        return (max_accl.value, max_vel.value)

    """
    Sets velocity parameters. According to the Thorlabs documentation
    minimum velocity is always 0 and hence is ignored.
    ----------
    min_vel : float
        minimum velocity
    accn : float
        acceleration
    max_vel : float
        maximum velocity
    """
    def setVelocityParams(self, min_vel, accl, max_vel):
        return self.lib_apt.MOT_SetVelParams(rot_stage_serial, min_vel, accl, max_vel) == 0
    
    def getHomeParams(self):
        direction = ctypes.c_long()
        lim_switch = ctypes.c_long()
        velocity = ctypes.c_float()
        zero_offset = ctypes.c_float()
        if self.lib_apt.MOT_GetHomeParams(rot_stage_serial, ctypes.byref(direction), ctypes.byref(lim_switch), ctypes.byref(velocity), ctypes.byref(zero_offset)) != 0:
            return False
        return (direction.value, lim_switch.value, velocity.value, zero_offset.value)

    """
    Sets parameters used when homing.
    ----------
    direction : int
        home in forward or reverse direction:
        - HOME_FWD = 1 : Home in the forward direction.
        - HOME_REV = 2 : Home in the reverse direction.
    lim_switch : int
        forward limit switch or reverse limit switch:
        - HOMELIMSW_FWD = 4 : Use forward limit switch for home datum.
        - HOMELIMSW_REV = 1 : Use reverse limit switch for home datum.
    velocity : float
        velocity of the motor
    zero_offset : float
        zero offset
    """
    def setHomeParams(self, direction, lim_switch, vel, zero_offset):
        return self.lib_apt.MOT_SetHomeParams(rot_stage_serial, direction, lim_switch, velocity, zero_offset) == 0
    
    def getMotorParams(self):
        steps_per_rev = ctypes.c_long()
        gear_box_ratio = ctypes.c_long()
        if self.lib_apt.MOT_GetMotorParams(rot_stage_serial, ctypes.byref(steps_per_rev), ctypes.byref(gear_box_ratio)) != 0:
            return False
        return (steps_per_rev.value, gear_box_ratio.value)
    
    def setMotorParams(self, steps_per_rev, gear_ratio):
        return self.lib_apt.MOT_SetMotorParams(rot_stage_serial, steps_per_rev, gear_box_ratio) == 0

    """
    Returns axis information of stage.

    Returns
    -------
    out : tuple
        (minimum position, maximum position, stage units, pitch)
        - STAGE_UNITS_MM = 1 : Stage units in mm
        - STAGE_UNITS_DEG = 2 : Stage units in degrees
    """
    def getStageInfo(self):
        min_pos = ctypes.c_float()
        max_pos = ctypes.c_float()
        units = ctypes.c_long()
        pitch = ctypes.c_float()
        if self.lib_apt.MOT_GetStageAxisInfo(rot_stage_serial, ctypes.byref(min_pos), ctypes.byref(max_pos), ctypes.byref(units), ctypes.byref(pitch)) != 0:
            return False
        return (min_pos.value, max_pos.value, units.value, pitch.value)
    
    def setStageInfo(self, min_pos, max_pos, pitch):
        return self.lib_apt.MOT_SetStageAxisInfo(rot_stage_serial, min_pos, max_pos, 2, pitch) == 0
    
    def moveTo(self, value, blocking = False):
        return self.lib_apt.MOT_MoveAbsoluteEx(rot_stage_serial, value, blocking) == 0
    
    def moveBy(self, value, blocking = False):
        return self.lib_apt.MOT_MoveRelativeEx(rot_stage_serial, value, blocking) == 0
    
    def moveHome(self):
        moveTo(0, True)
        moveTo(90, True)
        moveTo(180, True)
        moveTo(270, True)
        moveTo(45, True)
        return self.lib_apt.MOT_MoveHome(rot_stage_serial, True) == 0

    """
    Parameters
    ----------
    direction : int
        MOVE_FWD = 1 : Move forward
        MOVE_REV = 2 : Move reverse
    """
    def moveDirection(self, direction):
        return self.lib_apt.MOT_MoveVelocity(rot_stage_serial, direction) == 0
