from functools import partial
import threading
from threading import Lock
from tkinter import *
from tkinter import ttk
from time import sleep
import serial.tools.list_ports

from Sensor import Sensor, SensorError

print("done")

g_Temperature = 0.0
g_Humidity = 0
g_CO2 = 0

exit_signal = False
g_mutex_readings = Lock()
g_selected_temperature_unit=None


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
            # print("data-mutex[acq]")
            # print(f"T:{scd40.getTemperature()},H:{scd40.getHumidity()},CO2:{scd40.getCO2()}")
            g_Temperature = scd40.getTemperature()
            g_Humidity = scd40.getHumidity()
            g_CO2 = scd40.getCO2()
            g_mutex_readings.release()
            # print("data-mutex[rel]")
            print(f"T:{g_Temperature},H:{g_Humidity},CO2:{g_CO2}")
            sleep(1)
    except SensorError as err:
        print(err)


def update_readings(root, t_var: StringVar, h_var: StringVar, co2_var: StringVar):
    global g_mutex_readings
    global g_Temperature
    global g_Humidity
    global g_CO2
    global g_selected_temperature_unit

    # while True:
    g_mutex_readings.acquire()
    # print("ui-mutex[acq]")
    if g_selected_temperature_unit.get() == "°C":
        t_var.set(str(g_Temperature))
    else:
        t_var.set(str(round(((g_Temperature*9/5)+32),1)))

    h_var.set(str(g_Humidity))
    co2_var.set(str(g_CO2))
    g_mutex_readings.release()
    # print("ui-mutex[rel]")
    root.after(100, update_readings, root, t_var, h_var, co2_var)

def radio_print(unit_var:StringVar):
    global g_selected_temperature_unit
    unit_var.set(g_selected_temperature_unit.get())

    print(f"{g_selected_temperature_unit.get()} is set")

