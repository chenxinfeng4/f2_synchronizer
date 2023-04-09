# conda activate py310
#!pyinstaller.exe --noconsole .\f2_sync.py -i .\F2.ico --add-data "F2.ico;." --hidden-import win32api --hidden-import  pythonwin --hidden-import win32com --hidden-import win32comext --hidden-import isapi
# python D:\f2_sync_project\f2_sync.py
import pystray
from pystray import Menu as menu, MenuItem as item
from PIL import Image
import os
import sys
from global_hotkeys import register_hotkeys, start_checking_hotkeys, stop_checking_hotkeys
import socketserver
import threading
import win32ui
from f2_slaves import Slave, Slave_OBS, Slave_Miniscope, Slave_USV
import time

is_recording = True

singleton_port = 20170
socket_server_port = 20169
app_enable=1
countdown_timer_enable=1
countdown_timer_seconds=1*60+1 #15*60+1

slave_dict = {'OBS 录像': [True, Slave_OBS()],
              'USV 超声': [True, Slave_USV()],
              '小显微镜': [True, Slave_Miniscope()]}

class MyMenuItem(item):
    def __init__(self, title, callback, checked:bool=False):
        self.checked_ = checked
        super().__init__(title, callback, checked=lambda x:self.checked_)

def tic():
    """
    Records the current time.
    """
    global _start_time
    _start_time = time.time()

def toc(verbose=True):
    """
    Prints the time elapsed since `tic()` was called.

    Parameters:
        verbose: if True (default), print a message containing the elapsed time.

    Returns:
        The elapsed time in seconds.
    """
    global _start_time
    elapsed = time.time() - _start_time
    if verbose:
        print('Elapsed time: {:.4f} seconds.'.format(elapsed))
    return elapsed

def log_socket(*args, **kargs):
    print("[Socket]", *args, **kargs)

def log_switch(*args, **kargs):
    print("[Switch]", *args, **kargs)

def log_timer(*args, **kargs):
    print("[Timer]", *args, **kargs)

def log_manager(*args, **kargs):
    print("[Manager]", *args, **kargs)

def acquire_singleton(port):
    try:
        s = socketserver.TCPServer(('127.0.0.1',port),  None)
        # s.server_close()
        return True, s
    except:
        win32ui.MessageBox("[F2 同步助手] 未退出", "错误", 0)
        return False, None
    

