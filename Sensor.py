import time

from pymodbus.client import ModbusSerialClient


class SensorError(Exception):
    def __init__(self, action):
        super().__init__(action)


class Sensor:

    def check_crc(self, data, crc_received):
        data = data.to_bytes(2)
        CRC8_POLYNOMIAL = 0x31
        CRC8_INIT = 0xFF
        crc = CRC8_INIT
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ CRC8_POLYNOMIAL
                else:
                    crc <<= 1
                crc &= 0xFF  # Ensure CRC remains 8-bit
        # print(f"calculated crc is {crc}")
        # print(f"received crc is {crc_received}")
        if crc == crc_received:
            return True
        else:
            return False

    def __init__(self, comport: str):

        self.__Temperature = 0.0
        self.__Humidity = 0
        self.__Co2 = 0

        # serial connection parameters
        self.__COM_Port = ""
        self.__BAUD_Rate = 115200
        # Modbus register needed
        self.__MODBUS_Slave_address = 1
        self.__MODBUS_register_start_address = 0
        self.__COM_Port_isOpen = False

        # object of modbus lib once connected
        self.__ModbusClient = None
        self.__COM_Port = comport
        self.__ModbusClient = ModbusSerialClient(
            port=comport,
            baudrate=115200,
            stopbits=1,
            parity="N",
            bytesize=8,
            timeout=1
        )
        if self.__ModbusClient.connect() is False:
            raise SensorError(f"error opening {comport}")
        else:
            self.__COM_Port_isOpen = True
            print("sensor created")

    # destructor is needed because we cant leave port open
    def __del__(self):
        if self.__COM_Port_isOpen is True:
            # com port needs to be closed safely before deleting
            self.__ModbusClient.close()
        print('Sensor Deleted')

    def getTemperature(self):
        return round(self.__Temperature, 1)

    def getHumidity(self):
        return round(self.__Humidity)

    def getCO2(self):
        return round(self.__Co2)

    def getData(self):
        if self.__COM_Port_isOpen is True:
            # Read holding registers
            # query sent 01 03 00 00 00 06 c5 c8
            # response 01 03 0c 01 f4 00 33 66 67 00 a2 5e b9 00 3c 93 70
            # expected response [500, 51, 26215, 162, 24249, 60]
            t1 = time.time()
            result = self.__ModbusClient.read_holding_registers(self.__MODBUS_register_start_address, 6,
                                                                self.__MODBUS_Slave_address)
            # print(type(result))
            t2 = time.time()
            print(f"got data in {t2 - t1} sec")
            if not result.isError():
                print(result.registers)
            # if self.check_crc(0xbeef,0x92) is True:
            # TODO
            if (self.check_crc(result.registers[0], result.registers[1]) is True and
                    self.check_crc(result.registers[2],result.registers[3]) is True and
                    self.check_crc(result.registers[4], result.registers[5]) is True
            ):
            # if (1):
                    self.__Co2 = result.registers[0]
                    self.__Temperature = (-45) + (175 * (result.registers[2] / (pow(2, 16) - 1)))
                    self.__Humidity = 100 * (result.registers[4] / (pow(2, 16) - 1))
            else:
                print(result)