def draw_gui():

    # create window first
    root = Tk()
    root.title("thermalComfortDashboard 1.0")
    root.minsize(width=1000, height=1000)
    # root.maxsize(width=1000, height=1000)

    # vars
    t_var = StringVar()
    h_var = StringVar()
    co2_var = StringVar()
    unit_var = StringVar()
    unit_var.set("°C")
    global g_selected_temperature_unit

    # create a Frame for temperature -------------------------------------------------------
    frame_temperature = ttk.Frame(
        root,
        width=50,
        height=50,
        borderwidth=5,
        relief="raised",
        padding=20,
    )
    frame_temperature.pack(side=LEFT, anchor="nw", padx=10, pady=10)

    # 1.create a temperature text Label
    label_temperatureText = ttk.Label(
        frame_temperature,
        text="Temperature",
        font=("Arial", 30),
        borderwidth=1,
        width=15,
        anchor=CENTER,
    )
    label_temperatureText["relief"] = SOLID
    label_temperatureText.pack()
    
    # 2. create a temperature reading Label
    label_temperatureReading = ttk.Label(
        frame_temperature,
        text="20.3",
        font=("Arial", 30),
        borderwidth=1,
        padding=5,
        textvariable=t_var,
        anchor="e"

    )
    label_temperatureReading["relief"] = SOLID
    label_temperatureReading.pack(pady=5, side=LEFT,fill="x",expand=TRUE)

    # 3. create a label for temperature units text
    
    label_temperatureUnit = ttk.Label(
        frame_temperature,
        text="",
        font=("Arial", 30),
        borderwidth=1,
        padding=5,
        textvariable=unit_var,
        anchor="w"
    )
    label_temperatureUnit["relief"] = SOLID
    label_temperatureUnit.pack(pady=5, side=LEFT,fill="x",expand=TRUE)


    # 4. create a frame to hold radio buttons for units
    frame_radio_units = ttk.Frame(
        frame_temperature
    )
    frame_radio_units.pack(anchor="w",side="left")
    frame_radio_units["relief"]=SOLID
    
    # variable to hold state of selected radio button
    g_selected_temperature_unit = StringVar()
    g_selected_temperature_unit.set("°C")
    # 5. create radion buttons and pack
    radio_celsius = ttk.Radiobutton(
        frame_radio_units, text="Celsius", value="°C", variable=g_selected_temperature_unit, command=partial(radio_print,unit_var)
    )
    radio_Fahrenheit = ttk.Radiobutton(
        frame_radio_units, text="Fahrenheit", value="°F", variable=g_selected_temperature_unit, command=partial(radio_print,unit_var)
    )
    radio_celsius.pack(fill=X,expand=TRUE)
    radio_Fahrenheit.pack(fill=X,expand=TRUE)
    

    # ------create a Frame for humidity -------------------------------------------------------

    frame_humidity = ttk.Frame(
        root, width=50, height=50, borderwidth=5, relief="raised", padding=20
    )
    frame_humidity.pack(side=LEFT, anchor="nw", padx=10, pady=10)
    
    # 1. create label for humidity text
    label_humidityText = ttk.Label(
        frame_humidity,
        text="Humidity",
        font=("Arial", 30),
        borderwidth=1,
        width=15,
        anchor=CENTER,
    )
    label_humidityText["relief"] = SOLID
    label_humidityText.pack()

    # 2. create label for humidity reading
    label_humidityReading = ttk.Label(
        frame_humidity,
        text="100 %",
        font=("Arial", 30),
        borderwidth=1,
        padding=5,
        textvariable=h_var,
        anchor="e"
    )
    label_humidityReading["relief"] = SOLID
    label_humidityReading.pack(pady=5,side=LEFT,expand=True,fill="x")
    
    # 3. create label for humidity units
    label_humidityUnits = ttk.Label(
    frame_humidity,
    text="%",
    font=("Arial", 30),
    borderwidth=1,
    padding=5,
    anchor="w"
    )
    label_humidityUnits["relief"] = SOLID
    label_humidityUnits.pack(pady=5,side=LEFT,expand=TRUE,fill="x")
    
    
    # ------create a Frame for CO2 -------------------------------------------------------
    frame_CO2 = ttk.Frame(
        root, width=50, height=50, borderwidth=5, relief="raised", padding=20
    )
    frame_CO2.pack(side=LEFT, anchor="nw", padx=10, pady=10)
    
    # 1. create label for co2 text
    label_CO2Text = ttk.Label(
        frame_CO2,
        text="CO2",
        font=("Arial", 30),
        borderwidth=1,
        width=15,
        anchor=CENTER,
    )
    label_CO2Text["relief"] = SOLID
    label_CO2Text.pack()
    
    # 2. create a label for co2 reading
    label_CO2Reading = ttk.Label(
        frame_CO2,
        text="2000 ppm",
        font=("Arial", 30),
        borderwidth=1,
        padding=5,
        textvariable=co2_var,
        anchor="e"
    )
    label_CO2Reading["relief"] = SOLID
    label_CO2Reading.pack(pady=5, side=LEFT, fill="x",expand=TRUE)
    
    # 3. create a label for co2 units
    label_CO2Unit = ttk.Label(
    frame_CO2,
    text="ppm",
    font=("Arial", 30),
    borderwidth=1,
    padding=5,
    anchor="w"
    )
    label_CO2Unit["relief"] = SOLID

    label_CO2Unit.pack(pady=5, side=LEFT, fill="x",expand=TRUE)



    # other tasks to be done before gui loop is called---------------------------------------------------------
    root.after(100, update_readings, root, t_var, h_var, co2_var)
    
    # Extra trial space---------------------------------------------------------
    but = ttk.Button(root, text="BUTTON!!")
    but.pack()
    # -------
    
    
    root.mainloop()


def main():
    global exit_signal

    ports = serial.tools.list_ports.comports()

    for port, desc, hwid in ports:
        print(f"{port}: {desc}")
    # return
    data_thread_handle = threading.Thread(target=data_thread, args=("COM9",))
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
