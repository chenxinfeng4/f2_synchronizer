import win32gui
import win32api
import win32con
import obsws_python as  obs
from abc import ABC, abstractmethod
import socket
import pythoncom
import win32com
import win32com.client
from f2_logging import logprint
import os
from datetime import datetime
import subprocess
import time


pythoncom.CoInitialize()
def log_slave(*args, **kargs):
    logprint("[Slave] " + ' '.join(str(a) for a in args))


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
        if mode == (True, True):
            log_slave(self.__class__, "found and start")
            self.start()
            self.release()
        elif mode == (True, False):
            log_slave(self.__class__, "found and stop")
            self.stop()
            self.release()
        elif mode == (False, True):
            log_slave(self.__class__, "not openned")
        elif mode == (False, False):
            self.release()
        else:
            print('mode', mode)
            raise OSError("Unknown mode")

    def release(self):
        pass


class Slave_OBS_tagger(Slave):
    def __init__(self, ip='localhost', port=4455):
        super().__init__()
        self.ip = ip
        self.port = port
        self.hwnd = None
    
    def check_ready(self) -> bool:
        self.tbg = time.time()
        if self.hwnd is None or not self.hwnd.base_client.ws.connected:
            try:
                cl = obs.ReqClient(host=self.ip, port=self.port)
                resp = cl.send("GetInputList", {"inputKind": "text_gdiplus_v2"})
                inputName_l = [d['inputName'] for d in resp.inputs]
                if 'TextFrame' not in inputName_l:
                    sceneName = cl.get_current_program_scene().current_program_scene_name
                    cl.send("CreateInput", {"sceneName":sceneName, 
                                            "inputName": "TextFrame",
                                            "inputKind": "text_gdiplus_v2"})
                self.hwnd = cl
            except Exception:
                self.hwnd = None
            self.ready = self.hwnd is not None
        return self.ready

    def start(self):
        if self.hwnd:
            try:
                self.hwnd.send("SetInputSettings", {"inputName": "TextFrame", "inputSettings": {
                    'align': 'right', 'bk_opacity': 100,'color': '#FF0000', 
                    'text': '000', 'bk_color': 4278190335, 
                    'font': {'face': 'Courier New', 'flags': 0, 'size': 60, 'style': 'Regular'}}})
                while True:
                    tpass = int((time.time() - self.tbg) * 1000)
                    if tpass > 999: break
                    text = f'{tpass:03d}'
                    self.hwnd.send("SetInputSettings", {"inputName": "TextFrame", "inputSettings": {
                        'text': text}})
                    time.sleep(0.01)
                self.hwnd.send("SetInputSettings", {"inputName": "TextFrame", "inputSettings": {
                        'bk_color': 4278233685, 'text': '   '}})
            except:
                self.hwnd = None
    
    def stop(self):
        if self.hwnd:
            try:
                self.hwnd.send("SetInputSettings", {"inputName": "TextFrame", "inputSettings": {
                        'bk_color': 4278190080, 'text': '   '}})
            except:
                self.hwnd = None

    def release(self):
        if self.hwnd:
            self.hwnd.base_client.ws.close()
            self.hwnd=None


class Slave_OBS(Slave):
    def __init__(self, ip='localhost', port=4455):
        super().__init__()
        self.ip = ip
        self.port = port
        self.hwnd = None

    def check_ready(self) -> bool:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.settimeout(0.1)
        if tcp_socket.connect_ex((self.ip, self.port)) == 0: # connection successful
            tcp_socket.close()
        else:
            self.hwnd, self.ready = None, False
            return self.ready
        
        try:
            cl = obs.ReqClient(host=self.ip, port=self.port)
        except Exception:
            cl = None
        self.hwnd = cl
        self.ready = cl is not None
        return self.ready
    
    def start(self):
        if self.hwnd:
            try:
                self.hwnd.start_record()
            except:
                pass

    def stop(self):
        if self.hwnd:
            try:
                self.hwnd.stop_record()
            except:
                pass

    def release(self):
        if self.hwnd:
            self.hwnd.base_client.ws.close()
            self.hwnd=None