class SingletonManager:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonManager, cls).__new__(cls)
            cls.instance._init()
        return cls.instance

    def _init(self):
        # 1. create socket server
        # s_server = socketserver.TCPServer(('0.0.0.0', socket_server_port), MyTCPHandler)
        s_server = ThreadedTCPServer(('0.0.0.0', socket_server_port), MyTCPHandler)
        self.s_serer_p = threading.Thread(target=s_server.serve_forever)
        self.s_serer_p.daemon = True
        self.s_serer_p.start()

        # 2. binding hotkey
        bindings = [
            [["control","f2"], lambda: self.switch_record_world(True), None],
            [["control","f4"], lambda: self.switch_record_world(False), None],
        ]
        register_hotkeys(bindings)
        self.enable_hotkeys(True)
        print("Ready. \n1. [Ctrl+F2] to start. \n2. [Ctrl+F4] to stop.")

        # 3. rigister icon.
        self.app_hotkey_enable = True
        self.app_socket_enable = True
        # devices_items = [item(k, self.on_device_enable, checked=lambda item: v[0]) for (k,v) in slave_dict.items()]
        devices_items = [MyMenuItem(k, self.on_device_enable, checked=True) for (k,v) in slave_dict.items()]
        self.icon = pystray.Icon(
            'test name',
            icon=self.create_image(),
            menu=menu(
                item("选择同步设备", 
                     menu(*devices_items)),
                item('启用快捷键控制', 
                    self.on_clicked_hotkey,
                    checked=lambda item: self.app_hotkey_enable
                ),
                item('启用socket server控制', 
                    self.on_clicked_socket,
                    checked=lambda item: self.app_socket_enable
                ),
                item('使用倒计时',
                    self.on_clicked_countdown_timer,
                    checked=lambda item: countdown_timer_enable
                ),
                item('退出', self.on_exit),
                ))
        
        # 4. Countdown timer
        self.new_countdown_timer()

    def switch_record_world(self, switch, 
                        enablecountdowntimer=True):
        world = [v[1] for (k,v) in slave_dict.items() if v[0]]
        if enablecountdowntimer:
            log_switch('switch_record_world', switch)
            self.do_countdown(switch=switch)

        log_manager('Switch', switch)
        threads = [threading.Thread(target=obj.switch, args=(switch,)) for obj in world]
        _ = [t.start() for t in threads]
        _ = [t.join() for t in threads]

        if switch:
            self.icon.icon = self.image_record
            # self.on_notify('开始记录啦', '开始')
        else:
            self.icon.icon = self.image
            # self.on_notify('记录已经结束', '结束') 

    def new_countdown_timer(self):
        self.countdown_timer = threading.Timer(countdown_timer_seconds, self.do_countdown_callback)

    def do_countdown_callback(self):
        log_timer('Stopping')
        toc()
        self.switch_record_world(False, False)

    def do_countdown(self, switch):
        countdown_timer_alive = self.countdown_timer.is_alive()
        if switch==True and countdown_timer_alive==False and countdown_timer_enable:
            used = getattr(self.countdown_timer, 'used', False)
            if used:
                self.new_countdown_timer()
            self.countdown_timer.start()
            self.countdown_timer.used = True
            log_timer('Start')
            tic()
        elif switch==False and countdown_timer_alive==True:
            self.countdown_timer.cancel()
            log_timer('Manual stop')
            toc()
            self.new_countdown_timer()
        elif switch==True and countdown_timer_alive==True:
            log_timer('Already started. Ignore.')
        elif switch==False and countdown_timer_alive==True:
            log_timer('Already stopped. Ignore.')

    def serve_forever(self):
        self.icon.run()

    def status(self):
        if countdown_timer_enable:
            return 'countdown timer enabled'
        else:
            return 'countdown timer disabled'

    def create_image(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        iconpath = os.path.join(application_path, 'F2.ico')
        image = Image.open(iconpath)
        image_record = Image.open(os.path.join(application_path, 'F2_record.ico'))
        self.image = image
        self.image_record = image_record
        return image
    
    def on_device_enable(self, icon:pystray.Icon, item:MyMenuItem):
        item.checked_ = not item.checked_
        print(item.text, item.checked_)
        slave_dict[item.text][0] = item.checked_

    def on_clicked_hotkey(self, icon, item):
        # global app_enable
        self.app_hotkey_enable = not item.checked
        self.enable_hotkeys(self.app_hotkey_enable)

    def on_clicked_socket(self, icon, item):
        # global app_enable
        self.app_socket_enable = not item.checked
        log_manager("Socket enabled: {}".format(self.app_socket_enable))

    def on_clicked_countdown_timer(self, icon, item):
        global countdown_timer_enable
        countdown_timer_enable = not item.checked

    def on_exit(self, icon, item):
        icon.stop()
        os._exit(1)

    def on_notify(self, msgbody:str, msgtitle:str):
        self.icon.notify(msgbody, msgtitle)
        threading.Timer(5, self.icon.remove_notification).start()

    def enable_hotkeys(self, enable:bool):
        if enable:
            start_checking_hotkeys()
        else:
            stop_checking_hotkeys()
            log_manager('Stop hot keys')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        log_socket("conn is :",self.request) # conn
        log_socket("addr is :",self.client_address) # addr
        self.singletonManager = SingletonManager()
    
        while True:
            try:
                #收消息
                data = self.request.recv(1024)
                msg = data.decode("utf-8")
                if not data:break
                log_socket("收到客户端的消息是",msg)
                #发消息
                self.request.sendall(data.upper())
                self.msgfilter(msg)
            except Exception as e:
                log_socket(e)

        log_socket('Closed a request')

    def msgfilter(self, msg:str):
        if self.singletonManager.app_socket_enable:
            callbacks = {'start_record': lambda:self.singletonManager.switch_record_world(switch=True),
                        'stop_record': lambda: self.singletonManager.switch_record_world(switch=False),
                        'query_countdowntimer': lambda : None}
            for callkey, callfun in callbacks.items():
                if callkey in msg:
                    log_socket('执行命令')
                    callfun()
                    break
            else:
                log_socket("没有找到对应的回调函数", msg)
        else:
            log_socket("没有开启socket control")
    


if __name__=='__main__':
    res, sockethandle = acquire_singleton(singleton_port)
    if not res:
        print('In singleton program mode')
        os._exit(1)

    SingletonManager().serve_forever()
