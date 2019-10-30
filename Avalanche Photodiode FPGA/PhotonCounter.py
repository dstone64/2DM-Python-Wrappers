import ctypes

class PhotonCounter:
    def __init__(self):
        self.hAPI = ctypes.CDLL("PhotonCounter.dll")
        self.connection = False

    def __del__(self):
        if self.connection:
            self.FPGA_disconnect()

    """
    Establishes the connection to the FPGA.
    @return: Returns True if the connection was successful or False otherwise
    """
    def FPGA_connect(self):
        if self.hAPI.FPGA_Connect() == 0:
            self.connection = True
            return True
        if (not self.connection) and (self.hAPI.FPGA_Load() == 0):
            if self.hAPI.FPGA_Connect() == 0:
                self.connection = True
                return True
        return False

    """
    Disconnects the FPGA.
    @return: Returns True if the disconnection was successful or False otherwise
    """
    def FPGA_disconnect(self):
        self.connection = False;
        dc = self.hAPI.FPGA_Disconnect()
        ul = self.hAPI.FPGA_Unload()
        return (dc == 0 and ul == 0)

    """
    Retrieves the accumulated counts from the FPGA.
    @return: Returns the number of counts or -1 if the called failed
    """
    def get_counts(self):
        return self.hAPI.FPGA_Counts()
