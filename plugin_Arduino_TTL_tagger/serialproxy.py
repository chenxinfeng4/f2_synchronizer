import serial
import serial.tools.list_ports
import time


def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    # drop 'COM1' if it exists
    ports = [port for port in ports if port.device != 'COM1']
    return [port.device for port in ports]


class SerialCommunicator:
    def __init__(self, com_port, baud_rate=9600, timeout=1):
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_port = None
        self.isconnect = False
        self.isValid = False

    def connect(self):
        if self.isconnect:
            print(f"弹出串口 {self.com_port}")
            self.close()

        try:
            self.serial_port = serial.Serial(self.com_port, self.baud_rate, timeout=self.timeout)
            print(f"连接到串口 {self.com_port}")
            self.isconnect = True
        except serial.SerialException as e:
            self.isconnect = False
            self.isValid = False
            print(f"无法连接到串口 {self.com_port}: {e}")

        time.sleep(2.8)
        outcome = self.receive_message()
        self.isValid = outcome == "Hello from Arduino-Evt-TTL-tagger"
        if self.isValid:
            print("串口成功识别为 Arduino-Evt-TTL-tagger")
        else:
            print("串口未能识别为 Arduino-Evt-TTL-tagger")
            print("outcome is", outcome)

    def send_message(self, message):
        if self.serial_port:
            self.serial_port.write(message.encode())
            time.sleep(0.02)
            return self.receive_message()
        else:
            print("未连接到串口，无法发送消息")
            return ''

    def receive_message(self):
        msg = self.serial_port.readline().decode().strip()
        if self.serial_port.in_waiting > 0:
            msg = self.serial_port.read(self.serial_port.in_waiting).decode().strip()
        return msg

    def close(self):
        if self.serial_port:
            self.serial_port.close()
            if self.isconnect:
                print(f"关闭串口 {self.com_port}")
        self.isconnect = False
        self.isValid = False

    def __del__(self):
        self.close()


if __name__ == '__main__':
    # 使用示例
    serial_com = SerialCommunicator('COM14')  # 将 'COM1' 替换为你的串口名称
    serial_com.connect()
    serial_com.send_message("Hello from Python!")
    print(serial_com.receive_message())
    serial_com.close()
