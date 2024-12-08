from functools import partial
import threading
from threading import Lock
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import sleep
import serial.tools.list_ports

from Sensor import Sensor, SensorError



class UI:

    def __init__(self):
        # create window first

        self.__active_data_thread_handle = None
        self.__CO2 = None
        self.__Humidity = None
        self.__Temperature = None
        self.__button_closePort = None
        self.__button_openPort = None
        self.__combo_COMPort = None
        self.__label_COMPort = None
        self.__frame_ComPort = None
        self.__label_CO2Unit = None
        self.__label_CO2Reading = None
        self.__label_CO2Text = None
        self.__frame_CO2 = None
        self.__label_humidityUnits = None
        self.__label_humidityReading = None
        self.__label_humidityText = None
        self.__frame_humidity = None
        self.__radio_celsius = None
        self.__radio_Fahrenheit = None
        self.__selected_temperature_unit = None
        self.__label_temperatureUnit = None
        self.__label_temperatureReading = None
        self.__frame_radio_units = None
        self.__label_temperatureText = None
        self.__frame_temperature = None
        self.__co2_var = None
        self.__h_var = None
        self.__t_var = None
        self.__exitEvent = threading.Event()
        self.__portCloseEvent = threading.Event()
        self.__root = Tk()

    def start(self):
        self.draw_gui()
        self.__root.mainloop()
        print("gui exit")
        self.__exitEvent.set()
        if self.__active_data_thread_handle:
            # only wait for producer thread if it exists.
            # It may be that sensor thread was never started.
            self.__active_data_thread_handle.join()
            self.__active_data_thread_handle=None
            print("sensor thread exit")

    def sensor_data_thread(self):

        try:
            scd40 = Sensor(self.__combo_COMPort.get().split(":")[0])
            self.__combo_COMPort["state"] = "disabled"
            self.__button_openPort["state"] = "disabled"
            self.__button_closePort["state"] = "enabled"
            while True:
                if self.__exitEvent.is_set():
                    # this is set when gui loop exits in start function. Event is set. When producer thread wakes up, it exits.
                    self.__exitEvent.clear()
                    print("exiting producer")
                    return
                
                if self.__portCloseEvent.is_set():
                    self.__portCloseEvent.clear()
                    self.__combo_COMPort["state"] = "readonly"
                    self.__button_openPort["state"] = "enabled"
                    self.__button_closePort["state"] = "disabled"
                    return

                scd40.getData()
                # g_mutex_readings.acquire()
                # print("data-mutex[acq]")
                # print(f"T:{scd40.getTemperature()},H:{scd40.getHumidity()},CO2:{scd40.getCO2()}")
                self.__Temperature = scd40.getTemperature()
                self.__Humidity = scd40.getHumidity()
                self.__CO2 = scd40.getCO2()
                # g_mutex_readings.release()
                # print("data-mutex[rel]")
                print(f"T:{self.__Temperature},H:{self.__Humidity},CO2:{self.__CO2}")
                self.update_readings()
                sleep(10)
        except SensorError as err:
            print(err)
            messagebox.showerror("Error", f"Failed to open port {self.__combo_COMPort.get().split(":")[0]} !")

    def update_readings(self):

        # while True:
        # g_mutex_readings.acquire()
        print("ui-mutex[acq]")
        if self.__selected_temperature_unit.get() == "°C":
            self.__t_var.set(str(self.__Temperature))
        else:
            self.__t_var.set(str(round(((self.__Temperature*9/5)+32),1)))

        self.__h_var.set(str(self.__Humidity))
        self.__co2_var.set(str(self.__CO2))
        # g_mutex_readings.release()
        print("ui-mutex[rel]")
        # self.__root.after(100, self.update_readings)

    def temperature_unitChange(self):
        # TODO: add code to modify existing reading
        if self.__selected_temperature_unit.get() == "°C":
            self.__t_var.set(str(self.__Temperature))
        else:
            self.__t_var.set(str(round(((self.__Temperature * 9 / 5) + 32), 1)))
        print(f"{self.__selected_temperature_unit.get()} is set")

    def draw_gui(self):

        self.__root.title("thermalComfortDashboard 1.0")
        self.__root.minsize(width=1000, height=1000)

        # vars
        self.__t_var = StringVar()
        self.__h_var = StringVar()
        self.__co2_var = StringVar()

        # create a Frame for temperature -------------------------------------------------------
        self.__frame_temperature = ttk.Frame(
            self.__root,
            width=50,
            height=50,
            borderwidth=5,
            relief="raised",
            padding=20,
        )
        self.__frame_temperature.pack(side=LEFT, anchor="nw", padx=10, pady=10)

        # 1.create a temperature text Label
        self.__label_temperatureText = ttk.Label(
            self.__frame_temperature,
            text="Temperature",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
        )
        self.__label_temperatureText["relief"] = SOLID
        self.__label_temperatureText.pack()

        # 2. create a temperature reading Label
        self.__label_temperatureReading = ttk.Label(
            self.__frame_temperature,
            text="20.3",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            textvariable=self.__t_var,
            anchor="e"

        )
        self.__label_temperatureReading["relief"] = SOLID
        self.__label_temperatureReading.pack(pady=5, side=LEFT,fill="x",expand=TRUE)

        # 3. create a label for temperature units text

        # variable to hold state of selected radio button and label for units
        self.__selected_temperature_unit = StringVar()
        self.__selected_temperature_unit.set("°C")

        self.__label_temperatureUnit = ttk.Label(
            self.__frame_temperature,
            text="",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            textvariable=self.__selected_temperature_unit,
            anchor="w"
        )
        self.__label_temperatureUnit["relief"] = SOLID
        self.__label_temperatureUnit.pack(pady=5, side=LEFT,fill="x",expand=TRUE)


        # 4. create a frame to hold radio buttons for units
        self.__frame_radio_units = ttk.Frame(
            self.__frame_temperature
        )
        self.__frame_radio_units.pack(anchor="w",side="left")
        self.__frame_radio_units["relief"]=SOLID


        # 5. create radio buttons and pack
        self.__radio_celsius = ttk.Radiobutton(
            self.__frame_radio_units, text="°C", value="°C", variable=self.__selected_temperature_unit, command=self.temperature_unitChange
        )
        self.__radio_Fahrenheit = ttk.Radiobutton(
            self.__frame_radio_units, text="°F", value="°F", variable=self.__selected_temperature_unit, command=self.temperature_unitChange
        )

        self.__radio_celsius.pack(fill=X,expand=TRUE)
        self.__radio_Fahrenheit.pack(fill=X,expand=TRUE)

        # ------create a Frame for humidity -------------------------------------------------------

        self.__frame_humidity = ttk.Frame(
            self.__root, width=50, height=50, borderwidth=5, relief="raised", padding=20
        )
        self.__frame_humidity.pack(side=LEFT, anchor="nw", padx=10, pady=10)

        # 1. create label for humidity text
        self.__label_humidityText = ttk.Label(
            self.__frame_humidity,
            text="Humidity",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
        )
        self.__label_humidityText["relief"] = SOLID
        self.__label_humidityText.pack()

        # 2. create label for humidity reading
        self.__label_humidityReading = ttk.Label(
            self.__frame_humidity,
            text="100 %",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            textvariable=self.__h_var,
            anchor="e"
        )
        self.__label_humidityReading["relief"] = SOLID
        self.__label_humidityReading.pack(pady=5,side=LEFT,expand=True,fill="x")

        # 3. create label for humidity units
        self.__label_humidityUnits = ttk.Label(
        self.__frame_humidity,
        text="%",
        font=("Arial", 30),
        borderwidth=1,
        padding=5,
        anchor="w"
        )
        self.__label_humidityUnits["relief"] = SOLID
        self.__label_humidityUnits.pack(pady=5,side=LEFT,expand=TRUE,fill="x")


        # ------create a Frame for CO2 -------------------------------------------------------
        self.__frame_CO2 = ttk.Frame(
            self.__root, width=50, height=50, borderwidth=5, relief="raised", padding=20
        )
        self.__frame_CO2.pack(side=LEFT, anchor="nw", padx=10, pady=10)

        # 1. create label for co2 text
        self.__label_CO2Text = ttk.Label(
            self.__frame_CO2,
            text="CO2",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
        )
        self.__label_CO2Text["relief"] = SOLID
        self.__label_CO2Text.pack()

        # 2. create a label for co2 reading
        self.__label_CO2Reading = ttk.Label(
            self.__frame_CO2,
            text="2000 ppm",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            textvariable=self.__co2_var,
            anchor="e"
        )
        self.__label_CO2Reading["relief"] = SOLID
        self.__label_CO2Reading.pack(pady=5, side=LEFT, fill="x",expand=TRUE)

        # 3. create a label for co2 units
        self.__label_CO2Unit = ttk.Label(
        self.__frame_CO2,
        text="ppm",
        font=("Arial", 30),
        borderwidth=1,
        padding=5,
        anchor="w"
        )
        self.__label_CO2Unit["relief"] = SOLID

        self.__label_CO2Unit.pack(pady=5, side=LEFT, fill="x",expand=TRUE)

        # other tasks to be done before gui loop is called---------------------------------------------------------
        # self.__root.after(100, self.update_readings)

        # Extra trial space---------------------------------------------------------



def main():

    thermalDashboard = UI()
    thermalDashboard.start()

    # gui_thread_handle = threading.Thread(target=draw_gui)
    # gui_thread_handle.start()

    # uiUpdate_thread_handle = threading.Thread(target=update_readings)
    # uiUpdate_thread_handle.start()

    # gui_thread_handle.join()
    # print("return GUI thread!!!!!")
    # exit_signal = True
    # data_thread_handle.join()
    # print("return data thread!!!!!")


main()
