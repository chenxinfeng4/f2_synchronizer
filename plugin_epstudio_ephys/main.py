#!/home/nexdev/miniconda3/envs/epstudio/bin/python
# conda activate epstudio
# python epstudio_api_socket.py
# nc -q 1 10.50.31.76 20172 < <(echo "query_record")
# nc -q 1 10.50.31.76 20172 < <(echo "start_record")
# nc -q 1 10.50.31.76 20172 < <(echo "stop_record")

import socketserver
HOST, PORT = "0.0.0.0",20172

from epstudiosdk.client import EpClient
from epstudiosdk.bean.collection.CollectionDeviceBean import CollectionDeviceBean
from epstudiosdk.collection.Collection import Collection

def create_collection():
    # -----以下内容于全局调用 start-----
    # 1.创建 client
    client = EpClient(init_user_status=True)
    # 2.创建请求参数
    device = CollectionDeviceBean("E4:24:EF:C7:07:87", samplingRate=1000, channelStatus=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
    collection = Collection(client=client, device_list=[device], record_status=False)
    return collection

collection = create_collection()
current_status = 'stop'

def start_record():
    global current_status
    if current_status == 'start':
        print("采集器正在采集数据，请先停止采集器")
        # return "采集器正在采集数据，请先停止采集器"

    # 4.开始采集
    print(collection.start_collection())

    # 5.开始记录数据
    collection.start_record()

    current_status = 'start'
    return "采集器已开始采集数据"

def stop_record():
    global current_status
    if current_status == 'stop':
        print("采集器已停止采集数据")
        return "采集器已停止采集数据"
    
    # 5.开始记录数据
    collection.stop_record()

    # 4.停止采集
    print(collection.stop_collection())

    current_status = 'stop'
    return "采集器已停止采集数据"


def query_record():
    return current_status


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client

        print("conn is :",self.request) # conn
        print("addr is :",self.client_address) # addr

        try:
            while True:
                #收消息
                data = self.request.recv(1024)
                if not data:break
                msg = data.decode("utf-8").strip()
                print("收到客户端的消息是",msg)
                #发消息
                rep = self.msgfilter(msg)
                self.request.sendall(str(rep).encode("utf-8"))
                self.request.sendall(data.upper())
        except Exception as e:
            print(e)

        print('Closed a request')

    def msgfilter(self, msg:str):
        callbacks = {'start_record':start_record,
                     'stop_record':stop_record,
                     'query_record':query_record}
        if msg in callbacks:
            return callbacks[msg]()
        else:
            return 'unknown'


if __name__ == "__main__":
    # Create the server, binding to localhost on port 9999
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print('start server')
        server.serve_forever()
    
