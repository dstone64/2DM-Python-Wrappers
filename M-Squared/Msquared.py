import socket
import re

class Msquared:
    BUFFER_SIZE = 1024

    def __init__(self):
        self.mrr = ''      # most recent response

    """
    Initializes the tcp socket.
    @param client_ip: client IP address (string)
    @param server_ip: server IP address (string)
    @param server_port: server port (string)
    @return: Returns True if the connection was successful or False otherwise
    """
    def init_tcp(self, client_ip, server_ip, server_port):
        self.client_ip = client_ip
        self.server_ip = server_ip
        self.server_port = int(server_port)

        self.msquared_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msquared_socket.connect((self.server_ip, self.server_port))
        INITMSG = b'{"message":{"transmission_id":[1],"op":"start_link","parameters":{"ip_address":"' + self.client_ip.encode() + b'"}}}'
        self.msquared_socket.send(INITMSG)
        self.mrr = self.msquared_socket.recv(Msquared.BUFFER_SIZE)
        return bool(re.match(r'^.*"status":"ok"}}}$', self.mrr.decode()))

    """
    Closes the tcp socket.
    """
    def end_tcp(self):
        self.msquared_socket.close()

    """
    Retrieves the wavelength reading and the tuning status.
    @return: Returns a tuple composed of wavelength (string) and the tuning status (string) or 'error'
    """
    def get_wavelength(self):
        MESSAGE = b'{"message":{"transmission_id":[1],"op":"poll_wave_m"}}'
        self.msquared_socket.send(MESSAGE)
        self.mrr = self.msquared_socket.recv(Msquared.BUFFER_SIZE)
        regexp = re.match(r'^\{"message":\{"transmission_id":\[1\],"op":"poll_wave_m_reply","parameters":\{"status":\[(\d)\],"current_wavelength":\[(\d+\.?\d*)\]', self.mrr.decode())
        return (regexp.group(2).encode('ascii'), regexp.group(1).encode('ascii')) if regexp else 'error'

    """
    Sets the target wavelength.
    @param wavelength: the desired wavelength (string)
    @return: Returns True if the target wavelength was successfully set or False otherwise
    """
    def set_wavelength(self, wavelength):
        MESSAGE = b'{"message":{"transmission_id":[2],"op":"set_wave_m","parameters":{"wavelength":[' + wavelength.encode() + b']}}}'
        self.msquared_socket.send(MESSAGE)
        self.mrr = self.msquared_socket.recv(Msquared.BUFFER_SIZE)
        regexp = re.match(r'^\{"message":\{"transmission_id":\[2\],"op":"set_wave_m_reply","parameters":\{"status":\[0\]', self.mrr.decode())
        return bool(regexp)

    """
    Locks the target wavelength (SolsTiS will monitor the wavelength and adjust accordingly).
    @return: Returns True if the command was successful or False otherwise
    """
    def lock_wavelength(self):
        MESSAGE = b'{"message":{"transmission_id":[3],"op":"lock_wave_m","parameters":{"operation":"on"}}}'
        self.msquared_socket.send(MESSAGE)
        self.mrr = self.msquared_socket.recv(Msquared.BUFFER_SIZE)
        regexp = re.match(r'^\{"message":\{"transmission_id":\[3\],"op":"lock_wave_m_reply","parameters":\{"status":\[0\]\}\}\}$', self.mrr.decode())
        return bool(regexp)

    """
    Unlocks the target wavelength (SolTiS will no longer tune the wavelength).
    @return: Returns the current wavelength (string) if successful or 'error' of not
    """
    def unlock_wavelength(self):
        MESSAGE = b'{"message":{"transmission_id":[4],"op":"stop_wave_m"}}'
        self.msquared_socket.send(MESSAGE)
        self.mrr = self.msquared_socket.recv(Msquared.BUFFER_SIZE)
        regexp = re.match(r'^\{"message":\{"transmission_id":\[4\],"op":"stop_wave_m_reply","parameters":\{"status":\[0\],"current_wavelength":\[(\d+\.?\d*)\]\}\}\}$', self.mrr.decode())
        return regexp.group(1).encode('ascii') if regexp else 'error'

    """
    Retrieves the wavelength lock status.
    @return: Returns the lock condition ('on', 'off', 'error')
    """
    def get_lock_status(self):
        MESSAGE = b'{"message":{"transmission_id":[5],"op":"poll_wave_m"}}'
        self.msquared_socket.send(MESSAGE)
        self.mrr = self.msquared_socket.recv(Msquared.BUFFER_SIZE)
        regexp = re.match(r'^\{"message":\{"transmission_id":\[5\],"op":"poll_wave_m_reply","parameters":\{.*"lock_status":\[(\d)\]', self.mrr.decode())
        if regexp:
            return 'on' if regexp.group(1).encode('ascii') == '1' else 'off'
        else:
            return 'error'

    """
    Sets the etalon lock.
    @param lock: desired lock status of the etalon lock (boolean)
    @return: Returns True if command is successful or False otherwise
    """
    def set_etalon_lock(self, lock):
        MESSAGE = b'{"message":{"transmission_id":[6],"op":"etalon_lock","parameters":{"operation":' + (b'"on"' if lock else b'"off"') + b'}}}'
        self.msquared_socket.send(MESSAGE)
        self.mrr = self.msquared_socket.recv(Msquared.BUFFER_SIZE)
        regexp = re.match(r'^\{"message":\{"transmission_id":\[6\],"op":"etalon_lock_reply","parameters":\{"status":\[0\]\}\}\}$', self.mrr.decode())
        return bool(regexp)

    """
    Retrieves the status of the etalon lock.
    @return: Returns the lock condition ('on', 'off', 'debug', 'search', 'low', or 'error')
    """
    def get_etalon_lock(self):
        MESSAGE = b'{"message":{"transmission_id":[7],"op":"etalon_lock_status"}}'
        self.msquared_socket.send(MESSAGE)
        self.mrr = self.msquared_socket.recv(Msquared.BUFFER_SIZE)
        regexp = re.match(r'^\{"message":\{"transmission_id":\[7\],"op":"etalon_lock_status_reply","parameters":\{"status":\[0\],"condition":"(.*)"\}\}\}$', self.mrr.decode())
        return regexp.group(1).encode('ascii') if regexp else 'error'

    """
    Returns the most recent response from the Msquared.
    @return: Most recent response (string)
    """
    def most_recent_response(self):
        return str(self.mrr)
