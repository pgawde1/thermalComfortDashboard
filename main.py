import os
import time
from functools import partial
import threading
from threading import Lock, Thread
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import sleep
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from datetime import datetime
import serial.tools.list_ports
from pythermalcomfort.models import pmv_ppd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Sensor import Sensor, SensorError


class UI:

    def __init__(self):
        # create window first

        self.__button_apply_settings = None
        self.__label_clothing = None
        self.__frame_clothing = None
        self.__label_activity = None
        self.__frame_activity = None
        self.__frame_settings = None
        self.__combo_clothing = None
        self.__combo_activity = None
        self.__label_sensation_reading = None
        self.__var_sensation = None
        self.__label_sensation = None
        self.__frame_sensation = None
        self.__var_append_create = None
        self.__stopLoggingEvent = threading.Event()
        self.__radio_create = None
        self.__radio_append = None
        self.__logging_thread_handle = None
        self.__checkbox_difference = None
        self.__var_only_difference = None
        self.__create_button = None
        self.__append_button = None
        self.__file_option = None
        self.__frame_options = None
        self.__entry_fileName = None
        self.__label_fileName = None
        self.__frame_fileName = None
        self.__button_filebrowse = None
        self.__entry_folderName = None
        self.__label_folder = None
        self.__frame_folder_log = None
        self.__button_stop_log = None
        self.__button_start_log = None
        self.__frame_button_log = None
        self.__frame_reading_wrapper = None
        self.__title_label = None
        self.__frame_log = None
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
        self.__dataUpdated_LOG_Event = threading.Event()
        self.__dataUpdated_GUI_Event = threading.Event()
        self.__root = Tk()
        self.__dict_activity={"Sleeping": 0.7,
        "Reclining": 0.8,
        "Seated, quiet": 1.0,
        "Reading, seated": 1.0,
        "Writing": 1.0,
        "Typing": 1.1,
        "Standing, relaxed": 1.2,
        "Filing, seated": 1.2,
        "Flying aircraft, routine": 1.2,
        "Filing, standing": 1.4,
        "Driving a car": 1.5,
        "Walking about": 1.7,
        "Cooking": 1.8,
        "Table sawing": 1.8,
        "Walking 2mph (3.2kmh)": 2.0,
        "Lifting/packing": 2.1,
        "Seated, heavy limb movement": 2.2,
        "Light machine work": 2.2,
        "Flying aircraft, combat": 2.4,
        "Walking 3mph (4.8kmh)": 2.6,
        "House cleaning": 2.7,
        "Driving, heavy vehicle": 3.2,
        "Dancing": 3.4,
        "Calisthenics": 3.5,
        "Walking 4mph (6.4kmh)": 3.8,
        "Tennis": 3.8,
        "Heavy machine work": 4.0,
        "Handling 100lb (45 kg) bags": 4.0
        }
        self.__dict_clothing={"Walking shorts, short-sleeve shirt": 0.36,
        "Typical summer indoor clothing": 0.5,
        "Knee-length skirt, short-sleeve shirt, sandals, underwear": 0.54,
        "Trousers, short-sleeve shirt, socks, shoes, underwear": 0.57,
        "Trousers, long-sleeve shirt": 0.61,
        "Knee-length skirt, long-sleeve shirt, full slip": 0.67,
        "Sweat pants, long-sleeve sweatshirt": 0.74,
        "Jacket, Trousers, long-sleeve shirt": 0.96,
        "Typical winter indoor clothing": 1.0}

    def start(self):
        self.draw_gui()
        self.__root.mainloop()
        print("gui exit")
        self.__exitEvent.set()
        if self.__active_data_thread_handle:
            # only wait for producer thread if it exists.
            # It may be that sensor thread was never started.
            self.__active_data_thread_handle.join()
            self.__active_data_thread_handle = None
            print("sensor thread exit")
        if self.__logging_thread_handle:
            self.__logging_thread_handle.join()
            self.__logging_thread_handle=None
            print("logging thread exit")

        self.__exitEvent.clear()


    def sensor_data_thread(self):

        try:
            scd40 = Sensor(self.__combo_COMPort.get().split(":")[0])
            self.__combo_COMPort["state"] = "disabled"
            self.__button_openPort["state"] = "disabled"
            self.__button_closePort["state"] = "enabled"
            while True:
                if self.__exitEvent.is_set():
                    # this is set when gui loop exits in start function. Event is set. When producer thread wakes up, it exits.
                    # self.__exitEvent.clear()
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
                # self.update_readings()
                self.__dataUpdated_LOG_Event.set()
                self.__dataUpdated_GUI_Event.set()
                sleep(1)
        except SensorError as err:
            print(err)
            messagebox.showerror("Error", f"Failed to open port {self.__combo_COMPort.get().split(":")[0]} !")

    def update_readings(self):

        if self.__dataUpdated_GUI_Event.is_set():
            self.__dataUpdated_GUI_Event.clear()
            print("updateUI...")
            if self.__selected_temperature_unit.get() == "°C":
                self.__t_var.set(str(self.__Temperature))
            else:
                self.__t_var.set(str(round(((self.__Temperature * 9 / 5) + 32), 1)))

            self.__h_var.set(str(self.__Humidity))
            self.__co2_var.set(str(self.__CO2))

            result = pmv_ppd(tdb=self.__Temperature, tr=25, vr=0.1, rh=self.__Humidity, met=1, clo=0.36, standard="ashrae")
            if result['pmv']<=-2.5:
                self.__var_sensation.set("Cold")
            elif -2.5 < result['pmv'] <= -1.5:
                self.__var_sensation.set("Cool")
            elif -1.5 < result['pmv'] <= -0.5:
                self.__var_sensation.set("Slightly Cool")
            elif -0.5 < result['pmv'] <= 0.5:
                self.__var_sensation.set("Neutral")
            elif 0.5 < result['pmv'] <= 1.5:
                self.__var_sensation.set("Slightly Warm")
            elif 1.5 < result['pmv'] <= 2.5:
                self.__var_sensation.set("Warm")
            else:
                self.__var_sensation.set("Hot")

        self.__root.after(100, self.update_readings)

    def get_com_ports(self):
        ports = serial.tools.list_ports.comports()
        l_ports = []
        for port, desc, hwid in ports:
            l_ports.append(f"{port}: {desc}")
        return l_ports

    def open_button_action(self):
        print(self.__combo_COMPort.get())

        if self.__combo_COMPort.get() == "":  # Check if nothing is selected
            messagebox.showwarning("No Selection", "Please select a COM port.")
            return

        try:
            self.__active_data_thread_handle = threading.Thread(target=self.sensor_data_thread)
            self.__active_data_thread_handle.start()

        except Exception as err:
            print(err)

    def close_button_action(self):
        print(f"request to close {self.__combo_COMPort.get()}")
        if self.__active_data_thread_handle:
            # assumes that thread was created and is running
            self.__portCloseEvent.set()

    def temperature_unitChange(self):
        # TODO: add code to modify existing reading
        if self.__selected_temperature_unit.get() == "°C":
            self.__t_var.set(str(self.__Temperature))
        else:
            self.__t_var.set(str(round(((self.__Temperature * 9 / 5) + 32), 1)))
        print(f"{self.__selected_temperature_unit.get()} is set")

    def sensor_log_thread(self):
        self.__button_stop_log["state"]="enabled"
        self.__button_start_log["state"] = "disabled"
        self.__button_filebrowse["state"]= "disabled"

        self.__entry_folderName["state"] = "disabled"
        self.__entry_fileName["state"] = "disabled"

        self.__radio_append["state"] = "disabled"
        self.__radio_create["state"] = "disabled"
        self.__checkbox_difference["state"] = "disabled"

        lastTemperature = None
        lastHumidity = None
        lastCO2 = None

        print(self.__entry_folderName.get())
        print(self.__entry_fileName.get())

        if self.__var_only_difference.get():
            print("checked")
        logfileObj=None
        if self.__var_append_create.get() == "create":
            logfileObj=open(f"{self.__entry_folderName.get()}/{self.__entry_fileName.get()}.csv", "w")
            logfileObj.write("time,t,h,co2\n")
        else:
            # append is selected. this assumes that column headers are already present
            logfileObj = open(f"{self.__entry_folderName.get()}/{self.__entry_fileName.get()}.csv", "a")
        while True:
            if self.__exitEvent.is_set():
                if logfileObj:
                    logfileObj.close()
                    logfileObj=None
                return
            if self.__stopLoggingEvent.is_set():
                self.__stopLoggingEvent.clear()
                self.__button_stop_log["state"] = "disabled"
                self.__button_start_log["state"] = "enabled"
                self.__button_filebrowse["state"] = "enabled"

                self.__entry_folderName["state"] = "enabled"
                self.__entry_fileName["state"] = "enabled"

                self.__radio_append["state"] = "enabled"
                self.__radio_create["state"] = "enabled"
                self.__checkbox_difference["state"] = "enabled"
                if logfileObj:
                    logfileObj.close()
                    logfileObj=None
                return
            if self.__dataUpdated_LOG_Event.is_set():
                self.__dataUpdated_LOG_Event.clear()
                # code comes here only when data is generated
                print(f"LOG :{self.__Temperature},{self.__Humidity},{self.__CO2}")


                if self.__var_only_difference.get():
                    if (self.__Temperature != lastTemperature)or(self.__Humidity != lastHumidity)or(self.__CO2 != lastCO2):
                        logfileObj.write(f"{int(time.time())},{self.__Temperature},{self.__Humidity},{self.__CO2}\n")
                    else:
                        print("reading same as before!!")
                else:
                    logfileObj.write(f"{int(time.time())},{self.__Temperature},{self.__Humidity},{self.__CO2}\n")



                lastTemperature = self.__Temperature
                lastHumidity = self.__Humidity
                lastCO2 = self.__CO2
            time.sleep(0.1)

    def start_logging(self):
        folder_path = self.__entry_folderName.get()
        file_name = self.__entry_fileName.get()

        if not folder_path:
            messagebox.showerror(title="folder error",message="Invalid folder path")
            return

        if not os.path.isdir(folder_path):
            messagebox.showerror(title="folder error",message=f"{folder_path} is invalid")
            return

        if not file_name:
            messagebox.showerror(title="file error",message=f"Invalid file name")
            return

        print(f"Folder - {folder_path}, File - {file_name}")

        self.__logging_thread_handle = threading.Thread(target=self.sensor_log_thread)
        self.__logging_thread_handle.start()




    def stop_logging(self):
        print(f"request to stop logging")
        if self.__logging_thread_handle:
            # assumes that thread was created and is running
            self.__stopLoggingEvent.set()

    def browse_folder(self):
        selected_folder = askdirectory(title="Select a folder")
        if selected_folder:
            self.__entry_folderName.delete(0, END)
            self.__entry_folderName.insert(0, selected_folder)
            print(f"Selected folder: {selected_folder}")

    def apply_changed_settings(self):
        print(self.__combo_activity.get())
        print(self.__combo_clothing.get())
    def draw_gui(self):

        self.__root.title("thermalComfortDashboard 1.0")
        self.__root.minsize(width=1000, height=1000)

        # vars
        self.__t_var = StringVar()
        self.__h_var = StringVar()
        self.__co2_var = StringVar()

        # create a Frame for COM Port -------------------------------------------------------
        self.__frame_ComPort = ttk.Frame(
            self.__root,
            borderwidth=5,
            relief="raised",
            # padding=20,
        )
        self.__frame_ComPort.pack(anchor="nw", padx=10, pady=10)

        self.__label_COMPort = ttk.Label(self.__frame_ComPort, text="COM Port: ")
        # self.__label_COMPort["relief"] = SOLID
        self.__label_COMPort.pack(side=LEFT)

        self.__combo_COMPort = ttk.Combobox(self.__frame_ComPort, state="readonly", values=self.get_com_ports())
        self.__combo_COMPort.pack(side=LEFT, padx=10)

        self.__button_openPort = ttk.Button(self.__frame_ComPort, text="open", command=self.open_button_action)
        self.__button_openPort.pack(side=LEFT, padx=10)

        self.__button_closePort = ttk.Button(self.__frame_ComPort, text="close", state="disabled",
                                             command=self.close_button_action)
        self.__button_closePort.pack(side=LEFT, padx=10)

        #create a wrapper frame
        self.__frame_reading_wrapper = ttk.Frame(
            self.__root,
            # width=50,
            # height=50,
            # borderwidth=5,
            # relief="raised",
            # padding=20,
        )
        self.__frame_reading_wrapper.pack(fill="x")
        # create a Frame for temperature -------------------------------------------------------
        self.__frame_temperature = ttk.Frame(
            self.__frame_reading_wrapper,
            # width=50,
            # height=50,
            borderwidth=5,
            relief="raised",
            padding=20,
        )
        self.__frame_temperature.pack(side=LEFT, anchor="nw", padx=10, pady=10,fill="x",expand=TRUE)

        # 1.create a temperature text Label
        self.__label_temperatureText = ttk.Label(
            self.__frame_temperature,
            text="Temperature",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
        )
        # self.__label_temperatureText["relief"] = SOLID
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
        # self.__label_temperatureReading["relief"] = SOLID
        self.__label_temperatureReading.pack(pady=5, side=LEFT, fill="x", expand=TRUE)

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
        # self.__label_temperatureUnit["relief"] = SOLID
        self.__label_temperatureUnit.pack(pady=5, side=LEFT, fill="x", expand=TRUE)

        # 4. create a frame to hold radio buttons for units
        self.__frame_radio_units = ttk.Frame(
            self.__frame_temperature
        )
        self.__frame_radio_units.pack(anchor="w", side="left")
        # self.__frame_radio_units["relief"] = SOLID

        # 5. create radio buttons and pack
        self.__radio_celsius = ttk.Radiobutton(
            self.__frame_radio_units, text="°C", value="°C", variable=self.__selected_temperature_unit,
            command=self.temperature_unitChange
        )
        self.__radio_Fahrenheit = ttk.Radiobutton(
            self.__frame_radio_units, text="°F", value="°F", variable=self.__selected_temperature_unit,
            command=self.temperature_unitChange
        )

        self.__radio_celsius.pack(fill=X, expand=TRUE)
        self.__radio_Fahrenheit.pack(fill=X, expand=TRUE)

        # ------create a Frame for humidity -------------------------------------------------------

        self.__frame_humidity = ttk.Frame(
            self.__frame_reading_wrapper, borderwidth=5, relief="raised", padding=20
        )
        self.__frame_humidity.pack( side =LEFT, anchor="nw", padx=10, pady=10,expand=TRUE,fill="x")

        # 1. create label for humidity text
        self.__label_humidityText = ttk.Label(
            self.__frame_humidity,
            text="Humidity",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
        )
        # self.__label_humidityText["relief"] = SOLID
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
        # self.__label_humidityReading["relief"] = SOLID
        self.__label_humidityReading.pack(pady=5, side=LEFT, expand=True, fill="x")

        # 3. create label for humidity units
        self.__label_humidityUnits = ttk.Label(
            self.__frame_humidity,
            text="%",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            anchor="w"
        )
        # self.__label_humidityUnits["relief"] = SOLID
        self.__label_humidityUnits.pack(pady=5, side=LEFT, expand=TRUE, fill="x")

        # ------create a Frame for CO2 -------------------------------------------------------
        self.__frame_CO2 = ttk.Frame(
            self.__frame_reading_wrapper, borderwidth=5, relief="raised", padding=20
        )
        self.__frame_CO2.pack(side=LEFT, anchor="nw", padx=10, pady=10,fill="x", expand=TRUE)

        # 1. create label for co2 text
        self.__label_CO2Text = ttk.Label(
            self.__frame_CO2,
            text="CO2",
            font=("Arial", 30),
            borderwidth=1,
            width=15,
            anchor=CENTER,
        )
        # self.__label_CO2Text["relief"] = SOLID
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
        # self.__label_CO2Reading["relief"] = SOLID
        self.__label_CO2Reading.pack(pady=5, side=LEFT, fill="x", expand=TRUE)

        # 3. create a label for co2 units
        self.__label_CO2Unit = ttk.Label(
            self.__frame_CO2,
            text="ppm",
            font=("Arial", 30),
            borderwidth=1,
            padding=5,
            anchor="w"
        )
        # self.__label_CO2Unit["relief"] = SOLID

        self.__label_CO2Unit.pack(pady=5, side=LEFT, fill="x", expand=TRUE)

        # FRAME for LOGGING--------------------------------------------------
        self.__frame_log = ttk.Frame(self.__root,width=50, height=50, borderwidth=5, relief="raised", padding=20)
        self.__frame_log.pack( anchor="nw", padx=10, pady=10,  fill="x")

        # Title Label
        self.__title_label = ttk.Label(self.__frame_log, text="Log", font=("Arial", 14))
        self.__title_label.pack(anchor="w", pady=5)

        # Buttons Frame
        self.__frame_button_log = ttk.Frame(self.__frame_log)
        self.__frame_button_log.pack(fill="x", pady=5)

        self.__button_start_log = ttk.Button(self.__frame_button_log, text="Start", command=self.start_logging, width=10)
        self.__button_start_log.pack(side="left", padx=5)

        self.__button_stop_log = ttk.Button(self.__frame_button_log, state="disabled",text="Stop", command=self.stop_logging, width=10)
        self.__button_stop_log.pack(side="left", padx=5)

        # Folder Path Frame
        self.__frame_folder_log = ttk.Frame(self.__frame_log)
        self.__frame_folder_log.pack(fill="x", pady=5)

        self.__label_folder = ttk.Label(self.__frame_folder_log, text="Folder Path:")
        self.__label_folder.pack(side="left", padx=5)

        self.__entry_folderName = ttk.Entry(self.__frame_folder_log)
        self.__entry_folderName.pack(side="left", fill="x", expand=True, padx=5)

        self.__button_filebrowse = ttk.Button(self.__frame_folder_log, text="Browse", command=self.browse_folder)
        self.__button_filebrowse.pack(side="left", padx=5)

        # File Name Frame
        self.__frame_fileName = ttk.Frame(self.__frame_log)
        self.__frame_fileName.pack(fill="x", pady=5)

        self.__label_fileName = ttk.Label(self.__frame_fileName, text="File Name:")
        self.__label_fileName.pack(side="left", padx=5)

        self.__entry_fileName = ttk.Entry(self.__frame_fileName)
        self.__entry_fileName.pack(side="left", fill="x", expand=True, padx=5)

        # Options Frame
        self.__frame_options = ttk.Frame(self.__frame_log)
        self.__frame_options.pack(fill="x", pady=5)

        self.__var_append_create = StringVar(value="append")

        self.__radio_append = ttk.Radiobutton(self.__frame_log, text="Append if exists", variable=self.__var_append_create, value="append")
        self.__radio_append.pack(side="left", padx=5)

        self.__radio_create = ttk.Radiobutton(self.__frame_log, text="Create new", variable=self.__var_append_create, value="create")
        self.__radio_create.pack(side="left", padx=5)

        # Checkbox and Dropdown Frame
        # misc_frame = ttk.Frame(self.__frame_log)
        # misc_frame.pack(fill="x", pady=5)

        self.__var_only_difference = BooleanVar()
        self.__checkbox_difference = ttk.Checkbutton(self.__frame_log, text="Log Differences", variable=self.__var_only_difference)
        self.__checkbox_difference.pack(side="left", padx=5)

        # ---------------------------------------------------------
        self.__frame_sensation = ttk.Frame(self.__root, borderwidth=5, relief="raised", padding=20)
        self.__frame_sensation.pack( anchor="nw", padx=10, pady=10, fill="x")

        self.__label_sensation = ttk.Label(self.__frame_sensation, text="Sensation", font=("Arial", 14))
        self.__label_sensation.pack(anchor="w", pady=5)

        self.__var_sensation=StringVar()
        self.__var_sensation.set("___")
        self.__label_sensation_reading = ttk.Label(self.__frame_sensation, text="-",textvariable=self.__var_sensation, font=("Arial", 14))
        self.__label_sensation_reading.pack(anchor="w", pady=5)

        self.__frame_settings=ttk.Frame(self.__frame_sensation, borderwidth=5, relief="raised", padding=20)
        self.__frame_settings.pack(anchor="w",expand=True)
        self.__frame_activity=ttk.Frame(self.__frame_settings,  borderwidth=5,  padding=20)
        self.__frame_activity.pack(side=LEFT)
        self.__label_activity = ttk.Label(self.__frame_activity, text="Activity", font=("Arial", 14))
        self.__label_activity.pack()
        self.__combo_activity= ttk.Combobox(self.__frame_activity, width=30,values=[key for key in self.__dict_activity])
        self.__combo_activity.pack()

        self.__frame_clothing = ttk.Frame(self.__frame_settings,  borderwidth=5, padding=20)
        self.__frame_clothing.pack(side=LEFT)
        self.__label_clothing = ttk.Label(self.__frame_clothing, text="Clothing", font=("Arial", 14))
        self.__label_clothing.pack()
        self.__combo_clothing = ttk.Combobox(self.__frame_clothing, width=30, values=[key for key in self.__dict_clothing])
        self.__combo_clothing.pack()

        self.__button_apply_settings = ttk.Button(self.__frame_settings, text="apply", command=self.apply_changed_settings)
        self.__button_apply_settings.pack(side=LEFT, padx=10)

        # other tasks to be done before gui loop is called---------------------------------------------------------
        self.__root.after(100, self.update_readings)

        # Extra trial space---------------------------------------------------------


def main():
    thermalDashboard = UI()
    thermalDashboard.start()
    
main()
