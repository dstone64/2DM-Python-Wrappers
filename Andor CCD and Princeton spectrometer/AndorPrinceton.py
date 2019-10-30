import serial
import time
import os
import pickle
import numpy as np
import scipy.signal as pysignal
import atmcd

def filterSpikes(data, threshold=500, max_spike_width=10, window_length=51, polyorder1=3, polyorder2=1):
    smooth_data = pysignal.savgol_filter(data, window_length, polyorder1)
    smoother_data = pysignal.savgol_filter(smooth_data, window_length, polyorder2)
    i = 0
    new_data = np.array(data)
    data_len = len(data)
    while i < data_len:
        # Find spike
        if (data[i] - smoother_data[i]) > threshold:
            # Find start point
            start = i-1
            while data[start] > smoother_data[start]:
                start -= 1

            # Find end point
            end = (i + max_spike_width) if (i + max_spike_width) < data_len else (data_len - 1)
            j = 1
            while j < max_spike_width and (i + j) < data_len:
                if data[i + j] < smoother_data[i + j]:
                    end = i + j
                    break
                j += 1

            # Interpolate
            m = (data[end] - data[start]) / (end - start)
            b = data[start] - m*start
            j = start + 1
            while j < end:
                new_data[j] = m*j + b
                j += 1
            i = end
        i += 1
    return new_data

