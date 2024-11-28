import threading
from time import sleep

from Sensor import Sensor, SensorError

print("done")


def data_thread(arg):
    try:
        scd40 = Sensor(comport=arg)
        while True:
            scd40.getData()
            print(f"T:{scd40.getTemperature()},H:{scd40.getHumidity()},CO2:{scd40.getCO2()}")
            sleep(1)
    except SensorError as err:
        print(err)

def draw_gui():
    pass
def main():
    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()

    for port, desc, hwid in ports:
        print(f"{port}: {desc} [{hwid}]")
    # return
    data_thread_handle = threading.Thread(target=data_thread,args=("COM3",))
    data_thread_handle.start()

main()