class Slave_Miniscope(Slave):
    def __init__(self, ip='localhost', port=20172, label='Miniscope'):
        super().__init__()
        self.hwnd = None
        self.ip = ip
        self.port = port
        self.send_start_byte = "start_record".encode("utf-8")
        self.send_stop_byte = "stop_record".encode("utf-8")
        self.device_name = label

    def check_ready(self) -> bool:
        self.release()
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.settimeout(0.1)
        if tcp_socket.connect_ex((self.ip, self.port)) == 0: # connection successful
            log_slave(f'Found {self.device_name}.')
        else:
            tcp_socket = None
        self.hwnd = tcp_socket
        self.ready = tcp_socket is not None
        return self.ready

    def start(self):
        send_data_byte = "start_record".encode("utf-8")
        if self.hwnd:
            self.hwnd.send(send_data_byte)

    def stop(self):
        send_data_byte = "stop_record".encode("utf-8")
        if self.hwnd:
            self.hwnd.send(send_data_byte)

    def __read_response(self):
        from_server_msg = self.hwnd.recv(1024)
        print(from_server_msg.decode("utf-8"))
    
    def release(self):
        if self.hwnd:
            self.hwnd.close()
            del self.hwnd
            self.hwnd = None


class Slave_EPStudio(Slave_Miniscope):
    def __init__(self, ip='10.50.36.170', port=20172, label='EPStudio'):
        super().__init__(ip=ip, port=port, label=label)
        

class Slave_USVOld(Slave):
    def __init__(self):
        super().__init__()
        self.titlename = "Avisoft-RECORDER USGH  (RECORDER.INI)"
        self.hwnd = None
        self.shell = win32com.client.Dispatch("WScript.Shell")
    
    def check_ready(self) -> bool:
        hwnd = win32gui.FindWindow(None, self.titlename)
        if hwnd==0:
            self.hwnd = None
        else:
            self.hwnd = hwnd
            log_slave('Found USV.')
        self.ready = self.hwnd is not None
        return self.ready

    def start(self):
        self.shell.SendKeys('%')
        log_slave('USV_Start', self.hwnd)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.hwnd)

        win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
        win32api.keybd_event(win32con.VK_F3,0,0,0)     # F3
        win32api.keybd_event(win32con.VK_F3,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0) 

        self.shell.SendKeys('%')
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.hwnd)

        win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
        win32api.keybd_event(win32con.VK_F3,0,0,0)     # F3
        win32api.keybd_event(win32con.VK_F3,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0) 
        
    def stop(self):
        self.shell.SendKeys('%')
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.hwnd)

        win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
        win32api.keybd_event(win32con.VK_F5,0,0,0)     # F5
        win32api.keybd_event(win32con.VK_F5,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0) 

        self.shell.SendKeys('%')
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.hwnd)

        win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
        win32api.keybd_event(win32con.VK_F5,0,0,0)     # F5
        win32api.keybd_event(win32con.VK_F5,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0) 
        log_slave('USV Stopped', self.hwnd)



class Slave_USV(Slave_USVOld):
    def start(self):
        cmdstart = 'CMCDDE.EXE RECORDER main "start"'
        os.popen(cmdstart) #非阻塞式

        self.shell.SendKeys('%')
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.hwnd)
        log_slave('USV_Start')
        
    def stop(self):
        cmdstop = 'CMCDDE.EXE RECORDER main "stop"'
        os.popen(cmdstop)  #非阻塞式

        self.shell.SendKeys('%')
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(self.hwnd)
        log_slave('USV Stopped')


class Slave_RTSP_CAM(Slave):
    def __init__(self, rtsp_list):
        super().__init__()
        self.rtsp_list = rtsp_list
        self.outdir = 'E:/rtsp_cam'
        if rtsp_list:
            os.makedirs(self.outdir, exist_ok=True)
        self.process_l = []

    def check_ready(self) -> bool:
        self.release()
        return True
    
    def start(self):
        now = datetime.now()
        formatted_time = now.strftime('%Y-%m-%d_%H:%M:%S')
        cmd_l = []
        for i, rtsp in enumerate(self.rtsp_list):
            filename = os.path.join(self.outdir, f'{formatted_time}_cam{i+1}.mp4')
            cmd_l.append(f'ffmpeg -i {rtsp} -c copy {filename}')
        
        self.process_l = []
        for cmd in cmd_l:
            self.process_l.append(subprocess.Popen(cmd, shell=True))

    def stop(self):
        for p in self.process_l:
            p.terminate()
        self.process_l = []

    def release(self):
        if len(self.process_l):
            self.stop()