class AndorPrinceton():
    FRAMES = [
        500.000,
        526.977,
        553.640,
        579.991,
        606.036,
        631.776,
        657.216,
        682.360,
        707.210,
        731.770,
        756.044,
        780.035,
        803.746,
        827.180,
        850.341,
        873.232,
        895.856,
        918.216,
        940.315,
        962.156,
        983.743,
        1005.078,
        1026.164,
        1047.004,
        1067.601,
        1087.958,
        1108.077,
        1127.962,
        1147.614,
        1167.038,
        1186.235,
        1205.208,
        1223.959,
        1242.492,
        1260.809,
        1278.912,
        1296.804,
        1314.488,
        1331.965,
        1349.238,
        1366.310,
        1383.182,
        1399.858,
        1416.339,
        1432.628,
        1448.727,
        1464.639,
        1480.364,
        1495.907,
        1511.268
    ]

    MIDPOINTS = np.poly1d(np.array([-2.27116816e-02,  5.42828888e+02]))
    
    def __init__(self, com_port):
        self.frame_idx = 0
        self.frame_targets = []

        # Retrieve wavelength arrays for each frame
        script_dir = os.path.dirname(__file__)
        rel_path = "AndorPrinceton_wavelengths.bin"
        wl_arr_file_path = os.path.join(script_dir, rel_path)
        wl_file = open(wl_arr_file_path, "rb")
        self.WAVELENGTH_ARRAYS = pickle.load(wl_file)
        wl_file.close()

        # Andor initialization
        print("Intializing camera...")
        self.sdkObject = atmcd.atmcd() #load the atmcd library
        (ret) = self.sdkObject.Initialize("/usr/local/etc/andor") #initialise camera
        print("Initialize camera returned:",ret)
        if atmcd.atmcd.DRV_SUCCESS == ret:
            (ret, iSerialNumber) = self.sdkObject.GetCameraSerialNumber()
            print("GetCameraSerialNumber returned:",ret,"Serial No:",iSerialNumber)

            #configure the acquisition
            (ret) = self.sdkObject.CoolerON()
            print("Function CoolerON returned:",ret)

        # Princeton initialization
        self.spec=serial.Serial(port=com_port,baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
        self.spec.write(b'1 TURRET\r')
        self.spec.readline().decode()

    """
    Initializes the spectrometer sweep array
    """
    def initSweep(self, wavelength_start, wavelength_end):
        frame_start = 0
        while frame_start + 1 < len(self.FRAMES):
            if self.FRAMES[frame_start + 1] > wavelength_start:
                break
            frame_start += 1
        frame_end = len(self.FRAMES) - 1
        while frame_end > frame_start:
            if self.FRAMES[frame_end - 1] < wavelength_end:
                break
            frame_end -= 1
        self.frame_targets = self.FRAMES[frame_start:frame_end+1]
        self.frame_idx = 0
        return self.frame_targets

    """
    Returns a 5-tuple consisting of...
    bool  -> True if data collection occurred, False otherwise (indicates end of spectrometer sweep - all other values will return None)
    float -> Spectrometer center wavelength (i.e. the frame wavelength)
    int   -> Spectrometer center pixel
    array -> Camera counts array
    array -> Wavelength array
    """
    def collect(self):
        if self.frame_idx < len(self.frame_targets):
            self.setWavelength(self.frame_targets[self.frame_idx])
            spec_wl = float(self.getWavelength())
            mp = int(round(self.MIDPOINTS(spec_wl)))
            self.startAcq()
            self.waitAcq()
            data = self.collectData()
            wl_arr = self.WAVELENGTH_ARRAYS[self.frame_targets[self.frame_idx]]
            self.frame_idx += 1
            return (True, spec_wl, mp, data, wl_arr)
        else:
            return (False,None,None,None,None)

    def getWavelengthArrays(self):
        return self.WAVELENGTH_ARRAYS

    def setTemp(self, temp):
        (ret) = self.sdkObject.SetTemperature(temp)
        return ret

    def readTemp(self):
        (ret, temp) = self.sdkObject.GetTemperature()
        return float(temp)

    def setExposure(self, exposure):
        (ret) = self.sdkObject.SetExposureTime(exposure)
        return ret

    def prepFCBAcq(self):
        ret_str = ""
        
        (ret) = self.sdkObject.SetAcquisitionMode(1)
        ret_str += "Function SetAcquisitionMode returned" + str(ret) + "mode = Single Scan\n"

        (ret) = self.sdkObject.SetReadMode(0)
        ret_str += "Function SetReadMode returned" + str(ret) + "mode = FVB\n"

        (ret) = self.sdkObject.SetTriggerMode(0)
        ret_str += "Function SetTriggerMode returned" + str(ret) + "mode = Internal\n"

        (ret, self.xpixels, self.ypixels) = self.sdkObject.GetDetector()
        ret_str += "Function GetDetector returned" + str(ret) + "xpixels =" + str(self.xpixels) + "ypixels =" + str(self.ypixels) + "\n"

        (ret) = self.sdkObject.SetImage(1, 1, 1, self.xpixels, 1, self.ypixels)
        ret_str += "Function SetImage returned" + str(ret) + "hbin = 1 vbin = 1 hstart = 1 hend =" + str(self.xpixels) + "vstart = 1 vend =" + str(self.ypixels) + "\n"

        (ret, fminExposure, fAccumulate, fKinetic) = self.sdkObject.GetAcquisitionTimings()
        ret_str += "Function GetAcquisitionTimings returned" + str(ret) + "exposure =" + str(fminExposure) + "accumulate =" + str(fAccumulate) + "kinetic =" + str(fKinetic) + "\n"

        (ret) = self.sdkObject.PrepareAcquisition()
        ret_str += "Function PrepareAcquisition returned" + str(ret)

        return ret_str

    def startAcq(self):
        (ret) = self.sdkObject.StartAcquisition()
        return ret

    def waitAcq(self):
        (ret) = self.sdkObject.WaitForAcquisition()
        return ret

    def collectData(self):
        imageSize = self.xpixels
        (ret, fullFrameBuffer) = self.sdkObject.GetMostRecentImage(imageSize)
        data = np.array(fullFrameBuffer)
        return data[12:-12]

    """
    def shutdownCamera(self):
        (ret) = self.sdkObject.ShutDown()
        return ret
    """

    def getGratings(self):
        self.spec.write(b"?GRATINGS\r")
        gratings = []
        self.spec.readline().decode()
        for i in range(0, 10):
            gratings.append(self.spec.readline().decode().replace("\n", "").replace("ok", "").replace("nm", "").replace("\r", ""))
        return gratings

    def setGrating(self, num):
        self.spec.write(str(num).encode('utf-8') + b" GRATING\r")
        return self.spec.readline().decode()

    def getWavelength(self):
        self.spec.write(b"?NM\r")
        wl = self.spec.readline().decode().replace(" ", "").replace("\n", "").replace("ok", "").replace("nm", "")
        while len(wl) < 7:
            wl = self.spec.readline().decode().replace(" ", "").replace("\n", "").replace("ok", "").replace("nm", "")
        return wl

    def setWavelength(self, wavelength):
        self.spec.write(str(wavelength).encode('utf-8') + b" GOTO\r")
        self.spec.readline().decode()
        self.spec.readline().decode()
        
        self.spec.write(b"MONO-?DONE\r")
        done = self.spec.readline().decode().replace(" ", "").replace("\n", "").replace("ok", "")
        
        while done == "":
            self.spec.write(b"MONO-?DONE\r")
            done = self.spec.readline().decode().replace(" ", "").replace("\n", "").replace("ok", "")
        return done

    """
    def close(self):
        self.spec.close()
    """
