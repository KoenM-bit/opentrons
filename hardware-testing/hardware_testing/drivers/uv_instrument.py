#! /usr/bin/env python

"""
This driver is meant to be used with the GT-521S Particle Counter.
For more information about this Device, look at the following link:
https://metone.com/wp-content/uploads/2019/10/GT-521S-9800-Rev-D.pdf

Author: Carlos Fernandez
Date: 6/23/2020

"""
import serial
import os, sys, datetime, time
import re

class uv_Driver:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200,
                parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS, timeout=1,simulate=False):
        if simulate:
            self.particle_counter = None
        else:
            self.port = port
            self.baudrate = baudrate
            self.timeout = timeout
            self.particle_counter = serial.Serial(port = self.port,
                                        baudrate = self.baudrate,
                                        timeout = self.timeout)
       
    
    def get_uv_(self):
        """获取UV值和温度值"""
        self.particle_counter.flush()
        self.particle_counter.flushInput()
        try:
            # Modbus RTU 请求帧数据（示例数据） 
            # 01 04 01 C4 00 04 B1 C8 
            request_frame = bytearray([0x01, 0x04, 0x01, 0xC4, 0x00, 0x04,0xB1, 0xC8])
            # 发送请求
            self.particle_counter.write(request_frame)
            # 延时等待响应
            time.sleep(0.1)
            # 读取响应数据
            response_frame = self.particle_counter.read_all()
            print("Modbus响应帧:", response_frame.hex())
            return response_frame.hex()

        except Exception as e:
            print(f"发生错误: {e}")
    def parse_modbus_data(self,modbus_data_hex):
        # 将十六进制字符串转换为字节数组
        modbus_data_bytes = bytes.fromhex(modbus_data_hex)

        # 解析 Modbus 数据
        device_address = modbus_data_bytes[0]
        function_code = modbus_data_bytes[1]
        byte_count = modbus_data_bytes[2]
        
        uvdatahex = modbus_data_bytes[3:7]  # 去除设备地址、功能码、字节计数和 CRC 校验
        Tempvalhex = modbus_data_bytes[7:-2]

        uvdata = int.from_bytes(uvdatahex, byteorder='big', signed=False)  # 将数据转换为十进制
        Tempval = int.from_bytes(Tempvalhex, byteorder='big', signed=False)  # 将数据转换为十进制
        if uvdata != 0:
            uvdata = round(int(str(uvdata)[:-4]) / 100,1)
        if Tempval != 0:
            Tempval = round(int(str(Tempval)[:-4]) / 100,1)

        crc = int.from_bytes(modbus_data_bytes[-2:], byteorder='big')  # 获取 CRC 校验值

        return {
            "Device Address": hex(device_address),
            "Function Code": hex(function_code),
            "Byte Count": hex(byte_count),
            "uvdata": uvdata,
            "Tempval": Tempval,
            "CRC": hex(crc)
        }

    def get_stable_uv(self):
        datalist = []
        for i in range(3):

            modbus_data_hex = ''
            self.particle_counter.flush()
            self.particle_counter.flushInput()
            try:
                # Modbus RTU 请求帧数据（示例数据） 
                # 01 04 01 C4 00 04 B1 C8 
                request_frame = bytearray([0x01, 0x04, 0x01, 0xC4, 0x00, 0x04,0xB1, 0xC8])
                # 发送请求
                self.particle_counter.write(request_frame)
                # 延时等待响应
                time.sleep(0.1)
                # 读取响应数据
                response_frame = self.particle_counter.read_all()
                print("Modbus响应帧:", response_frame.hex())
                modbus_data_hex = response_frame.hex()

            except Exception as e:
                print(f"发生错误: {e}")
                
            # 解析 Modbus 数据
            device_address = modbus_data_hex[0:2]
            function_code = modbus_data_hex[2:4]
            byte_count = modbus_data_hex[4:6]
            
            uvdatahex = modbus_data_hex[6:10]  # 去除设备地址、功能码、字节计数和 CRC 校验
            Tempvalhex = modbus_data_hex[14:18]
            uvdata = int(uvdatahex, 16)
            Tempval = int(Tempvalhex, 16)
            
            if uvdata != 0:
                uvdata = round(int(str(uvdata)) / 10,1)
            if Tempval != 0:
                Tempval = round(int(str(Tempval)) / 10,1)
            # print("UVdata:", uvdata)
            # print("Tempval:", Tempval)
            # #crc = int.from_bytes(modbus_data_bytes[-2:], byteorder='big')  # 获取 CRC 校验值
            datalist.append(uvdata)
            # return {
            #     "Device Address": hex(device_address),
            #     "Function Code": hex(function_code),
            #     "Byte Count": hex(byte_count),
            #     "uvdata": uvdata,
            #     "Tempval": Tempval,
            #     "CRC": hex(crc)
            # }
        return max(datalist)

if __name__ == '__main__':
    port = "/dev/tty.usbserial-130"
    a = uv_Driver(port,simulate=True)
    # modbus_data_hex = a.get_uv_()
    # 解析 Modbus 数据
    cccc = "0104080897000000ca0000e35c"
    parsed_data = a.parse_modbus_data(cccc)

    # 打印解析结果
    for key, value in parsed_data.items():
        print(f"{key}: {value}")