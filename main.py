import threading
from threading import Lock
from tkinter import *
from tkinter import ttk
from time import sleep
import serial.tools.list_ports

from Sensor import Sensor, SensorError

print("done")

g_Temperature=0.0
g_Humidity=0
g_CO2=0

exit_signal = False
g_mutex_readings=Lock()

def data_thread(arg):
    global g_mutex_readings
    global exit_signal
    global g_Temperature
    global g_Humidity
    global g_CO2
    try:
        scd40 = Sensor(comport=arg)
        while True:
            if exit_signal is True:
                return
            scd40.getData()
            g_mutex_readings.acquire()
            print("data-mutex[acq]")
            # print(f"T:{scd40.getTemperature()},H:{scd40.getHumidity()},CO2:{scd40.getCO2()}")
            g_Temperature = scd40.getTemperature()
            g_Humidity = scd40.getHumidity()
            g_CO2 = scd40.getCO2()
            g_mutex_readings.release()
            print("data-mutex[rel]")
            print(f"T:{g_Temperature},H:{g_Humidity},CO2:{g_CO2}")
            sleep(1)
    except SensorError as err:
        print(err)
def update_readings(root, t_var:StringVar,h_var:StringVar,co2_var:StringVar):
    global g_mutex_readings
    global g_Temperature
    global g_Humidity
    global g_CO2

    # while True:
    g_mutex_readings.acquire()
    print("ui-mutex[acq]")
    t_var.set(str(g_Temperature))
    h_var.set(str(g_Humidity))
    co2_var.set(str(g_CO2))
    g_mutex_readings.release()
    print("ui-mutex[rel]")
    root.after(100,update_readings,root,t_var,h_var,co2_var)


def draw_gui():


    # create window first
    root = Tk()
    root.title("thermalComfortDashboard 1.0")
    root.minsize(width=1000,height=1000)
    # root.maxsize(width=1000, height=1000)

    #vars
    t_var = StringVar()
    h_var = StringVar()
    co2_var = StringVar()

    #create a Frame
    frame_temperature=ttk.Frame(root,width=50,height=50,borderwidth=5,relief="raised",padding=20)
    frame_temperature.pack(side=LEFT,anchor="nw",padx=10,pady=10)
    #create frame for temperature
    temperatureLabel=ttk.Label(frame_temperature,text="Temperature",font=("Arial",30), borderwidth=1,width=15,anchor=CENTER)
    temperatureLabel['relief']=SOLID
    temperatureLabel.pack()
    temperatureLabel1 = ttk.Label(frame_temperature, text="20.3", font=("Arial", 30), borderwidth=1,padding=5,textvariable=t_var)
    temperatureLabel1['relief']=SOLID
    temperatureLabel1.pack(pady=5)


    # create a humidity Frame
    frame_humidity = ttk.Frame(root, width=50, height=50, borderwidth=5, relief="raised", padding=20)
    frame_humidity.pack(side=LEFT, anchor="nw", padx=10, pady=10)
    # create frame for temperature
    humidityLabel = ttk.Label(frame_humidity, text="Humidity", font=("Arial", 30), borderwidth=1,width=15,anchor=CENTER)
    humidityLabel['relief']=SOLID
    humidityLabel.pack()
    humidityLabel1 = ttk.Label(frame_humidity, text="100 %", font=("Arial", 30), borderwidth=1, padding=5,textvariable=h_var)
    humidityLabel1['relief']=SOLID
    humidityLabel1.pack(pady=5)

    frame_CO2 = ttk.Frame(root, width=50, height=50, borderwidth=5, relief="raised", padding=20)
    frame_CO2.pack(side=LEFT, anchor="nw", padx=10, pady=10)
    # create frame for temperature
    CO2Label = ttk.Label(frame_CO2, text="CO2", font=("Arial", 30), borderwidth=1,width=15,anchor=CENTER)
    CO2Label['relief']=SOLID
    CO2Label.pack()
    CO2Label1 = ttk.Label(frame_CO2, text="2000 ppm", font=("Arial", 30), borderwidth=1, padding=5,textvariable=co2_var)
    CO2Label1['relief']=SOLID

    CO2Label1.pack(pady=5)
    root.after(100,update_readings,root,t_var,h_var,co2_var)

    but=ttk.Button(root,text="BUTTON!!")
    but.pack()
    selected = StringVar()
    C_radio = ttk.Radiobutton(root, text='Celsius', value='Value 1', variable=selected,state="")
    F_radio = ttk.Radiobutton(root, text='Fahrenheit', value='Value 2', variable=selected)

    C_radio.pack()
    F_radio.pack()
    root.mainloop()

def main():
    global exit_signal

    ports = serial.tools.list_ports.comports()

    for port, desc, hwid in ports:
        print(f"{port}: {desc}")
    # return
    data_thread_handle = threading.Thread(target=data_thread,args=("COM9",))
    data_thread_handle.start()


    gui_thread_handle = threading.Thread(target=draw_gui)
    gui_thread_handle.start()

    # uiUpdate_thread_handle = threading.Thread(target=update_readings)
    # uiUpdate_thread_handle.start()

    gui_thread_handle.join()
    print("return GUI thread!!!!!")
    exit_signal = True
    data_thread_handle.join()
    print("return data thread!!!!!")
main()