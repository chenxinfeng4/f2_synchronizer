from serialproxy import  SerialCommunicator
import socketserver

serial_com = SerialCommunicator('COM13')  # 将 'COM1' 替换为你的串口名称
serial_com.connect()
serial_com.send_message("Hello from Python!")
print(serial_com.receive_message())


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            try:
                #收消息
                data = self.request.recv(1024)
                msg = data.decode("utf-8")
                if not data:break
                print("收到客户端的消息是",msg)
                #发消息
                self.request.sendall(data.upper())
                self.msgfilter(msg)
            except Exception as e:
                print(e)

        print('Closed a request')

    def msgfilter(self, msg:str):
        callbacks = {'start_record': lambda:serial_com.send_message("b"),
                    'stop_record': lambda: serial_com.send_message("c")}
        for callkey, callfun in callbacks.items():
            if callkey in msg:
                print('执行命令')
                callfun()
                break
        else:
            print("没有找到对应的回调函数", msg)


HOST, PORT = "127.0.0.1", 20175



if __name__ == "__main__":
    # Create the server, binding to localhost on port 9999
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
