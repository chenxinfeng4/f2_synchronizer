import win32gui
import win32api
import win32con
import obsws_python as  obs
from abc import ABC, abstractmethod
import socket
import pythoncom
import win32com
import win32com.client

pythoncom.CoInitialize()
def log_slave(*args, **kargs):
    print("[Slave]", *args, **kargs)


class Slave(ABC):
    def __init__(self):
        self.ready = False

    @abstractmethod    
    def check_ready(self)->bool:
        return True
    
    @abstractmethod
    def start(self)->None:
        pass

    @abstractmethod
    def stop(self)->None:
        pass

    def switch(self, switch:bool):
        mode = (self.check_ready(), switch)
        log_slave('USV mode', self.__class__, mode)
        if mode == (True, True):
            self.start()
            self.release()
        elif mode == (True, False):
            self.stop()
            self.release()
        elif mode == (False, True):
            log_slave("Slave not openned")
        elif mode == (False, False):
            self.release()
        else:
            print('mode', mode)
            raise OSError("Unknown mode")

    def release(self):
        pass


class Slave_OBS(Slave):
    def __init__(self, ip='localhost', port=4455):
        super().__init__()
        self.ip = ip
        self.port = port
        self.cl = None

    def check_ready(self) -> bool:
        try:
            self.release()
            cl = obs.ReqClient(host=self.ip, port=self.port)
            log_slave('Found OBS studio.')
        except Exception:
            cl = None
        self.cl = cl
        self.ready = cl is not None
        return self.ready
    
    def start(self):
        if self.cl:
            try:
                self.cl.start_record()
            except:
                pass

    def stop(self):
        if self.cl:
            try:
                self.cl.stop_record()
            except:
                pass

    def release(self):
        if self.cl:
            self.cl.base_client.ws.close()
            self.cl=None


class Slave_Miniscope(Slave):
    def __init__(self, ip='localhost', port=20172):
        super().__init__()
        self.cl = None
        self.ip = ip
        self.port = port

    def check_ready(self) -> bool:
        try:
            self.release()
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((self.ip, self.port))
            log_slave('Found Slave_Miniscope.')
        except Exception:
            tcp_socket = None
        self.cl = tcp_socket
        self.ready = tcp_socket is None
        return self.ready

    def start(self):
        send_data_byte = "start_record".encode("utf-8")
        if self.cl:
            self.cl.send(send_data_byte)

    def stop(self):
        send_data_byte = "stop_record".encode("utf-8")
        if self.cl:
            self.cl.send(send_data_byte)

    def __read_response(self):
        from_server_msg = self.cl.recv(1024)
        print(from_server_msg.decode("utf-8"))
    
    def release(self):
        if self.cl:
            self.cl.close()
            del self.cl
            self.cl = None


class Slave_USV(Slave):
    def __init__(self):
        super().__init__()
        self.titlename = "Avisoft-RECORDER USGH  (RECORDER.INI)"
        self.cl = None
        self.shell = win32com.client.Dispatch("WScript.Shell")
    
    def check_ready(self) -> bool:
        hwnd = win32gui.FindWindow(None, self.titlename)
        if hwnd==0:
            self.cl = None
        else:
            self.cl = hwnd
            log_slave('Found USV.')
        self.ready = self.cl is not None
        return self.ready

    def start(self):
        self.shell.SendKeys('%')
        log_slave('USV_Start', self.cl)
        win32gui.ShowWindow(self.cl, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.cl)

        win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
        win32api.keybd_event(win32con.VK_F3,0,0,0)     # F3
        win32api.keybd_event(win32con.VK_F3,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0) 

        self.shell.SendKeys('%')
        win32gui.ShowWindow(self.cl, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.cl)

        win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
        win32api.keybd_event(win32con.VK_F3,0,0,0)     # F3
        win32api.keybd_event(win32con.VK_F3,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0) 
        
    def stop(self):
        self.shell.SendKeys('%')
        win32gui.ShowWindow(self.cl, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.cl)

        win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
        win32api.keybd_event(win32con.VK_F5,0,0,0)     # F5
        win32api.keybd_event(win32con.VK_F5,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0) 

        self.shell.SendKeys('%')
        win32gui.ShowWindow(self.cl, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.cl)

        win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
        win32api.keybd_event(win32con.VK_F5,0,0,0)     # F5
        win32api.keybd_event(win32con.VK_F5,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0) 
        log_slave('USV Stopped', self.cl)
